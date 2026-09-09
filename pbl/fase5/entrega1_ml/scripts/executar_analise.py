from __future__ import annotations

import json
import os
from pathlib import Path

import joblib
import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.base import clone
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, IsolationForest, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, silhouette_score
from sklearn.model_selection import GroupKFold, GroupShuffleSplit, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from dataset import ALVO, CATEGORICAS, COLUNAS_ORIGINAIS, DATA_PATH, NUMERICAS, carregar_dados

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "outputs"
MODELS_DIR = BASE_DIR / "models"
SEED = 572665
UNIDADE = "unidade original de Yield"


def criar_preprocessador() -> ColumnTransformer:
    """Cada pipeline ajusta suas escalas e categorias somente no respectivo treino."""
    return ColumnTransformer([
        ("num", StandardScaler(), NUMERICAS),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAS),
    ])


def executar_clusterizacao(df: pd.DataFrame) -> pd.DataFrame:
    # O alvo não participa da formação dos grupos; rendimento é analisado depois.
    matriz = criar_preprocessador().fit_transform(df[NUMERICAS + CATEGORICAS])
    scores = {}
    for k in range(2, min(7, len(df))):
        labels = KMeans(n_clusters=k, random_state=SEED, n_init=20).fit_predict(matriz)
        if 1 < len(np.unique(labels)) < len(df):
            scores[k] = silhouette_score(matriz, labels, sample_size=min(5000, len(df)), random_state=SEED)
    if not scores:
        raise ValueError("Não há variabilidade suficiente para comparar clusters.")
    melhor_k = max(scores, key=scores.get)
    clusters = KMeans(n_clusters=melhor_k, random_state=SEED, n_init=20).fit_predict(matriz)
    detector = IsolationForest(contamination=0.05, random_state=SEED)
    flags = detector.fit_predict(matriz)
    pca = PCA(n_components=2, random_state=SEED)
    componentes = pca.fit_transform(matriz)
    resultado = df.copy()
    resultado["cluster"] = clusters
    resultado["outlier"] = flags == -1
    resultado["score_anomalia"] = detector.decision_function(matriz)
    resultado["pca_1"], resultado["pca_2"] = componentes[:, 0], componentes[:, 1]
    resultado.attrs.update(silhouette_scores=scores, melhor_k=melhor_k,
                           pca_variancia_explicada=float(pca.explained_variance_ratio_.sum()))
    return resultado


def avaliar(y_real, y_previsto) -> dict[str, float | None]:
    mse = float(mean_squared_error(y_real, y_previsto))
    # R² não é informativo para um único valor ou para um alvo constante.
    r2 = float(r2_score(y_real, y_previsto)) if len(y_real) >= 2 and np.var(y_real) > 0 else None
    return {"MAE": float(mean_absolute_error(y_real, y_previsto)), "MSE": mse,
            "RMSE": float(np.sqrt(mse)), "R2": r2}


def separar_dados(df: pd.DataFrame):
    # A base oficial repete os mesmos cenários climáticos entre culturas.
    # O agrupamento impede compartilhar um cenário entre treino e teste.
    grupos = pd.Series(pd.factorize(pd.MultiIndex.from_frame(df[NUMERICAS]))[0], index=df.index)
    if grupos.nunique() < 4:
        raise ValueError("São necessários ao menos quatro cenários climáticos distintos.")
    treino_idx, teste_idx = next(GroupShuffleSplit(n_splits=1, test_size=0.22, random_state=SEED).split(df, groups=grupos))
    return treino_idx, teste_idx, grupos


