from __future__ import annotations

import sqlite3
import time
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "leituras_esp32.db"


st.set_page_config(
    page_title="FarmTech ESP32 IoT",
    layout="wide",
)


st.markdown(
    """
    <style>
    :root {
        --farm-bg: #eef5ef;
        --farm-card: #ffffff;
        --farm-text: #183629;
        --farm-muted: #607467;
        --farm-border: #c8d8ce;
        --farm-green: #166534;
    }
    .stApp {
        background: var(--farm-bg);
        color: var(--farm-text);
    }
    .hero {
        background: #123524;
        color: #ffffff;
        padding: 1.35rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .hero h1 {
        color: #ffffff !important;
        margin: 0;
        font-size: 2rem;
    }
    .hero p {
        color: #d9efe1;
        margin: .35rem 0 0;
    }
    .metric-card {
        background: var(--farm-card);
        border: 1px solid var(--farm-border);
        border-radius: 10px;
        padding: 1rem;
        min-height: 112px;
    }
    .metric-card span {
        color: var(--farm-muted);
        font-size: .88rem;
    }
    .metric-card strong {
        display: block;
        color: var(--farm-text);
        font-size: 1.7rem;
        margin-top: .35rem;
    }
    .panel {
        background: var(--farm-card);
        border: 1px solid var(--farm-border);
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_empty_state() -> None:
    st.info(
        "Nenhuma leitura encontrada ainda. Inicie o servidor local e envie dados pelo ESP32 "
        "ou rode `py scripts\\enviar_leitura_teste.py`."
    )


@st.cache_data(ttl=5)
def load_readings(limit: int) -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame()

    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(
            "SELECT * FROM sensor_readings ORDER BY id DESC LIMIT ?",
            conn,
            params=(limit,),
        )

    if df.empty:
        return df

    df = df.sort_values("id").reset_index(drop=True)
    df["received_at"] = pd.to_datetime(df["received_at"], errors="coerce")
    return df


def metric_card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <span>{label}</span>
            <strong>{value}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="hero">
        <h1>FarmTech ESP32 IoT</h1>
        <p>Monitoramento real de temperatura, umidade do ar e umidade do solo.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title("Filtros")
limit = st.sidebar.slider("Quantidade de leituras", 20, 500, 120, 20)
auto_refresh = st.sidebar.checkbox("Atualização automática", value=True)
refresh_seconds = st.sidebar.slider("Intervalo de atualização (s)", 3, 30, 5, 1)
if st.sidebar.button("Atualizar agora", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption(f"Banco local: `{DB_PATH}`")
st.sidebar.caption("Servidor esperado: `http://localhost:5000`")

df = load_readings(limit)

if df.empty:
    init_empty_state()
    st.stop()

latest = df.iloc[-1]

col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Temperatura do ar", f"{latest['temperature_air_c']:.1f} °C")
with col2:
    metric_card("Umidade do ar", f"{latest['humidity_air_pct']:.1f}%")
with col3:
    metric_card("Umidade do solo", f"{latest['soil_moisture_pct']:.1f}%")
with col4:
    metric_card("Risco operacional", str(latest["risk_level"]))

with st.container(border=True):
    st.subheader("Recomendação automática")
    st.write(str(latest["recommendation"]))

chart_df = df[["received_at", "temperature_air_c", "humidity_air_pct", "soil_moisture_pct"]].melt(
    id_vars="received_at",
    var_name="variavel",
    value_name="valor",
)
chart_df["variavel"] = chart_df["variavel"].replace(
    {
        "temperature_air_c": "Temperatura do ar (°C)",
        "humidity_air_pct": "Umidade do ar (%)",
        "soil_moisture_pct": "Umidade do solo (%)",
    }
)

fig = px.line(
    chart_df,
    x="received_at",
    y="valor",
    color="variavel",
    markers=True,
    labels={"received_at": "Recebido em", "valor": "Valor", "variavel": "Variável"},
)
fig.update_layout(
    title="",
    plot_bgcolor="#fbfdfb",
    paper_bgcolor="#ffffff",
    font={"color": "#183629"},
    legend_title_text="",
    margin={"l": 20, "r": 20, "t": 20, "b": 20},
)

with st.container(border=True):
    st.subheader("Histórico das leituras")
    st.plotly_chart(fig, use_container_width=True)

with st.container(border=True):
    st.subheader("Dados recebidos do ESP32")
    st.dataframe(
        df.sort_values("id", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

if auto_refresh:
    time.sleep(refresh_seconds)
    st.cache_data.clear()
    st.rerun()
