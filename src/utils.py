from pathlib import Path
import sqlite3

DB_PATH = Path("data/supply_chain.db")

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def read_sql_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")
