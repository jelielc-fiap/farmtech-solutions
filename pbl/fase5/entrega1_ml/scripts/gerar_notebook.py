"""Gera e executa o notebook oficial com relatório e resultados reproduzíveis."""
from pathlib import Path
import json
import textwrap
import nbformat
from nbclient import NotebookClient

BASE_DIR = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = BASE_DIR / "notebooks" / "JelielCardoso_RM572665_pbl_fase4.ipynb"

def md(s):
    return nbformat.v4.new_markdown_cell(textwrap.dedent(s).strip())

def code(s):
    return nbformat.v4.new_code_cell(textwrap.dedent(s).strip())

def criar_notebook():
    nb = nbformat.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    nb.cells = [
        md("""
        # FarmTech Solutions — Fase 5
        ## Entrega 1 — Rendimento agrícola
        **Aluno:** Jeliel Cardoso · **RM:** 572665

        O sufixo pbl_fase4.ipynb foi mantido conforme a exigência literal do enunciado da Fase 5.
        Este relatório explora o arquivo oficial, identifica grupos e outliers e compara cinco regressões.
        Para reproduzir: abrir o projeto completo, selecionar o kernel das dependências da Fase 5 e
        executar as células em ordem, ou usar run_entrega1_ml.bat. Os scripts auxiliares estão incluídos.
        """),
        md("""
        ## 1. Origem e qualidade
        O CSV original do portal é preservado sem alterar valores. O arquivo origem_dataset.json registra
        a procedência informada pelo aluno e o SHA-256. A leitura mapeia os cabeçalhos originais em inglês.

        **Unidades:** o enunciado informa t/ha e mm/dia, mas Yield chega a 203399 e precipitação está na casa
        dos milhares. Sem dicionário adicional, não aplicamos conversão arbitrária. Métricas e previsões
        são apresentadas na **unidade original de Yield**. O nome interno rendimento_t_ha é legado do
        projeto e não confirma a escala física. A periodicidade e as unidades devem ser confirmadas na fonte.

        Linhas inválidas e duplicatas completas são contabilizadas e removidas antes da divisão.
        """),
        code("""
        # Localiza o projeto a partir da raiz, da Fase 5 ou da pasta do notebook.
        from pathlib import Path
        import sys, inspect, json, joblib
        import pandas as pd
        from IPython.display import Image, display
        BASE_DIR = None
        for raiz in [Path.cwd(), *Path.cwd().parents]:
            for candidata in [raiz, raiz / "entrega1_ml", raiz / "pbl/fase5/entrega1_ml"]:
                if (candidata / "scripts/dataset.py").exists():
                    BASE_DIR = candidata
                    break
            if BASE_DIR is not None:
                break
        if BASE_DIR is None:
            raise FileNotFoundError("Abra o notebook dentro do projeto completo.")
        sys.path.insert(0, str(BASE_DIR / "scripts"))
        from dataset import carregar_dados, ler_csv, NUMERICAS, ALVO
        from executar_analise import executar_pipeline, criar_preprocessador, treinar_modelos
        OUTPUT_DIR, MODELS_DIR = BASE_DIR / "outputs", BASE_DIR / "models"
        df_raw, _, qualidade = ler_csv()
        df = carregar_dados()
        print("Origem:", df.attrs["origem"])
        print("Qualidade:", qualidade)
        display(df_raw.head())
        """),
        md("""
        ## 2. Análise exploratória
        Cultura é categórica. Clima é entrada numérica e Yield é o alvo. Comparar rendimentos absolutos
        de culturas diferentes não equivale a comparar eficiência agrícola.
        """),
        code("""
        # Tipos, ausentes, estatísticas e distribuição por cultura.
        print("Dimensão:", df_raw.shape)
        display(pd.DataFrame({"tipo": df_raw.dtypes.astype(str), "ausentes": df_raw.isna().sum()}))
        display(df_raw.describe(include="all").T)
        display(df.groupby("cultura")[ALVO].agg(["count", "mean", "min", "max"]).round(3))
        print("Cenários climáticos distintos:", len(df[NUMERICAS].drop_duplicates()))
        """),
        md("""
        ## 3. Preparação e avaliação supervisionada
        Os 39 cenários climáticos são repetidos nas quatro culturas. GroupShuffleSplit mantém cada
        cenário inteiro no treino ou no teste. São 120 registros de treino e 36 de teste, sem cenário
        compartilhado. No treino, GroupKFold com cinco folds seleciona o algoritmo pelo menor RMSE médio.

        StandardScaler e OneHotEncoder ficam dentro de cada Pipeline, ajustados apenas no respectivo
        treino. O teste é consultado depois da seleção. Os parâmetros dos algoritmos são fixos.
        A referência adicional prevê a média de cada cultura calculada somente no treino.
        """),
        code("""
        # Implementação reutilizável, comentada e visível no notebook.
        print(inspect.getsource(criar_preprocessador))
        print(inspect.getsource(treinar_modelos))
        """),
        code("""
        # Executa análise, treinamento, gráficos e persistência com o CSV oficial.
        resumo = executar_pipeline()
        print("Modelo selecionado:", resumo["melhor_modelo"])
        print("Avaliação:", resumo["avaliacao"])
        """),
        code("""
        # Gráficos da exploração gerados nesta execução.
        display(Image(filename=str(OUTPUT_DIR / "distribuicao_rendimento_por_cultura.png")))
        display(Image(filename=str(OUTPUT_DIR / "correlacao_variaveis.png")))
        """),
        md("""
        **Achados exploratórios:** 156 registros, 39 por cultura (cacau, palma, arroz e borracha natural),
        sem ausentes nem duplicatas completas. Palma tem uma escala de rendimento muito superior.
        Por isso, até a média por cultura pode apresentar R² global alto. As correlações são associações
        descritivas e não comprovam causalidade; a base não identifica datas nem talhões.
        """),
        md("""
        ## 4. Clusterização, tendências e outliers
        KMeans compara k de 2 a 6 pelo silhouette. Usa clima padronizado e cultura codificada,
        **sem usar Yield**. O rendimento é relacionado aos grupos depois. PCA serve à visualização.
        Isolation Forest usa contamination=0.05: a proporção de aproximadamente 5% é configurada,
        não descoberta. Os candidatos a outlier não são removidos do treinamento.
        """),
        code("""
        # Grupos, composição por cultura e rendimento dentro de cada cultura.
        for arquivo in ["resumo_clusters.csv", "composicao_clusters.csv", "tendencias_por_cultura_cluster.csv"]:
            print(arquivo)
            display(pd.read_csv(OUTPUT_DIR / arquivo).round(3))
        print("Silhouette:", resumo["silhouette_scores"])
        print("Variância explicada pelo PCA:", resumo["pca_variancia_explicada"])
        display(Image(filename=str(OUTPUT_DIR / "cluster_pca_outliers.png")))
        display(pd.read_csv(OUTPUT_DIR / "exemplos_outliers.csv"))
        """),
        md("""
        **Interpretação dos grupos:** k=3 tem o melhor silhouette, aproximadamente 0,3264, uma separação
        moderada. Grupos 0, 1 e 2 têm 44, 68 e 44 registros, com as quatro culturas igualmente representadas
        em cada grupo. O grupo 1 tem maior precipitação média (2733,52); o 0 maior temperatura (26,48 °C).
        Arroz tem rendimento médio de 35576,55 no grupo 0 e 27002,73 no 2. Borracha apresenta o padrão
        inverso: 6808,64 e 8916,00. Não há um grupo universalmente mais produtivo para todas as culturas.

        Os oito outliers representam dois cenários repetidos em quatro culturas. Um tem umidade específica
        17,54 e relativa 82,11%; outro tem a menor temperatura do conjunto, 25,56 °C. São extremos
        relativos à amostra, não prova de seca, falha do sensor ou dano agronômico.
        """),
        md("""
        ## 5. Cinco algoritmos e métricas
        Regressão Linear, Ridge (linear regularizada), Random Forest, Gradient Boosting e Extra Trees.
        A tabela é ordenada pelo RMSE médio de validação cruzada, e não pelo teste.

        MAE mede erro absoluto médio; MSE erro quadrático; RMSE volta à escala original do alvo.
        R² mede desempenho relativo à média e pode ser negativo. **R² não é percentual de acerto.**
        MAE/RMSE usam a unidade original de Yield; MSE usa essa unidade ao quadrado.
        """),
        code("""
        # Compara a seleção por CV e o desempenho no teste reservado.
        metricas = pd.read_csv(OUTPUT_DIR / "metricas_modelos.csv")
        display(metricas[["modelo", "CV_RMSE_medio", "CV_RMSE_desvio", "MAE", "MSE", "RMSE", "R2", "selecionado_por_cv"]].round(4))
        display(Image(filename=str(OUTPUT_DIR / "comparacao_validacao_cruzada.png")))
        display(Image(filename=str(OUTPUT_DIR / "comparacao_modelos_r2_rmse.png")))
        """),
        code("""
        # Avaliação contra referência simples e separadamente por cultura.
        display(pd.read_csv(OUTPUT_DIR / "metricas_baseline.csv").round(4))
        por_cultura = pd.read_csv(OUTPUT_DIR / "metricas_por_cultura.csv")
        display(por_cultura[por_cultura.modelo.isin([resumo["melhor_modelo"], "Média por cultura (treino)"])].round(4))
        display(Image(filename=str(OUTPUT_DIR / "importancia_variaveis.png")))
        """),
        md("RESULTADO_ATUAL"),
        md("""
        ## 6. Previsão para um cenário de arroz
        O pipeline salvo foi selecionado por CV e ajustado apenas ao treino. As entradas abaixo estão
        dentro das faixas observadas. A saída é mantida na unidade original do CSV.
        """),
        code("""
        # Célula curta para execução ao vivo no vídeo.
        modelo = joblib.load(MODELS_DIR / "melhor_modelo_rendimento.joblib")
        cenario = pd.DataFrame([{
            "cultura": "Rice, paddy", "precipitacao_mm_dia": 2450.0,
            "umidade_especifica_2m_g_kg": 18.2, "umidade_relativa_2m_pct": 84.7,
            "temperatura_2m_c": 26.2,
        }])
        cenario["rendimento_previsto_unidade_original"] = modelo.predict(cenario).round(3)
        display(cenario)
        """),
        md("""
        ## 7. Conclusões
        **Pontos fortes:** base oficial rastreável, pipeline reproduzível, cinco algoritmos,
        seleção por CV, cenários separados, baseline, métricas por cultura e outliers concretos.

        **Limitações:** apenas 39 cenários, ausência de datas/talhões/manejo, escala e periodicidade
        a confirmar na fonte, grupos moderadamente separados, proporção de outliers definida a priori
        e forte influência da diferença entre culturas no R² global. Cada cultura tem apenas nove
        observações no teste. A avaliação não demonstra generalização temporal para uma safra futura.

        O resultado é um protótipo educacional. Próximos passos: confirmar unidades, incluir variáveis
        de manejo e identificação temporal/espacial e validar em safras independentes.
        """),
    ]
    return nb

