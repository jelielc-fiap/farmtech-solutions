"""Leitura e rastreabilidade do CSV, sem gerar ou sobrescrever dados automaticamente."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "crop_yield.csv"
ORIGEM_PATH = BASE_DIR / "data" / "origem_dataset.json"
NUMERICAS = ["precipitacao_mm_dia", "umidade_especifica_2m_g_kg", "umidade_relativa_2m_pct", "temperatura_2m_c"]
CATEGORICAS = ["cultura"]
ALVO = "rendimento_t_ha"
COLUNAS_ORIGINAIS = {
    "Cultura": "cultura",
    "Precipitação (mm dia 1)": NUMERICAS[0],
    "Umidade específica a 2 metros (g/kg)": NUMERICAS[1],
    "Umidade relativa a 2 metros (%)": NUMERICAS[2],
    "Temperatura a 2 metros (ºC)": NUMERICAS[3],
    "Rendimento": ALVO,
}


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", texto)


ALIASES = {normalizar(k): v for k, v in COLUNAS_ORIGINAIS.items()}
ALIASES.update({normalizar(v): v for v in COLUNAS_ORIGINAIS.values()})
for destino, nomes in {
    "cultura": ["Crop", "Crop Type"],
    NUMERICAS[0]: ["Precipitation (mm day-1)", "Precipitation (mm day 1)"],
    NUMERICAS[1]: ["Specific Humidity at 2 Meters (g/kg)", "Specific humidity at 2m (g/kg)"],
    NUMERICAS[2]: ["Relative Humidity at 2 Meters (%)", "Relative humidity at 2m (%)"],
    NUMERICAS[3]: ["Temperature at 2 Meters (C)", "Temperature at 2m (C)"],
    ALVO: ["Yield", "Yield (t/ha)", "Crop Yield"],
}.items():
    ALIASES.update({normalizar(nome): destino for nome in nomes})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ler_csv(path: Path = DATA_PATH) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    if not path.exists():
        raise FileNotFoundError("CSV ausente. Baixe crop_yield.csv do portal e use importar_dataset.py.")
    # Detecta separador e BOM; o arquivo original permanece intacto.
    raw = pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig")
    mapa = {c: ALIASES.get(normalizar(c)) for c in raw.columns}
    mapa = {c: d for c, d in mapa.items() if d is not None}
    faltantes = set(CATEGORICAS + NUMERICAS + [ALVO]) - set(mapa.values())
    if faltantes or len(set(mapa.values())) != len(mapa):
        raise ValueError(f"Cabeçalhos não reconhecidos ou duplicados. Faltantes: {sorted(faltantes)}. Encontrados: {list(raw.columns)}")
    df = raw.rename(columns=mapa)[CATEGORICAS + NUMERICAS + [ALVO]].copy()
    df["cultura"] = df["cultura"].astype("string").str.strip().replace("", pd.NA)
    for coluna in NUMERICAS + [ALVO]:
        df[coluna] = pd.to_numeric(df[coluna].astype("string").str.replace(",", ".", regex=False), errors="coerce")
    df = df.replace([np.inf, -np.inf], np.nan)
    invalidas = df.isna().any(axis=1)
    duplicadas = df.loc[~invalidas].duplicated()
    # Duplicatas completas não devem aparecer dos dois lados da divisão treino/teste.
    limpo = df.loc[~invalidas].drop_duplicates().reset_index(drop=True)
    if len(limpo) < 20:
        raise ValueError("Menos de 20 registros válidos e únicos; revise o arquivo e o esquema antes de treinar.")
    limpo["cultura"] = limpo["cultura"].astype(str)
    qualidade = {
        "linhas_originais": len(raw), "linhas_invalidas_removidas": int(invalidas.sum()),
        "duplicatas_removidas": int(duplicadas.sum()), "linhas_analisadas": len(limpo),
        "ausentes_originais": {str(k): int(v) for k, v in raw.isna().sum().items()},
        "mapeamento_colunas": mapa, "sha256": sha256(path),
    }
    return raw, limpo, qualidade


def ler_origem(path: Path = DATA_PATH) -> dict:
    if not ORIGEM_PATH.exists():
        return {"tipo": "nao_confirmada", "descricao": "Origem ainda não registrada"}
    origem = json.loads(ORIGEM_PATH.read_text(encoding="utf-8"))
    if origem.get("sha256") != sha256(path):
        raise ValueError("O CSV mudou desde o registro de origem. Importe novamente o arquivo do portal.")
    return origem


def carregar_dados(permitir_sintetico: bool = False) -> pd.DataFrame:
    _, df, qualidade = ler_csv()
    origem = ler_origem()
    if origem.get("tipo") != "portal_fiap" and not permitir_sintetico:
        raise ValueError("Base oficial pendente. Use importar_dataset.py com o arquivo baixado do portal. Dados sintéticos não são aceitos no fluxo de entrega.")
    df.attrs["qualidade"] = qualidade
    df.attrs["origem"] = origem
    return df
