"""Importa o arquivo do portal informado pelo usuário e preserva a versão anterior."""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from dataset import BASE_DIR, DATA_PATH, ORIGEM_PATH, ler_csv, sha256


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("arquivo", type=Path, help="Caminho do crop_yield.csv original baixado do portal FIAP")
    args = parser.parse_args()
    origem = args.arquivo.resolve()
    _, df, qualidade = ler_csv(origem)
    # Impede que a antiga demonstração seja rotulada como arquivo do portal.
    from gerar_crop_yield import gerar_dataset
    import pandas as pd
    if pd.read_csv(origem).equals(gerar_dataset()):
        raise ValueError("Este é o CSV sintético do projeto. Baixe o arquivo oficial do portal.")
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DATA_PATH.exists() and sha256(DATA_PATH) != sha256(origem):
        arquivo_backup = BASE_DIR / "data" / "historico" / f"crop_yield_{sha256(DATA_PATH)[:12]}.csv"
        arquivo_backup.parent.mkdir(exist_ok=True)
        if not arquivo_backup.exists():
            shutil.copy2(DATA_PATH, arquivo_backup)
    if origem != DATA_PATH.resolve():
        shutil.copy2(origem, DATA_PATH)
    registro = {
        "tipo": "portal_fiap", "descricao": "Arquivo baixado do portal FIAP e fornecido pelo aluno",
        "arquivo_original": origem.name, "importado_em_utc": datetime.now(timezone.utc).isoformat(),
        "sha256": sha256(DATA_PATH), "linhas_originais": qualidade["linhas_originais"],
        "linhas_validas_unicas": len(df),
    }
    ORIGEM_PATH.write_text(json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"CSV importado sem alterar seu conteúdo: {len(df)} linhas válidas. Execute run_entrega1_ml.bat.")


if __name__ == "__main__":
    main()
