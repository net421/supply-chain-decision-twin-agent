import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils import get_connection, read_sql_file
from src.write_memory import write_decision_memory

QUESTION = "Which SKUs are at stockout risk next week?"

def main():
    sql_query = read_sql_file("sql/queries/stockout_risk.sql")

    conn = get_connection()
    rows = conn.execute(sql_query).fetchall()
    conn.close()

    summary = f"{len(rows)} product-location pairs exceeded the stockout risk threshold."

    recommendation = (
        "Review expedited replenishment or supplier-capacity actions for high-risk product-location pairs."
        if rows else
        "No high-risk stockout pairs found."
    )

    memory_id = write_decision_memory(
        user_question=QUESTION,
        business_decision="Identify product-location pairs requiring replenishment review",
        scenario_id="demand_spike",
        kpi_used="Stockout Risk, Service Level",
        sql_query=sql_query,
        sql_result_summary=summary,
        recommendation=recommendation,
        validation_status="Passed basic KPI threshold validation",
        human_review_required=bool(rows),
        claim_boundary="Synthetic lab decision-support workflow only",
    )

    print(summary)
    print(f"Decision memory written: {memory_id}")
    for row in rows:
        print(row)

if __name__ == "__main__":
    main()
