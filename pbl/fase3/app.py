from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "sensores_fase2.csv"

COLORS = {
    "forest": "#1f5f3b",
    "leaf": "#2f7d4f",
    "mint": "#e9f5ee",
    "soil": "#8a5a32",
    "amber": "#c78a1d",
    "water": "#2f80ed",
    "danger": "#b84a3a",
    "ink": "#1f2a24",
    "muted": "#66746b",
    "panel": "#ffffff",
    "line": "#dce8df",
}


st.set_page_config(
    page_title="Dashboard de Sensores Agricolas",
    page_icon=":seedling:",
    layout="wide",
)


st.markdown(
    f"""
    <style>
        :root {{
            --forest: {COLORS["forest"]};
            --leaf: {COLORS["leaf"]};
            --mint: {COLORS["mint"]};
            --soil: {COLORS["soil"]};
            --amber: {COLORS["amber"]};
            --water: {COLORS["water"]};
            --danger: {COLORS["danger"]};
            --ink: {COLORS["ink"]};
            --muted: {COLORS["muted"]};
            --panel: {COLORS["panel"]};
            --line: {COLORS["line"]};
        }}

        .stApp {{
            background:
                linear-gradient(180deg, #f3f8f4 0%, #fbf7ef 42%, #f7faf7 100%);
            color: var(--ink);
        }}

        [data-testid="stSidebar"] {{
            background: #f4efe4;
            border-right: 1px solid #e0d2bd;
        }}

        [data-testid="stHeader"] {{
            display: none;
        }}

        [data-testid="stToolbar"] {{
            display: none;
        }}

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {{
            color: var(--forest);
        }}

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span {{
            color: var(--ink);
        }}

        [data-baseweb="tag"] {{
            background-color: var(--leaf) !important;
            border-radius: 6px !important;
        }}

        [data-baseweb="tag"] span {{
            color: #ffffff !important;
        }}

        .block-container {{
            padding-top: 1.4rem;
            padding-bottom: 3rem;
            max-width: 1280px;
        }}

        .hero {{
            padding: 28px 30px;
            border-radius: 8px;
            background:
                linear-gradient(120deg, rgba(31, 95, 59, 0.96), rgba(47, 125, 79, 0.92)),
                radial-gradient(circle at 84% 18%, rgba(236, 190, 92, 0.22), transparent 28%);
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.16);
            box-shadow: 0 18px 45px rgba(31, 95, 59, 0.16);
            margin-bottom: 20px;
        }}

        .hero .eyebrow {{
            text-transform: uppercase;
            font-size: 0.78rem;
            letter-spacing: 0.08em;
            font-weight: 700;
            color: #d9f1df;
            margin-bottom: 8px;
        }}

        .hero h1 {{
            color: #ffffff;
            font-size: 2.25rem;
            line-height: 1.12;
            margin: 0 0 8px 0;
            letter-spacing: 0;
        }}

        .hero p {{
            color: #edf8f0;
            font-size: 1.02rem;
            max-width: 820px;
            margin: 0;
        }}

        .section-title {{
            color: var(--forest);
            font-weight: 760;
            font-size: 1.22rem;
            margin: 1.1rem 0 0.55rem 0;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-color: var(--line);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.86);
            box-shadow: 0 12px 30px rgba(31, 42, 36, 0.07);
        }}

        div[data-testid="stVerticalBlockBorderWrapper"] > div {{
            padding-top: 0.35rem;
        }}

        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 16px;
            margin-bottom: 18px;
        }}

        .metric-card {{
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 16px 18px;
            box-shadow: 0 10px 26px rgba(31, 42, 36, 0.06);
            min-height: 116px;
        }}

        .metric-label {{
            color: var(--muted);
            font-size: 0.9rem;
            font-weight: 700;
            margin-bottom: 8px;
        }}

        .metric-value {{
            color: var(--forest);
            font-size: clamp(1.55rem, 4vw, 2.15rem);
            line-height: 1.05;
            font-weight: 820;
            overflow-wrap: anywhere;
        }}

        .metric-delta {{
            color: var(--soil);
            font-size: 0.88rem;
            margin-top: 8px;
        }}

        .info-panel {{
            background: var(--panel);
            border: 1px solid var(--line);
            border-left: 5px solid var(--leaf);
            border-radius: 8px;
            padding: 18px 18px 14px 18px;
            min-height: 198px;
            box-shadow: 0 10px 26px rgba(31, 42, 36, 0.06);
        }}

        .info-row {{
            display: flex;
            justify-content: space-between;
            gap: 16px;
            padding: 8px 0;
            border-bottom: 1px solid #edf2ee;
        }}

        .info-row:last-child {{
            border-bottom: 0;
        }}

        .info-label {{
            color: var(--muted);
            font-size: 0.92rem;
        }}

        .info-value {{
            color: var(--ink);
            font-weight: 700;
            text-align: right;
        }}

        .suggestion {{
            margin-top: 14px;
            padding: 12px 14px;
            background: var(--mint);
            border-radius: 8px;
            color: var(--forest);
            font-weight: 760;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            border-bottom: 1px solid var(--line);
        }}

        .stTabs [data-baseweb="tab"] {{
            background: #ffffff;
            border: 1px solid var(--line);
            border-bottom: 0;
            border-radius: 8px 8px 0 0;
            color: var(--forest);
            font-weight: 700;
            padding-left: 28px;
            padding-right: 28px;
            min-width: 116px;
        }}

        .stTabs [data-baseweb="tab"] p {{
            color: var(--forest);
            font-weight: 760;
        }}

        .stDataFrame {{
            border: 1px solid var(--line);
            border-radius: 8px;
            overflow: hidden;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def carregar_dados(caminho: Path) -> pd.DataFrame:
    dados = pd.read_csv(caminho, encoding="utf-8")
    dados["Data_Leitura"] = pd.to_datetime(dados["Data_Leitura"], errors="coerce")
    dados = dados.dropna(subset=["Data_Leitura"]).sort_values("Data_Leitura")

    dados["Status_Irrigacao"] = dados["Bomba_Ligada"].map(
        {1: "Bomba ligada", 0: "Bomba desligada"}
    )
    dados["Status_P"] = dados["P_ok"].map({1: "Adequado", 0: "Atencao"})
    dados["Status_K"] = dados["K_ok"].map({1: "Adequado", 0: "Atencao"})
    dados["Sugestao_Irrigacao"] = dados.apply(sugerir_irrigacao, axis=1)
    return dados


def sugerir_irrigacao(linha: pd.Series) -> str:
    umidade = linha["Umidade"]
    chuva = linha["Chuva_Probabilidade"]

    if umidade < 45 and chuva < 60:
        return "Irrigar agora"
    if umidade < 45 and chuva >= 60:
        return "Aguardar chuva"
    if 45 <= umidade < 55 and chuva < 40:
        return "Monitorar e preparar irrigacao"
    if chuva >= 75:
        return "Suspender irrigacao"
    return "Sem irrigacao necessaria"


def formatar_delta(valor_atual: float, valor_anterior: float, sufixo: str = "") -> str:
    if pd.isna(valor_anterior):
        return "sem comparacao"
    diferenca = valor_atual - valor_anterior
    return f"{diferenca:+.1f}{sufixo}"


def aplicar_layout(fig: go.Figure, altura: int = 420) -> go.Figure:
    fig.update_layout(
        height=altura,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        font=dict(color=COLORS["ink"], family="Arial", size=14),
        title=dict(font=dict(color=COLORS["forest"], size=19)),
        margin=dict(l=24, r=20, t=50, b=36),
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
            gridcolor="#dfe9e2",
            linecolor="#9fb6a8",
            zeroline=False,
            title_font=dict(color=COLORS["ink"], size=14),
            tickfont=dict(color=COLORS["ink"], size=12),
        ),
        yaxis=dict(
            gridcolor="#dfe9e2",
            linecolor="#9fb6a8",
            zeroline=False,
            title_font=dict(color=COLORS["ink"], size=14),
            tickfont=dict(color=COLORS["ink"], size=12),
        ),
    )
    return fig


if not DATA_FILE.exists():
    st.error(f"Arquivo nao encontrado: {DATA_FILE}")
    st.stop()

df = carregar_dados(DATA_FILE)

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">FarmTech Solutions</div>
        <h1>Dashboard de Sensores Agricolas</h1>
        <p>Monitoramento de umidade, pH, nutrientes e irrigacao com apoio de dados climaticos para tomada de decisao no campo.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## Filtros")
    st.caption("Ajuste o periodo e os cenarios de irrigacao para analisar as leituras.")
    datas = df["Data_Leitura"].dt.date
    intervalo = st.date_input(
        "Periodo",
        value=(datas.min(), datas.max()),
        min_value=datas.min(),
        max_value=datas.max(),
    )

    status_bomba = st.multiselect(
        "Status da irrigacao",
        options=sorted(df["Status_Irrigacao"].unique()),
        default=sorted(df["Status_Irrigacao"].unique()),
    )

    sugestoes = st.multiselect(
        "Sugestoes",
        options=sorted(df["Sugestao_Irrigacao"].unique()),
        default=sorted(df["Sugestao_Irrigacao"].unique()),
    )

inicio, fim = intervalo if len(intervalo) == 2 else (datas.min(), datas.max())
mascara = (
    (df["Data_Leitura"].dt.date >= inicio)
    & (df["Data_Leitura"].dt.date <= fim)
    & (df["Status_Irrigacao"].isin(status_bomba))
    & (df["Sugestao_Irrigacao"].isin(sugestoes))
)
dados_filtrados = df.loc[mascara].copy()

if dados_filtrados.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

ultimo = dados_filtrados.iloc[-1]
anterior = dados_filtrados.iloc[-2] if len(dados_filtrados) > 1 else pd.Series(dtype=float)

st.markdown(
    f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">Umidade atual</div>
            <div class="metric-value">{ultimo['Umidade']:.1f}%</div>
            <div class="metric-delta">{formatar_delta(ultimo["Umidade"], anterior.get("Umidade", pd.NA), "%")}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">pH atual</div>
            <div class="metric-value">{ultimo['pH']:.2f}</div>
            <div class="metric-delta">{formatar_delta(ultimo["pH"], anterior.get("pH", pd.NA))}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Fosforo (P)</div>
            <div class="metric-value">{ultimo['Status_P']}</div>
            <div class="metric-delta">Nutriente monitorado</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Potassio (K)</div>
            <div class="metric-value">{ultimo['Status_K']}</div>
            <div class="metric-delta">Nutriente monitorado</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.container(border=True):
    st.markdown('<div class="section-title">Resumo operacional</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="info-panel">
            <div class="info-row">
                <span class="info-label">Ultima leitura</span>
                <span class="info-value">{ultimo['Data_Leitura'].date().strftime('%d/%m/%Y')}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Bomba</span>
                <span class="info-value">{ultimo['Status_Irrigacao']}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Chance de chuva</span>
                <span class="info-value">{ultimo['Chuva_Probabilidade']:.0f}%</span>
            </div>
            <div class="suggestion">{ultimo['Sugestao_Irrigacao']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sugestao_resumo = (
        dados_filtrados["Sugestao_Irrigacao"]
        .value_counts()
        .rename_axis("Sugestao")
        .reset_index(name="Leituras")
    )
    fig_sugestoes = px.bar(
        sugestao_resumo,
        y="Sugestao",
        x="Leituras",
        color="Sugestao",
        text="Leituras",
        color_discrete_sequence=[
            COLORS["leaf"],
            COLORS["amber"],
            COLORS["water"],
            COLORS["soil"],
            COLORS["danger"],
        ],
        title="Sugestoes por condicao climatica",
    )
fig_sugestoes.update_traces(textposition="outside", marker_line_width=0)
fig_sugestoes.update_layout(showlegend=False, yaxis_title="", xaxis_title="Leituras")
fig_sugestoes.update_traces(textfont=dict(color=COLORS["ink"], size=13))
st.plotly_chart(aplicar_layout(fig_sugestoes, 360), use_container_width=True)

with st.container(border=True):
    st.markdown('<div class="section-title">Niveis ao longo do tempo</div>', unsafe_allow_html=True)
    aba_umidade, aba_nutrientes, aba_ph = st.tabs(["Umidade", "P e K", "pH"])

    with aba_umidade:
        fig_umidade = px.line(
            dados_filtrados,
            x="Data_Leitura",
            y="Umidade",
            markers=True,
            color="Status_Irrigacao",
            labels={"Umidade": "Umidade (%)", "Data_Leitura": "Data"},
            color_discrete_map={
                "Bomba ligada": COLORS["water"],
                "Bomba desligada": COLORS["leaf"],
            },
            title="Umidade do solo por leitura",
        )
        fig_umidade.update_traces(line_width=3, marker_size=7)
        fig_umidade.add_hline(
            y=45,
            line_dash="dash",
            line_color=COLORS["danger"],
            annotation_text="Umidade critica",
        )
        fig_umidade.add_hline(
            y=55,
            line_dash="dot",
            line_color=COLORS["amber"],
            annotation_text="Monitoramento",
        )
        st.plotly_chart(aplicar_layout(fig_umidade), use_container_width=True)

    with aba_nutrientes:
        nutrientes = dados_filtrados.melt(
            id_vars=["Data_Leitura"],
            value_vars=["P_ok", "K_ok"],
            var_name="Nutriente",
            value_name="Adequado",
        )
        nutrientes["Nutriente"] = nutrientes["Nutriente"].replace(
            {"P_ok": "Fosforo (P)", "K_ok": "Potassio (K)"}
        )
        nutrientes["Status"] = nutrientes["Adequado"].map({1: "Adequado", 0: "Atencao"})

        fig_nutrientes = px.scatter(
            nutrientes,
            x="Data_Leitura",
            y="Nutriente",
            color="Status",
            symbol="Status",
            labels={"Data_Leitura": "Data"},
            color_discrete_map={"Adequado": COLORS["leaf"], "Atencao": COLORS["danger"]},
            title="Disponibilidade de nutrientes",
        )
        fig_nutrientes.update_traces(marker_size=12)
        st.plotly_chart(aplicar_layout(fig_nutrientes), use_container_width=True)

    with aba_ph:
        fig_ph = px.line(
            dados_filtrados,
            x="Data_Leitura",
            y="pH",
            markers=True,
            labels={"pH": "pH", "Data_Leitura": "Data"},
            title="Evolucao do pH",
        )
        fig_ph.update_traces(line_color=COLORS["soil"], line_width=3, marker_size=7)
        fig_ph.add_hrect(
            y0=5.5,
            y1=7.0,
            line_width=0,
            fillcolor=COLORS["leaf"],
            opacity=0.14,
            annotation_text="Faixa ideal",
        )
        st.plotly_chart(aplicar_layout(fig_ph), use_container_width=True)

with st.container(border=True):
    st.markdown('<div class="section-title">Dados filtrados</div>', unsafe_allow_html=True)
    st.dataframe(
        dados_filtrados[
            [
                "Data_Leitura",
                "Umidade",
                "pH",
                "Status_P",
                "Status_K",
                "Chuva_Probabilidade",
                "Status_Irrigacao",
                "Sugestao_Irrigacao",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )
