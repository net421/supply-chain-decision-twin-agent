from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from src.decision_twin import get_persisted_run, list_scenarios, run_decision_twin
from src.utils import get_connection
from src.write_memory import write_decision_memory

DEFAULT_HIGH_RISK_THRESHOLD = 0.70

app = FastAPI(
    title="Supply Chain Decision Twin API",
    description=(
        "Synthetic/local decision-support API combining the preserved Dify SQL demo "
        "with deterministic forecasting, scenario simulation, action ranking, and "
        "human approval boundaries. It does not execute purchase orders."
    ),
    version="0.2.0",
)


class DecisionMemoryCreate(BaseModel):
    user_question: str
    business_decision: str = "Review high stockout risk product-location pairs"
    scenario_id: str = "demand_spike"
    kpi_used: str = "Stockout Risk, Inventory Gap, Supplier Risk"
    sql_query: str = "API-generated deterministic SQL query"
    sql_result_summary: str
    recommendation: str
    validation_status: str = "Passed API request validation"
    human_review_required: bool = True
    claim_boundary: str = "Synthetic/local decision-support lab only"


class DecisionTwinRunCreate(BaseModel):
    scenario_id: str = Field(default="demand_spike_supplier_delay")
    product_id: str | None = None
    location_id: str | None = None
    persist: bool = True


def _row_to_stockout_risk(row: Any) -> dict[str, Any]:
    return {
        "product_id": row[0],
        "location_id": row[1],
        "stockout_risk": row[2],
        "inventory_gap": row[3],
        "supplier_risk": row[4],
        "recommended_action": row[5],
        "requires_human_approval": bool(row[6]),
    }


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "project": "supply-chain-decision-twin-agent",
        "mode": "synthetic/local decision-support lab",
        "version": app.version,
        "executes_purchase_orders": False,
        "human_approval_required": True,
        "capabilities": [
            "dify_rag_api_orchestration",
            "deterministic_sql_evidence",
            "demand_forecast",
            "scenario_simulation",
            "action_ranking",
            "decision_memory",
        ],
    }


# Preserved compatibility endpoint used by the existing Dify chatflow.
@app.get("/stockout-risks")
def stockout_risks(
    threshold: float = Query(
        DEFAULT_HIGH_RISK_THRESHOLD,
        ge=0.0,
        le=1.0,
        description="Deterministic backend threshold for stockout_risk.",
    )
) -> list[dict[str, Any]]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT
              product_id,
              location_id,
              stockout_risk,
              projected_inventory AS inventory_gap,
              service_level AS supplier_risk,
              recommended_action,
              human_review_required
            FROM scenario_results
            WHERE stockout_risk >= ?
            ORDER BY stockout_risk DESC
            """,
            (threshold,),
        ).fetchall()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        conn.close()

    return [_row_to_stockout_risk(row) for row in rows]


@app.get("/stockout-risks/high")
def high_stockout_risks() -> list[dict[str, Any]]:
    return stockout_risks(DEFAULT_HIGH_RISK_THRESHOLD)


@app.get("/decision-twin/scenarios")
def decision_twin_scenarios() -> list[dict[str, Any]]:
    return list_scenarios()


@app.get("/decision-twin/recommendations")
def decision_twin_recommendations(
    scenario_id: str = "demand_spike_supplier_delay",
    product_id: str | None = None,
    location_id: str | None = None,
) -> dict[str, Any]:
    try:
        return run_decision_twin(
            scenario_id,
            product_id=product_id,
            location_id=location_id,
            persist=False,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/decision-twin/run", status_code=201)
def create_decision_twin_run(payload: DecisionTwinRunCreate) -> dict[str, Any]:
    try:
        return run_decision_twin(
            payload.scenario_id,
            product_id=payload.product_id,
            location_id=payload.location_id,
            persist=payload.persist,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/decision-twin/runs/{run_id}")
def read_decision_twin_run(run_id: str) -> dict[str, Any]:
    result = get_persisted_run(run_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Decision twin run not found")
    return result


@app.get("/decision-memory")
def decision_memory() -> list[dict[str, Any]]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT
              memory_id,
              created_at,
              user_question,
              business_decision,
              scenario_id,
              kpi_used,
              sql_result_summary,
              recommendation,
              validation_status,
              human_review_required,
              approved_by_human,
              claim_boundary
            FROM decision_memory
            ORDER BY created_at DESC
            """
        ).fetchall()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        conn.close()

    return [
        {
            "memory_id": row[0],
            "created_at": row[1],
            "user_question": row[2],
            "business_decision": row[3],
            "scenario_id": row[4],
            "kpi_used": row[5],
            "sql_result_summary": row[6],
            "recommendation": row[7],
            "validation_status": row[8],
            "human_review_required": bool(row[9]),
            "approved_by_human": bool(row[10]),
            "claim_boundary": row[11],
        }
        for row in rows
    ]


@app.post("/decision-memory", status_code=201)
def create_decision_memory(payload: DecisionMemoryCreate) -> dict[str, Any]:
    memory_id = write_decision_memory(
        user_question=payload.user_question,
        business_decision=payload.business_decision,
        scenario_id=payload.scenario_id,
        kpi_used=payload.kpi_used,
        sql_query=payload.sql_query,
        sql_result_summary=payload.sql_result_summary,
        recommendation=payload.recommendation,
        validation_status=payload.validation_status,
        human_review_required=payload.human_review_required,
        claim_boundary=payload.claim_boundary,
    )

    return {
        "memory_id": memory_id,
        "human_review_required": payload.human_review_required,
        "approved_by_human": False,
        "claim_boundary": payload.claim_boundary,
    }
