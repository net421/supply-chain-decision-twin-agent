import sqlite3
from pathlib import Path
import subprocess
import sys

DB_PATH = Path("data/supply_chain.db")

def ensure_db():
    if not DB_PATH.exists():
        subprocess.run([sys.executable, "src/create_database.py"], check=True)

def test_stockout_risk_between_zero_and_one():
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT stockout_risk FROM scenario_results").fetchall()
    conn.close()

    for (risk,) in rows:
        assert 0 <= risk <= 1

def test_service_level_between_zero_and_one():
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT service_level FROM scenario_results").fetchall()
    conn.close()

    for (service_level,) in rows:
        assert 0 <= service_level <= 1

def test_high_risk_requires_human_review():
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT stockout_risk, human_review_required FROM scenario_results"
    ).fetchall()
    conn.close()

    for risk, review_required in rows:
        if risk >= 0.70:
            assert review_required == 1
