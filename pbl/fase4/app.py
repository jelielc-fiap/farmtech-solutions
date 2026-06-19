from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from criar_banco import DB_PATH
from ingerir_dados import ingerir_dados
from recomendacoes import recomendar_manejo
from treinar_modelos import FEATURES, METRICS_FILE, MODELS_DIR, TARGETS, treinar_modelos


COLORS = {
    "forest": "#155332",
    "leaf": "#237044",
    "mint": "#e9f5ee",
    "soil": "#6b4a24",
    "amber": "#9a6500",
    "water": "#1769c2",
    "danger": "#a3362b",
    "ink": "#17231d",
    "muted": "#4f5f55",
    "line": "#cbd9cf",
    "panel": "#ffffff",
    "app_bg": "#f7faf7",
    "sidebar_bg": "#eef5ef",
}

CHART_COLORS = ["#155332", "#1769c2", "#9a6500", "#a3362b", "#5b4aa0", "#00766f"]


st.set_page_config(
    page_title="FarmTech Fase 4",
    page_icon=":seedling:",
    layout="wide",
    initial_sidebar_state="expanded",
)

sidebar_width = "288px"


st.markdown(
    f"""
    <style>
        .stApp {{
            background: {COLORS["app_bg"]};
            color: {COLORS["ink"]};
        }}
        html {{
            scrollbar-gutter: stable;
        }}
        .stApp, .stApp p, .stApp label, .stApp span {{
            color: {COLORS["ink"]};
        }}
        [data-testid="stHeader"] {{
            background: transparent;
            height: 0;
            min-height: 0;
            pointer-events: none;
        }}
        [data-testid="stHeader"]::before {{
            content: "";
            display: none;
        }}
        [data-testid="stToolbar"] {{
            display: none;
        }}
        [data-testid="stHeader"] button {{
            display: none !important;
        }}
        [data-testid="stHeader"] button svg {{
            fill: #ffffff !important;
        }}
        [data-testid="stMain"] {{
            overflow-y: scroll;
            scrollbar-gutter: stable;
        }}
        [data-testid="stSidebar"] {{
            background: {COLORS["sidebar_bg"]};
            border-right: 1px solid {COLORS["line"]};
            width: {sidebar_width} !important;
            min-width: {sidebar_width} !important;
            max-width: {sidebar_width} !important;
            transform: translateX(0) !important;
        }}
        [data-testid="stSidebarHeader"] {{
            display: none !important;
        }}
        [data-testid="stSidebarCollapseButton"] {{
            display: none !important;
            pointer-events: none !important;
        }}
        [data-testid="stSidebar"] * {{
            color: {COLORS["ink"]};
        }}
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p {{
            color: {COLORS["ink"]} !important;
        }}
        [data-testid="stSidebar"] [data-baseweb="select"] > div,
        [data-testid="stSidebar"] [data-baseweb="input"] > div {{
            background: #ffffff !important;
            border: 1px solid #9fb4a7 !important;
            border-radius: 8px !important;
        }}
        [data-testid="stSidebar"] .stDateInput [data-baseweb="input"] > div {{
            align-items: center !important;
            min-height: 42px !important;
            width: 100% !important;
            padding: 0 !important;
            border: 1px solid #9fb4a7 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
            outline: none !important;
            overflow: hidden !important;
        }}
        [data-testid="stSidebar"] .stDateInput [data-baseweb="input"] > div:focus-within {{
            border-color: {COLORS["forest"]} !important;
            box-shadow: 0 0 0 2px rgba(21, 83, 50, .14) !important;
        }}
        [data-testid="stSidebar"] .stDateInput input {{
            height: 40px !important;
            width: 100% !important;
            padding: 0 12px !important;
            border: 0 !important;
            outline: 0 !important;
            box-shadow: none !important;
            background: transparent !important;
            border-radius: 8px !important;
        }}
        [data-testid="stSidebar"] .stMultiSelect {{
            margin-bottom: 8px;
        }}
        [data-testid="stSidebar"] .stDateInput,
        [data-testid="stSidebar"] .stDateInput [data-baseweb="input"] {{
            width: 100% !important;
            padding: 0 !important;
            border: 0 !important;
            box-shadow: none !important;
            background: transparent !important;
        }}
        [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"],
        [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div,
        [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div > div {{
            height: auto !important;
            min-height: 84px !important;
            overflow: visible !important;
        }}
        [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div > div > div {{
            align-items: flex-start !important;
            height: auto !important;
            min-height: 76px !important;
            max-height: none !important;
            overflow: visible !important;
            padding: 7px 8px !important;
        }}
        [data-testid="stSidebar"] .stMultiSelect input {{
            background: transparent !important;
            border: 0 !important;
            box-shadow: none !important;
            min-width: 2px !important;
            width: 2px !important;
            padding: 0 !important;
        }}
        [data-testid="stSidebar"] input {{
            color: {COLORS["ink"]} !important;
            background: #ffffff !important;
        }}
        [data-testid="stSidebar"] svg {{
            fill: {COLORS["forest"]} !important;
        }}
        [data-testid="stSidebar"] [data-baseweb="tag"] {{
            background: {COLORS["forest"]} !important;
            border: 1px solid {COLORS["forest"]} !important;
            border-radius: 6px !important;
            flex: 0 0 auto !important;
            height: 28px !important;
            margin-bottom: 4px !important;
        }}
        [data-testid="stSidebar"] [data-baseweb="tag"] span,
        [data-testid="stSidebar"] [data-baseweb="tag"] svg {{
            color: #ffffff !important;
            fill: #ffffff !important;
        }}
        [data-testid="stSidebar"] button {{
            background: {COLORS["forest"]} !important;
            border: 1px solid {COLORS["forest"]} !important;
            color: #ffffff !important;
            border-radius: 8px !important;
        }}
        [data-testid="stSidebar"] div[data-testid="stButton"] button {{
            height: 40px !important;
            min-height: 40px !important;
            white-space: nowrap !important;
        }}
        [data-testid="stSidebar"] button p,
        [data-testid="stSidebar"] button span {{
            color: #ffffff !important;
        }}
        .block-container {{
            width: 100%;
            box-sizing: border-box;
            max-width: 1320px;
            padding-top: 1.2rem;
            padding-bottom: 3rem;
        }}
        .hero {{
            width: 100%;
            box-sizing: border-box;
            display: block;
            min-height: 158px;
            padding: 26px 30px;
            border-radius: 8px;
            background: linear-gradient(120deg, #123f28 0%, #155332 55%, #1f6d42 100%);
            color: white;
            box-shadow: 0 18px 42px rgba(21, 83, 50, .18);
            margin-bottom: 18px;
        }}
        .hero h1 {{
            color: #ffffff !important;
            margin: 0 0 8px 0;
            font-size: 2.2rem;
            letter-spacing: 0;
        }}
        .hero h1,
        .hero h1 *,
        .hero h1 span {{
            color: #ffffff !important;
        }}
        .hero h1 a {{
            display: none !important;
        }}
        .hero p {{
            color: #f3fff7 !important;
            max-width: 900px;
            margin: 0;
        }}
        .eyebrow {{
            color: #d9f5e1 !important;
            text-transform: uppercase;
            font-size: .78rem;
            font-weight: 700;
            letter-spacing: .08em;
            margin-bottom: 8px;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 14px;
            margin-bottom: 16px;
        }}
        .metric-card {{
            background: white;
            border: 1px solid {COLORS["line"]};
            border-radius: 8px;
            padding: 15px 16px;
            box-shadow: 0 10px 26px rgba(31, 42, 36, .06);
            min-height: 112px;
        }}
        .metric-label {{
            color: {COLORS["muted"]};
            font-size: .88rem;
            font-weight: 700;
            margin-bottom: 7px;
        }}
        .metric-value {{
            color: {COLORS["forest"]};
            font-size: 1.9rem;
            line-height: 1.05;
            font-weight: 820;
            overflow-wrap: anywhere;
        }}
        .metric-delta {{
            color: {COLORS["soil"]};
            font-size: .86rem;
            margin-top: 8px;
        }}
        .section-title {{
            color: {COLORS["forest"]};
            font-size: 1.16rem;
            font-weight: 760;
            margin: .5rem 0 .6rem 0;
        }}
        .rec-box {{
            background: white;
            border: 1px solid {COLORS["line"]};
            border-left: 5px solid {COLORS["leaf"]};
            border-radius: 8px;
            padding: 15px 16px;
            box-shadow: 0 10px 26px rgba(31, 42, 36, .06);
            min-height: 132px;
        }}
        .rec-box strong {{
            color: {COLORS["forest"]};
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            border-bottom: 1px solid {COLORS["line"]};
        }}
        .stTabs [data-baseweb="tab"] {{
            background: #ffffff;
            border: 1px solid {COLORS["line"]};
            border-bottom: 0;
            border-radius: 8px 8px 0 0;
            width: auto !important;
            min-width: max-content !important;
            padding-left: 20px;
            padding-right: 20px;
            flex: 0 0 auto;
        }}
        .stTabs [data-baseweb="tab"] p {{
            color: {COLORS["forest"]};
            font-weight: 760;
        }}
        .stTabs [aria-selected="true"] {{
            background: {COLORS["forest"]};
        }}
        .stTabs [aria-selected="true"] p {{
            color: #ffffff;
        }}
        div[data-testid="stDataFrame"] {{
            border: 1px solid {COLORS["line"]};
            border-radius: 8px;
            overflow: hidden;
        }}
        div[data-testid="stElementContainer"]:has(> div[data-testid="stCheckbox"]) {{
            background: transparent !important;
            border: 0 !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            padding: 0 !important;
        }}
        div[data-testid="stCheckbox"] > label {{
            background: transparent !important;
            border: 0 !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background: #ffffff;
            border: 1px solid {COLORS["line"]};
            border-radius: 8px;
            box-shadow: 0 10px 26px rgba(31, 42, 36, .06);
        }}
        div[data-testid="stPlotlyChart"] {{
            background: #ffffff;
            border: 1px solid {COLORS["line"]};
            border-radius: 8px;
            padding: 14px;
            box-shadow: 0 8px 22px rgba(31, 42, 36, .05);
            box-sizing: border-box;
        }}
        div[data-testid="stPlotlyChart"] > div {{
            border-radius: 8px;
            overflow: hidden;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


def garantir_pipeline() -> None:
    modelos_ok = all((MODELS_DIR / f"{alvo}.joblib").exists() for alvo in TARGETS)
    if not DB_PATH.exists() or not modelos_ok or not METRICS_FILE.exists():
        with st.spinner("Preparando banco, ingestão e modelos preditivos..."):
            ingerir_dados()
            treinar_modelos()


@st.cache_data(show_spinner=False)
def carregar_tabelas() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    with sqlite3.connect(DB_PATH) as conn:
        leituras = pd.read_sql_query("SELECT * FROM leituras_sensores ORDER BY data_leitura", conn)
        ingestao = pd.read_sql_query("SELECT * FROM execucoes_ingestao ORDER BY id DESC", conn)
        previsoes = pd.read_sql_query("SELECT * FROM previsoes_modelo ORDER BY id DESC", conn)
        recomendacoes = pd.read_sql_query(
            """
            SELECT r.*, l.data_leitura, l.cultura, l.umidade, l.ph, l.rendimento_estimado_t_ha
            FROM recomendacoes_manejo r
            JOIN leituras_sensores l ON l.id = r.leitura_id
            ORDER BY l.data_leitura DESC
            """,
            conn,
        )
    leituras["data_leitura"] = pd.to_datetime(leituras["data_leitura"])
    return leituras, ingestao, previsoes, recomendacoes


def carregar_metricas() -> dict:
    return json.loads(METRICS_FILE.read_text(encoding="utf-8"))


def aplicar_layout(fig: go.Figure, altura: int = 420) -> go.Figure:
    titulo = fig.layout.title.text or ""
    fig.update_layout(
        height=altura,
        paper_bgcolor=COLORS["panel"],
        plot_bgcolor=COLORS["panel"],
        font=dict(color=COLORS["ink"], family="Arial", size=14),
        title=dict(text=titulo, font=dict(color=COLORS["forest"], size=19)),
        margin=dict(l=20, r=20, t=52, b=36),
        colorway=CHART_COLORS,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0)",
            font=dict(color=COLORS["ink"], size=13),
        ),
        xaxis=dict(
            gridcolor="#d8e3db",
            linecolor="#8da497",
            zeroline=False,
            tickfont=dict(color=COLORS["ink"]),
            title_font=dict(color=COLORS["ink"]),
        ),
        yaxis=dict(
            gridcolor="#d8e3db",
            linecolor="#8da497",
            zeroline=False,
            tickfont=dict(color=COLORS["ink"]),
            title_font=dict(color=COLORS["ink"]),
        ),
        coloraxis_colorbar=dict(
            tickfont=dict(color=COLORS["ink"]),
            title=dict(font=dict(color=COLORS["ink"])),
        ),
    )
    return fig


def prever(alvo: str, cenario: dict) -> float:
    modelo = joblib.load(MODELS_DIR / f"{alvo}.joblib")
    entrada = pd.DataFrame([cenario])[FEATURES]
    return float(modelo.predict(entrada)[0])


def texto_pt(valor: object) -> str:
    texto = str(valor)
    substituicoes = {
        "Irrigar": "Irrigar",
        "Irrigacao": "Irrigação",
        "irrigacao": "irrigação",
        "Recomendacao": "Recomendação",
        "recomendacao": "recomendação",
        "Fertilizacao": "Fertilização",
        "fertilizacao": "fertilização",
        "previsao": "previsão",
        "Correlacao": "Correlação",
        "correlacao": "correlação",
        "Historico": "Histórico",
        "ingestao": "ingestão",
        "Acoes": "Ações",
        "acao": "ação",
        "automacao": "automação",
        "disponiveis": "disponíveis",
        "agricola": "agrícola",
        "necessaria": "necessária",
        "proximas": "próximas",
        "Decisao": "Decisão",
        "umidade": "umidade",
    }
    for origem, destino in substituicoes.items():
        texto = texto.replace(origem, destino)
    return texto


garantir_pipeline()
leituras, ingestao, previsoes, recomendacoes = carregar_tabelas()
metricas = carregar_metricas()

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow" style="color: #d9f5e1;">FarmTech Solutions - Fase 4</div>
        <h1 style="color: #ffffff;">Assistente Agrícola Inteligente</h1>
        <p style="color: #f3fff7;">Pipeline com sensores IoT simulados, banco SQL, regressão supervisionada e recomendações de irrigação e manejo para apoio ao gestor agrícola.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    culturas = sorted(leituras["cultura"].unique())
    datas = leituras["data_leitura"].dt.date

    st.markdown("## Filtros")
    cultura_sel = st.multiselect("Cultura", culturas, default=culturas)
    intervalo = st.date_input(
        "Período",
        value=(datas.min(), datas.max()),
        min_value=datas.min(),
        max_value=datas.max(),
    )
    if st.button("Atualizar ingestão e modelos", use_container_width=True):
        ingerir_dados()
        treinar_modelos()
        st.cache_data.clear()
        st.rerun()

inicio, fim = intervalo if len(intervalo) == 2 else (datas.min(), datas.max())
dados = leituras[
    (leituras["cultura"].isin(cultura_sel))
    & (leituras["data_leitura"].dt.date >= inicio)
    & (leituras["data_leitura"].dt.date <= fim)
].copy()

if dados.empty:
    st.warning("Nenhum registro encontrado para os filtros selecionados.")
    st.stop()

ultima = dados.iloc[-1]
rec_ultima = recomendacoes[recomendacoes["leitura_id"] == ultima["id"]].iloc[0]

aba_geral, aba_banco, aba_corr, aba_modelos, aba_simulador, aba_recs = st.tabs(
    ["Visão Geral", "Banco IoT", "Correlação", "Modelos ML", "Simulador", "Recomendações"]
)

with aba_geral:
    st.markdown(
        f"""
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Rendimento previsto</div>
                <div class="metric-value">{ultima['rendimento_estimado_t_ha']:.2f} t/ha</div>
                <div class="metric-delta">Cultura: {ultima['cultura']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Umidade futura</div>
                <div class="metric-value">{ultima['umidade_futura']:.1f}%</div>
                <div class="metric-delta">Leitura atual: {ultima['umidade']:.1f}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Irrigação recomendada</div>
                <div class="metric-value">{ultima['volume_irrigacao_l']:.0f} L</div>
                <div class="metric-delta">por hectare</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Risco produtivo</div>
                <div class="metric-value">{rec_ultima['risco_produtivo']}</div>
                <div class="metric-delta">{ultima['data_leitura'].strftime('%d/%m/%Y')}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.markdown('<div class="section-title">Tendência de produtividade estimada</div>', unsafe_allow_html=True)
        fig = px.line(
            dados,
            x="data_leitura",
            y="rendimento_estimado_t_ha",
            color="cultura",
            markers=True,
            labels={"data_leitura": "Data", "rendimento_estimado_t_ha": "t/ha"},
            color_discrete_sequence=CHART_COLORS,
        )
        st.plotly_chart(aplicar_layout(fig), use_container_width=True)

    st.markdown('<div class="section-title">Recomendação principal</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="rec-box">
            <p><strong>Irrigação:</strong> {texto_pt(rec_ultima['acao_irrigacao'])}</p>
            <p><strong>pH:</strong> {texto_pt(rec_ultima['acao_ph'])}</p>
            <p><strong>Nutrientes:</strong> {texto_pt(rec_ultima['acao_nutrientes'])}</p>
            <p>{texto_pt(rec_ultima['justificativa'])}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with aba_banco:
    with st.container(border=True):
        st.markdown('<div class="section-title">Histórico de ingestão</div>', unsafe_allow_html=True)
        st.dataframe(ingestao, use_container_width=True, hide_index=True)

        st.markdown('<div class="section-title">Leituras persistidas no SQLite</div>', unsafe_allow_html=True)
        st.dataframe(
            dados[
                [
                    "data_leitura",
                    "cultura",
                    "umidade",
                    "ph",
                    "n_ok",
                    "p_ok",
                    "k_ok",
                    "chuva_probabilidade",
                    "rendimento_estimado_t_ha",
                ]
            ].rename(
                columns={
                    "data_leitura": "Data",
                    "cultura": "Cultura",
                    "umidade": "Umidade",
                    "ph": "pH",
                    "n_ok": "Nitrogênio",
                    "p_ok": "Fósforo",
                    "k_ok": "Potássio",
                    "chuva_probabilidade": "Chuva (%)",
                    "rendimento_estimado_t_ha": "Rendimento (t/ha)",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

with aba_corr:
    with st.container(border=True):
        numericas = [
            "umidade",
            "ph",
            "n_ok",
            "p_ok",
            "k_ok",
            "chuva_probabilidade",
            "bomba_ligada",
            "volume_irrigacao_l",
            "necessidade_fertilizacao_kg_ha",
            "rendimento_estimado_t_ha",
        ]
        corr = dados[numericas].corr().round(2)
        fig_corr = px.imshow(
            corr,
            text_auto=True,
            color_continuous_scale=[
                [0.0, "#d7e8f5"],
                [0.5, "#ffffff"],
                [1.0, "#f1d5c4"],
            ],
            zmin=-1,
            zmax=1,
            title="Matriz de correlação agrícola",
        )
        fig_corr.update_traces(textfont=dict(color=COLORS["ink"], size=12))
        st.plotly_chart(aplicar_layout(fig_corr, 560), use_container_width=True)
        fig_scatter = px.scatter(
            dados,
            x="umidade",
            y="rendimento_estimado_t_ha",
            color="cultura",
            size="chuva_probabilidade",
            hover_data=["ph", "volume_irrigacao_l"],
            title="Relação entre umidade, chuva e rendimento",
            labels={"umidade": "Umidade (%)", "rendimento_estimado_t_ha": "Rendimento (t/ha)"},
            color_discrete_sequence=CHART_COLORS,
        )
        st.plotly_chart(aplicar_layout(fig_scatter), use_container_width=True)

with aba_modelos:
    with st.container(border=True):
        linhas = []
        for alvo, modelos in metricas["metricas"].items():
            for modelo, vals in modelos.items():
                linhas.append(
                    {
                        "Alvo": texto_pt(metricas["targets"][alvo]),
                        "Modelo": modelo,
                        "MAE": vals["MAE"],
                        "MSE": vals["MSE"],
                        "RMSE": vals["RMSE"],
                        "R2": vals["R2"],
                        "Melhor": modelo == metricas["melhores_modelos"][alvo],
                    }
                )
        df_metricas = pd.DataFrame(linhas)
        st.dataframe(df_metricas, use_container_width=True, hide_index=True)
        alvo_grafico = st.selectbox("Alvo para comparar modelos", sorted(df_metricas["Alvo"].unique()))
        fig_metricas = px.bar(
            df_metricas[df_metricas["Alvo"] == alvo_grafico],
            x="Modelo",
            y="R2",
            color="Melhor",
            text="R2",
            title="Comparação de R² por modelo",
            color_discrete_map={True: COLORS["forest"], False: COLORS["amber"]},
        )
        fig_metricas.update_traces(texttemplate="%{text:.3f}", textposition="outside")
        st.plotly_chart(aplicar_layout(fig_metricas, 380), use_container_width=True)
        st.caption(f"Métricas geradas em {metricas['gerado_em']}.")

with aba_simulador:
    st.markdown('<div class="section-title">Cenário interativo para previsão em tempo real</div>', unsafe_allow_html=True)
    with st.container(border=True):
        cultura = st.selectbox("Cultura analisada", ["cafe", "milho", "soja"])

        col_solo, col_clima = st.columns(2)
        with col_solo:
            st.markdown('<div class="section-title">Solo</div>', unsafe_allow_html=True)
            umidade = st.slider("Umidade atual (%)", 25.0, 85.0, 52.0, 0.5)
            ph = st.slider("pH do solo", 4.2, 7.6, 6.0, 0.05)
        with col_clima:
            st.markdown('<div class="section-title">Clima e automação</div>', unsafe_allow_html=True)
            chuva = st.slider("Probabilidade de chuva (%)", 0.0, 100.0, 45.0, 1.0)
            bomba = st.checkbox("Bomba ligada", value=False)

        st.markdown('<div class="section-title">Nutrientes disponíveis</div>', unsafe_allow_html=True)
        col_n, col_p, col_k = st.columns(3)
        with col_n:
            n_ok = st.checkbox("Nitrogênio adequado", value=True)
        with col_p:
            p_ok = st.checkbox("Fósforo adequado", value=True)
        with col_k:
            k_ok = st.checkbox("Potássio adequado", value=True)

    cenario = {
        "umidade": umidade,
        "ph": ph,
        "n_ok": int(n_ok),
        "p_ok": int(p_ok),
        "k_ok": int(k_ok),
        "chuva_probabilidade": chuva,
        "bomba_ligada": int(bomba),
        "cultura": cultura,
    }
    pred_rendimento = prever("rendimento_estimado_t_ha", cenario)
    pred_irrigacao = max(0, prever("volume_irrigacao_l", cenario))
    pred_fert = max(0, prever("necessidade_fertilizacao_kg_ha", cenario))
    pred_umidade = prever("umidade_futura", cenario)
    pred_ph = prever("ph_futuro", cenario)
    rec = recomendar_manejo(
        umidade=umidade,
        ph=ph,
        n_ok=int(n_ok),
        p_ok=int(p_ok),
        k_ok=int(k_ok),
        chuva_probabilidade=chuva,
        rendimento_estimado=pred_rendimento,
        volume_irrigacao=pred_irrigacao,
    )
    st.markdown(
        f"""
        <div class="metric-grid">
            <div class="metric-card"><div class="metric-label">Rendimento</div><div class="metric-value">{pred_rendimento:.2f} t/ha</div><div class="metric-delta">previsão do modelo</div></div>
            <div class="metric-card"><div class="metric-label">Irrigação</div><div class="metric-value">{pred_irrigacao:.0f} L</div><div class="metric-delta">por hectare</div></div>
            <div class="metric-card"><div class="metric-label">Fertilização</div><div class="metric-value">{pred_fert:.0f} kg/ha</div><div class="metric-delta">estimativa de manejo</div></div>
            <div class="metric-card"><div class="metric-label">Solo futuro</div><div class="metric-value">{pred_umidade:.1f}% / {pred_ph:.2f}</div><div class="metric-delta">umidade e pH</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-title">Recomendação para o cenário</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="rec-box">
            <p><strong>Irrigação:</strong> {texto_pt(rec.acao_irrigacao)}</p>
            <p><strong>pH:</strong> {texto_pt(rec.acao_ph)}</p>
            <p><strong>Nutrientes:</strong> {texto_pt(rec.acao_nutrientes)}</p>
            <p><strong>Risco produtivo:</strong> {texto_pt(rec.risco_produtivo)}</p>
            <p>{texto_pt(rec.justificativa)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with aba_recs:
    with st.container(border=True):
        st.markdown('<div class="section-title">Ações futuras de irrigação e manejo</div>', unsafe_allow_html=True)
        rec_filtradas = recomendacoes[recomendacoes["leitura_id"].isin(dados["id"])]
        rec_visiveis = rec_filtradas[
            [
                "data_leitura",
                "cultura",
                "acao_irrigacao",
                "acao_ph",
                "acao_nutrientes",
                "risco_produtivo",
                "justificativa",
            ]
        ].copy()
        for coluna in ["acao_irrigacao", "acao_ph", "acao_nutrientes", "risco_produtivo", "justificativa"]:
            rec_visiveis[coluna] = rec_visiveis[coluna].map(texto_pt)
        rec_visiveis = rec_visiveis.rename(
            columns={
                "data_leitura": "Data",
                "cultura": "Cultura",
                "acao_irrigacao": "Ação de irrigação",
                "acao_ph": "Ação de pH",
                "acao_nutrientes": "Ação de nutrientes",
                "risco_produtivo": "Risco produtivo",
                "justificativa": "Justificativa",
            }
        )
        st.dataframe(
            rec_visiveis,
            use_container_width=True,
            hide_index=True,
        )
        resumo_risco = rec_filtradas["risco_produtivo"].value_counts().reset_index()
        resumo_risco.columns = ["Risco", "Leituras"]
        fig_risco = px.pie(
            resumo_risco,
            names="Risco",
            values="Leituras",
            hole=.45,
            title="Distribuicao do risco produtivo",
            color_discrete_sequence=[COLORS["forest"], COLORS["amber"], COLORS["danger"]],
        )
        st.plotly_chart(aplicar_layout(fig_risco, 380), use_container_width=True)
