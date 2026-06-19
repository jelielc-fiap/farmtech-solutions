from __future__ import annotations

import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "farmtech_fase4.db"
SCHEMA_PATH = BASE_DIR / "sql" / "schema_sqlite.sql"


def criar_banco(db_path: Path = DB_PATH) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    return db_path


if __name__ == "__main__":
    caminho = criar_banco()
    print(f"Banco SQLite preparado em: {caminho}")
