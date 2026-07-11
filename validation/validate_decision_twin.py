import json
from pathlib import Path

from fastapi.testclient import TestClient

from src.api import app
from src.create_database import create_database
from src.decision_twin import get_action_evaluations, get_persisted_run, run_decision_twin
from src.utils import get_connection

ARTIFACT_DIR = Path("artifacts")


def validate() -> dict:
    create_database()
    checks: list[dict] = []

    def record(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})
        if not passed:
            raise AssertionError(f"{name}: {detail}")

    conn = get_connection()
    try:
        for table, expected in [
            ("products", 3),
            ("locations", 2),
            ("inventory", 6),
            ("demand_history", 48),
            ("supplier_profiles", 3),
            ("scenario_definitions", 4),
        ]:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            record(f"source_{table}_count", count == expected, f"count={count}")
    finally:
        conn.close()

    client = TestClient(app)
    legacy = client.get("/stockout-risks/high")
    record("legacy_dify_endpoint_status", legacy.status_code == 200, f"status={legacy.status_code}")
    record("legacy_dify_endpoint_rows", len(legacy.json()) == 2, f"rows={len(legacy.json())}")

    scenario_results = {}
    for scenario_id in [
        "baseline",
        "demand_spike",
        "supplier_delay",
        "demand_spike_supplier_delay",
    ]:
        result = run_decision_twin(scenario_id, persist=True)
        scenario_results[scenario_id] = result
        record(
            f"{scenario_id}_coverage",
            result["product_location_count"] == 6,
            f"pairs={result['product_location_count']}",
        )
        record(
            f"{scenario_id}_service_range",
            all(0 <= row["service_level_after_action"] <= 1 for row in result["recommendations"]),
            "service levels are bounded",
        )
        record(
            f"{scenario_id}_risk_range",
            all(0 <= row["stockout_risk_after_action"] <= 1 for row in result["recommendations"]),
            "risk scores are bounded",
        )
        persisted = get_persisted_run(result["run_id"])
        record(
            f"{scenario_id}_persistence",
            persisted is not None and len(persisted["recommendations"]) == 6,
            f"run_id={result['run_id']}",
        )
        evaluations = get_action_evaluations(result["run_id"])
        record(
            f"{scenario_id}_action_evidence",
            len(evaluations) >= 6,
            f"evaluations={len(evaluations)}",
        )

    baseline = {
        (row["product_id"], row["location_id"]): row
        for row in scenario_results["baseline"]["recommendations"]
    }
    combined = {
        (row["product_id"], row["location_id"]): row
        for row in scenario_results["demand_spike_supplier_delay"]["recommendations"]
    }
    record(
        "combined_demand_dominates_baseline",
        all(combined[key]["projected_demand_units"] >= baseline[key]["projected_demand_units"] for key in baseline),
        "combined scenario demand is never below baseline",
    )
    record(
        "combined_inbound_not_above_baseline",
        all(combined[key]["available_units_before_action"] <= baseline[key]["available_units_before_action"] for key in baseline),
        "supplier delay never increases available inventory",
    )
    record(
        "no_autonomous_execution",
        all(not result["executes_operational_actions"] for result in scenario_results.values()),
        "all runs are decision-support only",
    )

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {
        "status": "passed",
        "checks_passed": len(checks),
        "scenario_count": len(scenario_results),
        "product_location_pairs": 6,
        "checks": checks,
        "runs": {
            key: {
                "run_id": value["run_id"],
                "high_risk_count": value["high_risk_count"],
                "total_incremental_cost": value["total_incremental_cost"],
                "average_service_level": value["average_service_level"],
            }
            for key, value in scenario_results.items()
        },
    }
    (ARTIFACT_DIR / "decision_twin_validation.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    (ARTIFACT_DIR / "combined_scenario_recommendations.json").write_text(
        json.dumps(
            scenario_results["demand_spike_supplier_delay"],
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    (ARTIFACT_DIR / "openapi.json").write_text(
        json.dumps(app.openapi(), indent=2, sort_keys=True), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True))
