from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd


matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"

HORAS_MES = 730
ARMAZENAMENTO_GB = 50


REGIOES = [
    {
        "regiao": "Norte da Virgínia",
        "codigo": "us-east-1",
        "instancia": "t3.micro",
        "vcpu": 2,
        "memoria_gib": 1,
        "rede": "Até 5 Gigabit",
        "ec2_usd_hora": 0.0104,
        "ebs_magnetico_usd_gb_mes": 0.0500,
        "fonte": "AWS Pricing Calculator; capturas fornecidas pelo aluno",
    },
    {
        "regiao": "São Paulo",
        "codigo": "sa-east-1",
        "instancia": "t3.micro",
        "vcpu": 2,
        "memoria_gib": 1,
        "rede": "Até 5 Gigabit",
        "ec2_usd_hora": 0.0168,
        "ebs_magnetico_usd_gb_mes": 0.1200,
        "fonte": "AWS Pricing Calculator; capturas fornecidas pelo aluno",
    },
]


def gerar_tabela() -> pd.DataFrame:
    df = pd.DataFrame(REGIOES)
    df["horas_mes"] = HORAS_MES
    df["armazenamento_gb"] = ARMAZENAMENTO_GB
    df["custo_ec2_mes_usd"] = df["ec2_usd_hora"] * HORAS_MES
    df["custo_ebs_mes_usd"] = df["ebs_magnetico_usd_gb_mes"] * ARMAZENAMENTO_GB
    df["custo_total_mes_usd"] = df["custo_ec2_mes_usd"] + df["custo_ebs_mes_usd"]
    df["diferenca_vs_menor_usd"] = df["custo_total_mes_usd"] - df["custo_total_mes_usd"].min()
    return df


def gerar_grafico(df: pd.DataFrame) -> None:
    cores = ["#2f855a", "#b7791f"]
    fig, ax = plt.subplots(figsize=(9, 5.2))
    barras = ax.bar(df["regiao"], df["custo_total_mes_usd"], color=cores, width=0.55)
    ax.set_title("Estimativa mensal AWS: EC2 t3.micro + EBS magnético 50 GB")
    ax.set_ylabel("Custo mensal estimado (USD)")
    ax.set_xlabel("Região")
    ax.grid(axis="y", alpha=0.25)

    for barra, valor in zip(barras, df["custo_total_mes_usd"]):
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height() + 0.35,
            f"US$ {valor:.2f}",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "comparativo_custos_aws.png", dpi=170)
    plt.close(fig)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = gerar_tabela()
    df.to_csv(DATA_DIR / "aws_cost_estimate.csv", index=False, encoding="utf-8")
    gerar_grafico(df)

    print("Comparativo AWS gerado.")
    print(df[["regiao", "codigo", "instancia", "custo_total_mes_usd"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