def main():
    nb = criar_notebook()
    NotebookClient(nb, timeout=900, kernel_name="python3",
                   resources={"metadata": {"path": str(BASE_DIR.parent)}}).execute()
    r = json.loads((BASE_DIR / "outputs/resumo_analise.json").read_text(encoding="utf-8"))
    m, b = r["metricas_melhor_modelo"], r["avaliacao"]["baseline_teste"]
    for cell in nb.cells:
        if cell.cell_type == "markdown" and cell.source == "RESULTADO_ATUAL":
            cell.source = (
                f"**Resultado:** {r['melhor_modelo']} selecionado com RMSE médio de CV {m['CV_RMSE_medio']:.2f}. "
                f"No teste: MAE {m['MAE']:.2f}, RMSE {m['RMSE']:.2f} e R² {m['R2']:.4f}. "
                f"A média por cultura teve RMSE {b['RMSE']:.2f} e R² {b['R2']:.4f}; a redução de RMSE foi "
                f"{100*(1-m['RMSE']/b['RMSE']):.2f}%. No Extra Trees, só arroz tem R² por cultura positivo "
                "(aproximadamente 0,436). As outras três culturas têm R² negativo, apesar do R² global alto. "
                "Importância interna não é efeito causal; coeficientes lineares também não equivalem às importâncias de árvores."
            )
    NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, NOTEBOOK_PATH)
    print(f"Notebook oficial executado: {NOTEBOOK_PATH}")

if __name__ == "__main__":
    main()
