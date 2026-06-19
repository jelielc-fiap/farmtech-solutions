from __future__ import annotations

from pathlib import Path
import unicodedata

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
FASE3_CSV = BASE_DIR.parent / "fase3" / "sensores_fase2.csv"
DATA_DIR = BASE_DIR / "data"
OUTPUT_CSV = DATA_DIR / "sensores_iot_enriquecidos.csv"


def normalizar_cultura(valor: str) -> str:
    texto = str(valor).strip().lower()
    if "caf" in texto:
        return "cafe"
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return texto or "cafe"


def enriquecer_dados(origem: Path = FASE3_CSV, destino: Path = OUTPUT_CSV) -> pd.DataFrame:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(origem, encoding="utf-8")
    df.columns = [c.strip() for c in df.columns]
    df["Data_Leitura"] = pd.to_datetime(df["Data_Leitura"], errors="coerce")
    df = df.dropna(subset=["Data_Leitura"]).sort_values("Data_Leitura").reset_index(drop=True)
    df["label"] = df["label"].map(normalizar_cultura)

    culturas = ["cafe", "milho", "soja"]
    medias_cultura = {"cafe": 4.4, "milho": 5.2, "soja": 4.0}
    fator_cultura = df["label"].map(medias_cultura).fillna(4.1)
    dia = np.arange(len(df))
    sazonalidade = np.sin(dia / 8) * 2.8
    nutrientes = df[["N_ok", "P_ok", "K_ok"]].sum(axis=1)

    deficit_umidade = np.maximum(0, 58 - df["Umidade"])
    chuva_efeito = df["Chuva_Probabilidade"] * 0.055
    bomba_efeito = df["Bomba_Ligada"] * 7.5
    df["Umidade_Futura"] = (
        df["Umidade"] + chuva_efeito + bomba_efeito - 3.2 + sazonalidade * 0.25
    ).clip(25, 88).round(2)

    ajuste_ph = (nutrientes - 2) * 0.035 + np.cos(dia / 11) * 0.06
    df["pH_Futuro"] = (df["pH"] + ajuste_ph).clip(4.4, 7.4).round(2)

    df["Volume_Irrigacao_L"] = (
        deficit_umidade * 105
        + (100 - df["Chuva_Probabilidade"]) * 2.5
        - df["Bomba_Ligada"] * 120
    ).clip(0, 1800).round(2)

    df["Necessidade_Fertilizacao_kg_ha"] = (
        (3 - nutrientes) * 28
        + np.maximum(0, 5.5 - df["pH"]) * 12
        + np.maximum(0, df["pH"] - 7.0) * 10
    ).clip(0, 120).round(2)

    penalidade_umidade = np.abs(df["Umidade_Futura"] - 58) * 0.045
    penalidade_ph = np.abs(df["pH_Futuro"] - 6.2) * 0.38
    penalidade_nutriente = (3 - nutrientes) * 0.32
    bonus_chuva = np.minimum(df["Chuva_Probabilidade"], 65) * 0.006
    df["Rendimento_Estimado_t_ha"] = (
        fator_cultura + bonus_chuva - penalidade_umidade - penalidade_ph - penalidade_nutriente
    ).clip(1.4, 7.2).round(2)

    df = df.rename(
        columns={
            "label": "Cultura",
            "pH": "pH",
        }
    )
    colunas = [
        "Data_Leitura",
        "Cultura",
        "Umidade",
        "pH",
        "N_ok",
        "P_ok",
        "K_ok",
        "Chuva_Probabilidade",
        "Bomba_Ligada",
        "Umidade_Futura",
        "pH_Futuro",
        "Volume_Irrigacao_L",
        "Necessidade_Fertilizacao_kg_ha",
        "Rendimento_Estimado_t_ha",
    ]
    df[colunas].to_csv(destino, index=False, encoding="utf-8")
    return df[colunas]


if __name__ == "__main__":
    dados = enriquecer_dados()
    print(f"Dataset enriquecido gerado em: {OUTPUT_CSV}")
    print(f"Total de registros: {len(dados)}")
