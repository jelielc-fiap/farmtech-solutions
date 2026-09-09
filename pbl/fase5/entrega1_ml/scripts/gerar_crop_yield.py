from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUTPUT_PATH = DATA_DIR / "demonstracao" / "crop_yield_sintetico.csv"
RANDOM_SEED = 572665


CULTURAS = {
    "Soja": {
        "base": 3.25,
        "precip_media": 4.2,
        "precip_sd": 1.35,
        "temp_media": 25.0,
        "temp_sd": 2.4,
        "ur_media": 66.0,
        "ur_sd": 9.0,
        "umid_esp_media": 15.0,
        "opt_precip": 4.6,
        "opt_temp": 25.0,
        "opt_ur": 68.0,
    },
    "Milho": {
        "base": 6.8,
        "precip_media": 4.8,
        "precip_sd": 1.5,
        "temp_media": 26.4,
        "temp_sd": 2.8,
        "ur_media": 63.0,
        "ur_sd": 10.0,
        "umid_esp_media": 15.8,
        "opt_precip": 5.2,
        "opt_temp": 26.0,
        "opt_ur": 65.0,
    },
    "Trigo": {
        "base": 2.9,
        "precip_media": 3.2,
        "precip_sd": 1.1,
        "temp_media": 20.5,
        "temp_sd": 2.3,
        "ur_media": 60.0,
        "ur_sd": 8.0,
        "umid_esp_media": 10.6,
        "opt_precip": 3.4,
        "opt_temp": 20.0,
        "opt_ur": 60.0,
    },
    "Café": {
        "base": 2.35,
        "precip_media": 3.8,
        "precip_sd": 1.25,
        "temp_media": 22.8,
        "temp_sd": 2.0,
        "ur_media": 70.0,
        "ur_sd": 7.5,
        "umid_esp_media": 13.4,
        "opt_precip": 3.9,
        "opt_temp": 22.5,
        "opt_ur": 70.0,
    },
    "Cana-de-açúcar": {
        "base": 72.0,
        "precip_media": 5.6,
        "precip_sd": 1.7,
        "temp_media": 27.5,
        "temp_sd": 2.4,
        "ur_media": 69.0,
        "ur_sd": 8.5,
        "umid_esp_media": 17.0,
        "opt_precip": 5.8,
        "opt_temp": 27.0,
        "opt_ur": 70.0,
    },
}


def calcular_rendimento(
    cultura: str,
    cfg: dict[str, float],
    precip: float,
    umidade_especifica: float,
    umidade_relativa: float,
    temperatura: float,
    rng: np.random.Generator,
) -> float:
    """Gera rendimento coerente com o cenário climático de cada cultura."""

    escala_cana = 9.5 if cultura == "Cana-de-açúcar" else 1.0
    ganho_chuva = min(precip, cfg["opt_precip"]) * 0.08 * escala_cana
    deficit_chuva = max(0.0, cfg["opt_precip"] - precip) * 0.16 * escala_cana
    excesso_chuva = max(0.0, precip - cfg["opt_precip"] - 1.8) * 0.10 * escala_cana
    penalidade_temp = ((temperatura - cfg["opt_temp"]) ** 2) * 0.025 * escala_cana
    ajuste_umidade = (umidade_relativa - cfg["opt_ur"]) * 0.012 * escala_cana
    ajuste_umidade_especifica = (umidade_especifica - cfg["umid_esp_media"]) * 0.035 * escala_cana
    ruido = rng.normal(0, 0.18 * escala_cana)

    rendimento = (
        cfg["base"]
        + ganho_chuva
        + ajuste_umidade
        + ajuste_umidade_especifica
        - deficit_chuva
        - excesso_chuva
        - penalidade_temp
        + ruido
    )
    return round(max(rendimento, 0.15 * cfg["base"]), 3)


def gerar_dataset(linhas_por_cultura: int = 90) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_SEED)
    registros: list[dict[str, object]] = []

    for cultura, cfg in CULTURAS.items():
        for indice in range(linhas_por_cultura):
            precip = float(np.clip(rng.normal(cfg["precip_media"], cfg["precip_sd"]), 0.0, 12.0))
            temperatura = float(np.clip(rng.normal(cfg["temp_media"], cfg["temp_sd"]), 12.0, 38.0))
            umidade_relativa = float(np.clip(rng.normal(cfg["ur_media"], cfg["ur_sd"]), 28.0, 96.0))
            umidade_especifica = float(
                np.clip(
                    rng.normal(cfg["umid_esp_media"], 1.25)
                    + (temperatura - cfg["temp_media"]) * 0.18
                    + (umidade_relativa - cfg["ur_media"]) * 0.045,
                    4.0,
                    26.0,
                )
            )

            if indice in {8, 39, 72}:
                precip *= 0.18
                umidade_relativa = max(28.0, umidade_relativa - 24.0)
                temperatura = min(38.0, temperatura + 5.5)
            elif indice in {21, 63}:
                precip = min(12.0, precip + 5.5)
                umidade_relativa = min(96.0, umidade_relativa + 18.0)

            rendimento = calcular_rendimento(
                cultura,
                cfg,
                precip,
                umidade_especifica,
                umidade_relativa,
                temperatura,
                rng,
            )

            registros.append(
                {
                    "Cultura": cultura,
                    "Precipitação (mm dia 1)": round(precip, 2),
                    "Umidade específica a 2 metros (g/kg)": round(umidade_especifica, 2),
                    "Umidade relativa a 2 metros (%)": round(umidade_relativa, 2),
                    "Temperatura a 2 metros (ºC)": round(temperatura, 2),
                    "Rendimento": rendimento,
                }
            )

    df = pd.DataFrame(registros)
    return df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = gerar_dataset()
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    print(f"Dataset gerado em: {OUTPUT_PATH}")
    print(f"Linhas: {len(df)} | Culturas: {', '.join(sorted(df['Cultura'].unique()))}")


if __name__ == "__main__":
    main()