def treinar_modelos(df: pd.DataFrame) -> tuple[pd.DataFrame, Pipeline, pd.DataFrame]:
    X, y = df[NUMERICAS + CATEGORICAS], df[ALVO]
    treino_idx, teste_idx, grupos = separar_dados(df)
    X_train, X_test = X.iloc[treino_idx], X.iloc[teste_idx]
    y_train, y_test = y.iloc[treino_idx], y.iloc[teste_idx]
    grupos_treino = grupos.iloc[treino_idx]
    cv = GroupKFold(n_splits=min(5, grupos_treino.nunique()))
    modelos = {
        "Regressão Linear": LinearRegression(),
        "Ridge": Ridge(alpha=1.0),
        "Random Forest": RandomForestRegressor(n_estimators=350, random_state=SEED, min_samples_leaf=2),
        "Gradient Boosting": GradientBoostingRegressor(random_state=SEED),
        "Extra Trees": ExtraTreesRegressor(n_estimators=350, random_state=SEED, min_samples_leaf=2),
    }

    # Primeiro escolhe usando exclusivamente os folds de treinamento.
    registros, pipelines = [], {}
    for nome, estimador in modelos.items():
        pipeline = Pipeline([("preprocessamento", criar_preprocessador()), ("modelo", estimador)])
        rmse_folds = -cross_val_score(pipeline, X_train, y_train, groups=grupos_treino,
                                     cv=cv, scoring="neg_root_mean_squared_error", n_jobs=1)
        registros.append({"modelo": nome, "CV_RMSE_medio": float(rmse_folds.mean()),
                          "CV_RMSE_desvio": float(rmse_folds.std()),
                          **{f"CV_fold_{i + 1}": float(v) for i, v in enumerate(rmse_folds)}})
        pipelines[nome] = pipeline
    melhor_nome = min(registros, key=lambda r: r["CV_RMSE_medio"])["modelo"]

    # O teste só é consultado depois da seleção; comparar os demais não muda o vencedor.
    previsoes, metricas_cultura = [], []
    for registro in registros:
        nome = registro["modelo"]
        pipeline = pipelines[nome]
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        registro.update(avaliar(y_test, y_pred))
        registro["selecionado_por_cv"] = nome == melhor_nome
        previsao = X_test.copy()
        previsao["indice_original"] = teste_idx
        previsao["grupo_climatico"] = grupos.iloc[teste_idx].to_numpy()
        previsao["modelo"] = nome
        previsao["rendimento_real"] = y_test.to_numpy()
        previsao["rendimento_previsto"] = y_pred
        previsao["erro_absoluto"] = np.abs(y_test.to_numpy() - y_pred)
        previsoes.append(previsao)
        for cultura, dados in previsao.groupby("cultura"):
            metricas_cultura.append({"modelo": nome, "cultura": cultura, "registros_teste": len(dados),
                                    **avaliar(dados["rendimento_real"], dados["rendimento_previsto"])})

    # Referência simples: média por cultura calculada somente no treino.
    medias = df.iloc[treino_idx].groupby("cultura")[ALVO].mean()
    baseline = X_test["cultura"].map(medias).fillna(y_train.mean()).to_numpy()
    baseline_metricas = avaliar(y_test, baseline)
    pd.DataFrame([{"modelo": "Média por cultura (treino)", **baseline_metricas}]).to_csv(
        OUTPUT_DIR / "metricas_baseline.csv", index=False)
    for cultura in sorted(X_test["cultura"].unique()):
        mask = (X_test["cultura"] == cultura).to_numpy()
        metricas_cultura.append({"modelo": "Média por cultura (treino)", "cultura": cultura,
                                "registros_teste": int(mask.sum()), **avaliar(y_test.to_numpy()[mask], baseline[mask])})
    pd.DataFrame(metricas_cultura).to_csv(OUTPUT_DIR / "metricas_por_cultura.csv", index=False)
    pd.DataFrame({"indice_original": df.index, "grupo_climatico": grupos,
                  "particao": np.where(df.index.isin(teste_idx), "teste", "treino")}).to_csv(
                      OUTPUT_DIR / "divisao_treino_teste.csv", index=False)
    metricas = pd.DataFrame(registros).sort_values("CV_RMSE_medio").reset_index(drop=True)
    metricas.attrs["avaliacao"] = {
        "criterio_selecao": "Menor RMSE médio na validação cruzada agrupada, somente no treino",
        "folds": cv.n_splits, "linhas_treino": len(treino_idx), "linhas_teste": len(teste_idx),
        "grupos_treino": int(grupos_treino.nunique()), "grupos_teste": int(grupos.iloc[teste_idx].nunique()),
        "grupos_em_comum": len(set(grupos_treino) & set(grupos.iloc[teste_idx])),
        "baseline_teste": baseline_metricas,
        "culturas_ausentes_no_treino": sorted(set(X_test["cultura"]) - set(X_train["cultura"])),
    }
    return metricas, pipelines[melhor_nome], pd.concat(previsoes, ignore_index=True)


def calcular_importancias(pipeline: Pipeline) -> pd.DataFrame:
    modelo = pipeline.named_steps["modelo"]
    nomes = pipeline.named_steps["preprocessamento"].get_feature_names_out()
    valores = modelo.feature_importances_ if hasattr(modelo, "feature_importances_") else np.abs(np.ravel(modelo.coef_))
    return pd.DataFrame({"variavel": nomes, "importancia": valores}).sort_values("importancia", ascending=False).reset_index(drop=True)


def salvar_graficos(df, cluster_df, metricas_df, pipeline):
    sns.set_theme(style="whitegrid", palette="viridis")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=df, x="cultura", y=ALVO, ax=ax)
    ax.set(title="Distribuição do rendimento por cultura", xlabel="Cultura", ylabel=UNIDADE)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "distribuicao_rendimento_por_cultura.png", dpi=170)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(df[NUMERICAS + [ALVO]].corr(), annot=True, cmap="Greens", fmt=".2f", ax=ax)
    ax.set_title("Associações globais: clima e rendimento (não implicam causalidade)")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "correlacao_variaveis.png", dpi=170)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.scatterplot(data=cluster_df, x="pca_1", y="pca_2", hue="cluster", style="outlier", s=65, ax=ax)
    ax.set(title="Cenários agrícolas: clusters e candidatos a outlier", xlabel="PCA 1", ylabel="PCA 2")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "cluster_pca_outliers.png", dpi=170)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    sns.barplot(data=metricas_df, y="modelo", x="R2", ax=axes[0], color="#2f855a")
    sns.barplot(data=metricas_df, y="modelo", x="RMSE", ax=axes[1], color="#b7791f")
    axes[0].set(title="R² no teste (após seleção por CV)", ylabel="")
    axes[1].set(title="RMSE no teste", xlabel=UNIDADE, ylabel="")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "comparacao_modelos_r2_rmse.png", dpi=170)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=metricas_df, y="modelo", x="CV_RMSE_medio", color="#2f855a", ax=ax)
    ax.set(title="Seleção: RMSE médio da validação cruzada no treino", xlabel=UNIDADE, ylabel="")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "comparacao_validacao_cruzada.png", dpi=170)
    plt.close(fig)

    importancias = calcular_importancias(pipeline)
    importancias.to_csv(OUTPUT_DIR / "importancia_variaveis.csv", index=False)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=importancias.head(10), y="variavel", x="importancia", color="#2f855a", ax=ax)
    ax.set(title="Importância interna / magnitude dos coeficientes do modelo", ylabel="")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "importancia_variaveis.png", dpi=170)
    plt.close(fig)


