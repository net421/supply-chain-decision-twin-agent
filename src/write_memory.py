import uuid
from datetime import datetime
from src.utils import get_connection

def write_decision_memory(
    user_question: str,
    business_decision: str,
    scenario_id: str,
    kpi_used: str,
    sql_query: str,
    sql_result_summary: str,
    recommendation: str,
    validation_status: str,
    human_review_required: bool,
    claim_boundary: str,
):
    memory_id = f"mem_{uuid.uuid4().hex[:8]}"
    trace_id = f"trace_{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow().isoformat()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO decision_memory VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            memory_id,
            now,
            user_question,
            business_decision,
            scenario_id,
            kpi_used,
            sql_query.strip(),
            sql_result_summary,
            recommendation,
            validation_status,
            int(human_review_required),
            0,
            claim_boundary,
        ),
    )

    cur.execute(
        """
        INSERT INTO agent_trace VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            trace_id,
            memory_id,
            "write_decision_memory",
            user_question,
            sql_result_summary,
            1,
            now,
        ),
    )

    conn.commit()
    conn.close()

    return memory_id
