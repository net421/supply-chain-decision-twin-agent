from pathlib import Path
import subprocess
import sys
import sqlite3

DB_PATH = Path("data/supply_chain.db")

def test_decision_memory_table_exists_after_db_creation():
    subprocess.run([sys.executable, "src/create_database.py"], check=True)
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='decision_memory'"
    ).fetchall()
    conn.close()

    assert len(rows) == 1

def test_demo_writes_decision_memory():
    subprocess.run([sys.executable, "src/create_database.py"], check=True)
    subprocess.run([sys.executable, "src/query_stockout_risk.py"], check=True)

    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM decision_memory").fetchone()[0]
    conn.close()

    assert count >= 1