def salvar_resumos(df, cluster_df, metricas_df, pipeline) -> dict:
    cluster_stats = cluster_df.groupby("cluster").agg(
        registros=("cluster", "size"), rendimento_medio=(ALVO, "mean"),
        precipitacao_media=(NUMERICAS[0], "mean"), temperatura_media=(NUMERICAS[3], "mean")).reset_index()
    cultura_stats = df.groupby("cultura").agg(
        registros=("cultura", "size"), rendimento_medio=(ALVO, "mean"),
        rendimento_minimo=(ALVO, "min"), rendimento_maximo=(ALVO, "max"),
        temperatura_media=(NUMERICAS[3], "mean"), precipitacao_media=(NUMERICAS[0], "mean")).reset_index()
    composicao = pd.crosstab(cluster_df["cluster"], cluster_df["cultura"])
    tendencias = cluster_df.groupby(["cluster", "cultura"]).agg(
        registros=("cluster", "size"), rendimento_medio=(ALVO, "mean"),
        precipitacao_media=(NUMERICAS[0], "mean"), temperatura_media=(NUMERICAS[3], "mean")).reset_index()
    for nome, tabela in {
        "metricas_modelos": metricas_df, "clusterizacao_outliers": cluster_df,
        "resumo_por_cultura": cultura_stats, "resumo_clusters": cluster_stats,
        "composicao_clusters": composicao.reset_index(), "tendencias_por_cultura_cluster": tendencias,
        "exemplos_outliers": cluster_df[cluster_df.outlier].sort_values("score_anomalia").head(10),
    }.items():
        tabela.to_csv(OUTPUT_DIR / f"{nome}.csv", index=False, encoding="utf-8")
    joblib.dump(pipeline, MODELS_DIR / "melhor_modelo_rendimento.joblib")
    melhor = metricas_df.iloc[0]
    resumo = {
        "linhas_analisadas": len(df), "culturas": sorted(df["cultura"].unique()),
        "origem_dataset": df.attrs["origem"], "qualidade_dados": df.attrs["qualidade"],
        "unidade_resultados": UNIDADE,
        "nota_unidades": "O enunciado declara t/ha, mas Yield chega a valores muito elevados e precipitação está na casa dos milhares. Mantidos os valores originais, sem conversão arbitrária; escala e periodicidade precisam de confirmação na fonte.",
        "melhor_modelo": melhor["modelo"],
        "metricas_melhor_modelo": {k: float(melhor[k]) for k in ["MAE", "MSE", "RMSE", "R2", "CV_RMSE_medio"]},
        "avaliacao": metricas_df.attrs["avaliacao"], "quantidade_modelos": len(metricas_df),
        "melhor_k_clusters": cluster_df.attrs["melhor_k"],
        "silhouette_scores": {str(k): float(v) for k, v in cluster_df.attrs["silhouette_scores"].items()},
        "pca_variancia_explicada": cluster_df.attrs["pca_variancia_explicada"],
        "outliers_detectados": int(cluster_df["outlier"].sum()),
        "achados": [
            f"O modelo {melhor['modelo']} foi escolhido pela validação cruzada do treino, antes de consultar o teste.",
            "Os grupos foram formados sem usar Yield; as tabelas detalham composição e rendimento por cultura.",
            "Outliers são candidatos a investigação, com contamination fixada em 5%; não foram removidos do treinamento.",
            "O R² global deve ser confrontado com a média por cultura e com erros separados por cultura.",
        ],
    }
    (OUTPUT_DIR / "resumo_analise.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    return resumo


def executar_pipeline(permitir_sintetico: bool = False) -> dict:
    df = carregar_dados(permitir_sintetico=permitir_sintetico)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    clusters = executar_clusterizacao(df)
    metricas, modelo, previsoes = treinar_modelos(df)
    previsoes.to_csv(OUTPUT_DIR / "previsoes_teste.csv", index=False)
    salvar_graficos(df, clusters, metricas, modelo)
    return salvar_resumos(df, clusters, metricas, modelo)


if __name__ == "__main__":
    print(json.dumps(executar_pipeline(), ensure_ascii=False, indent=2))
