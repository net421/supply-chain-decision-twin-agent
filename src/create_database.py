import sqlite3
from pathlib import Path

DB_PATH = Path("data/supply_chain.db")

def create_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for path in ["sql/schema_operational.sql", "memory/schema_memory.sql"]:
        cur.executescript(Path(path).read_text(encoding="utf-8"))

    cur.executescript(Path("sql/seed_data.sql").read_text(encoding="utf-8"))

    conn.commit()
    conn.close()
    print(f"Database created at {DB_PATH}")

if __name__ == "__main__":
    create_database()
