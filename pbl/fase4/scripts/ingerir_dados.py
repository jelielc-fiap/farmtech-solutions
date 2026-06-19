from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd

from criar_banco import DB_PATH, criar_banco
from gerar_dados_iot import OUTPUT_CSV, enriquecer_dados


COLUNAS_DB = {
    "Data_Leitura": "data_leitura",
    "Cultura": "cultura",
    "Umidade": "umidade",
    "pH": "ph",
    "N_ok": "n_ok",
    "P_ok": "p_ok",
    "K_ok": "k_ok",
    "Chuva_Probabilidade": "chuva_probabilidade",
    "Bomba_Ligada": "bomba_ligada",
    "Umidade_Futura": "umidade_futura",
    "pH_Futuro": "ph_futuro",
    "Volume_Irrigacao_L": "volume_irrigacao_l",
    "Necessidade_Fertilizacao_kg_ha": "necessidade_fertilizacao_kg_ha",
    "Rendimento_Estimado_t_ha": "rendimento_estimado_t_ha",
}


def carregar_dataset(caminho_csv: Path = OUTPUT_CSV) -> pd.DataFrame:
    if not caminho_csv.exists():
        enriquecer_dados(destino=caminho_csv)
    df = pd.read_csv(caminho_csv, encoding="utf-8")
    df["Data_Leitura"] = pd.to_datetime(df["Data_Leitura"]).dt.strftime("%Y-%m-%d")
    return df


def ingerir_dados(caminho_csv: Path = OUTPUT_CSV, db_path: Path = DB_PATH) -> tuple[int, int]:
    criar_banco(db_path)
    df = carregar_dataset(caminho_csv).rename(columns=COLUNAS_DB)
    colunas = list(COLUNAS_DB.values())
    placeholders = ", ".join(["?"] * len(colunas))
    sql = f"""
        INSERT OR IGNORE INTO leituras_sensores ({", ".join(colunas)})
        VALUES ({placeholders})
    """

    with sqlite3.connect(db_path) as conn:
        antes = conn.execute("SELECT COUNT(*) FROM leituras_sensores").fetchone()[0]
        conn.executemany(sql, df[colunas].itertuples(index=False, name=None))
        depois = conn.execute("SELECT COUNT(*) FROM leituras_sensores").fetchone()[0]
        inseridos = depois - antes
        conn.execute(
            """
            INSERT INTO execucoes_ingestao
            (executado_em, arquivo_origem, registros_lidos, registros_inseridos)
            VALUES (?, ?, ?, ?)
            """,
            (datetime.now().isoformat(timespec="seconds"), str(caminho_csv), len(df), inseridos),
        )
    return len(df), inseridos


if __name__ == "__main__":
    lidos, inseridos = ingerir_dados()
    print(f"Registros lidos: {lidos}")
    print(f"Registros inseridos: {inseridos}")
