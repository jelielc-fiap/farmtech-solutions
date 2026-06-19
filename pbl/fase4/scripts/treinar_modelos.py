from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from criar_banco import DB_PATH
from ingerir_dados import ingerir_dados
from recomendacoes import recomendar_manejo


BASE_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = BASE_DIR / "models"
METRICS_FILE = MODELS_DIR / "metricas_modelos.json"
TARGETS = {
    "rendimento_estimado_t_ha": "Rendimento estimado (t/ha)",
    "volume_irrigacao_l": "Volume de irrigacao (L/ha)",
    "necessidade_fertilizacao_kg_ha": "Necessidade de fertilizacao (kg/ha)",
    "umidade_futura": "Umidade futura (%)",
    "ph_futuro": "pH futuro",
}

FEATURES_NUM = [
    "umidade",
    "ph",
    "n_ok",
    "p_ok",
    "k_ok",
    "chuva_probabilidade",
    "bomba_ligada",
]
FEATURES_CAT = ["cultura"]
FEATURES = FEATURES_NUM + FEATURES_CAT


def carregar_leituras(db_path: Path = DB_PATH) -> pd.DataFrame:
    ingerir_dados(db_path=db_path)
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query("SELECT * FROM leituras_sensores ORDER BY data_leitura", conn)


def criar_pipeline(modelo) -> Pipeline:
    preprocessador = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), FEATURES_NUM),
            ("cat", OneHotEncoder(handle_unknown="ignore"), FEATURES_CAT),
        ]
    )
    return Pipeline([("preprocessador", preprocessador), ("modelo", modelo)])


def avaliar(y_true, y_pred) -> dict[str, float]:
    mse = mean_squared_error(y_true, y_pred)
    return {
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "MSE": float(mse),
        "RMSE": float(np.sqrt(mse)),
        "R2": float(r2_score(y_true, y_pred)),
    }


def treinar_modelos(db_path: Path = DB_PATH) -> dict:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    df = carregar_leituras(db_path)
    modelos = {
        "Regressao Linear": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=160, random_state=42, min_samples_leaf=3),
        "Gradient Boosting": GradientBoostingRegressor(random_state=42),
    }
    metricas: dict[str, dict] = {}
    melhores: dict[str, str] = {}
    previsoes_dashboard = []

    X = df[FEATURES]
    for alvo, nome_alvo in TARGETS.items():
        y = df[alvo]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42
        )
        metricas[alvo] = {}
        melhor_nome = ""
        melhor_score = -999999.0
        melhor_pipeline = None

        for nome_modelo, estimador in modelos.items():
            pipeline = criar_pipeline(estimador)
            pipeline.fit(X_train, y_train)
            pred = pipeline.predict(X_test)
            resultado = avaliar(y_test, pred)
            metricas[alvo][nome_modelo] = resultado
            score = resultado["R2"] - resultado["RMSE"] * 0.01
            if score > melhor_score:
                melhor_score = score
                melhor_nome = nome_modelo
                melhor_pipeline = pipeline

        assert melhor_pipeline is not None
        joblib.dump(melhor_pipeline, MODELS_DIR / f"{alvo}.joblib")
        melhores[alvo] = melhor_nome
        pred_todos = melhor_pipeline.predict(X)
        for leitura_id, valor in zip(df["id"], pred_todos):
            previsoes_dashboard.append((int(leitura_id), melhor_nome, nome_alvo, float(valor)))

    payload = {
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "features": FEATURES,
        "targets": TARGETS,
        "melhores_modelos": melhores,
        "metricas": metricas,
    }
    METRICS_FILE.write_text(json.dumps(payload, indent=4, ensure_ascii=False), encoding="utf-8")
    salvar_previsoes_recomendacoes(db_path, df, previsoes_dashboard, melhores)
    return payload


def salvar_previsoes_recomendacoes(db_path: Path, df: pd.DataFrame, previsoes: list[tuple], melhores: dict) -> None:
    criado_em = datetime.now().isoformat(timespec="seconds")
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM previsoes_modelo")
        conn.execute("DELETE FROM recomendacoes_manejo")
        conn.executemany(
            """
            INSERT INTO previsoes_modelo (leitura_id, modelo, alvo, valor_previsto, criado_em)
            VALUES (?, ?, ?, ?, ?)
            """,
            [(leitura_id, modelo, alvo, valor, criado_em) for leitura_id, modelo, alvo, valor in previsoes],
        )
        recomendacoes = []
        for linha in df.itertuples(index=False):
            rec = recomendar_manejo(
                umidade=linha.umidade,
                ph=linha.ph,
                n_ok=linha.n_ok,
                p_ok=linha.p_ok,
                k_ok=linha.k_ok,
                chuva_probabilidade=linha.chuva_probabilidade,
                rendimento_estimado=linha.rendimento_estimado_t_ha,
                volume_irrigacao=linha.volume_irrigacao_l,
            )
            recomendacoes.append(
                (
                    int(linha.id),
                    rec.acao_irrigacao,
                    rec.acao_ph,
                    rec.acao_nutrientes,
                    rec.risco_produtivo,
                    rec.justificativa,
                    criado_em,
                )
            )
        conn.executemany(
            """
            INSERT INTO recomendacoes_manejo
            (leitura_id, acao_irrigacao, acao_ph, acao_nutrientes, risco_produtivo, justificativa, criado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            recomendacoes,
        )


def prever_cenario(cenario: dict, alvo: str = "rendimento_estimado_t_ha") -> float:
    modelo_path = MODELS_DIR / f"{alvo}.joblib"
    if not modelo_path.exists():
        treinar_modelos()
    pipeline = joblib.load(modelo_path)
    entrada = pd.DataFrame([cenario])[FEATURES]
    return float(pipeline.predict(entrada)[0])


if __name__ == "__main__":
    resultado = treinar_modelos()
    print(f"Modelos treinados em: {MODELS_DIR}")
    for alvo, modelo in resultado["melhores_modelos"].items():
        print(f"{alvo}: {modelo}")
