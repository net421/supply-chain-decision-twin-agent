import subprocess
import sys

from src.decision_twin import (
    get_action_evaluations,
    get_persisted_run,
    list_scenarios,
    run_decision_twin,
)


def setup_module():
    subprocess.run([sys.executable, "src/create_database.py"], check=True)


def _index(result):
    return {
        (row["product_id"], row["location_id"]): row
        for row in result["recommendations"]
    }


def test_scenario_catalog_is_complete():
    ids = [row["scenario_id"] for row in list_scenarios()]
    assert ids == [
        "baseline",
        "demand_spike",
        "supplier_delay",
        "demand_spike_supplier_delay",
    ]


def test_forecast_and_non_persistent_run_are_deterministic():
    first = run_decision_twin("baseline", persist=False)
    second = run_decision_twin("baseline", persist=False)
    first.pop("run_id")
    second.pop("run_id")
    assert first == second


def test_combined_scenario_is_more_stressful_than_baseline():
    baseline = _index(run_decision_twin("baseline", persist=False))
    combined = _index(
        run_decision_twin("demand_spike_supplier_delay", persist=False)
    )
    for key in baseline:
        assert combined[key]["projected_demand_units"] >= baseline[key]["projected_demand_units"]
        assert combined[key]["available_units_before_action"] <= baseline[key]["available_units_before_action"]
        assert combined[key]["baseline_stockout_risk"] >= baseline[key]["baseline_stockout_risk"]


def test_ranked_recommendation_is_minimum_score_candidate():
    result = run_decision_twin("demand_spike_supplier_delay", persist=True)
    evaluations = get_action_evaluations(result["run_id"])
    by_pair = {}
    for row in evaluations:
        by_pair.setdefault((row["product_id"], row["location_id"]), []).append(row)
    for recommendation in result["recommendations"]:
        key = (recommendation["product_id"], recommendation["location_id"])
        minimum = min(by_pair[key], key=lambda row: (row["decision_score"], row["incremental_cost"]))
        assert recommendation["recommended_action"] == minimum["action_name"]
        assert recommendation["decision_score"] == minimum["decision_score"]


def test_persisted_run_reconciles_to_returned_summary():
    result = run_decision_twin("supplier_delay", persist=True)
    persisted = get_persisted_run(result["run_id"])
    assert persisted is not None
    assert persisted["scenario_id"] == result["scenario_id"]
    assert persisted["product_location_count"] == len(persisted["recommendations"])
    assert round(sum(row["incremental_cost"] for row in persisted["recommendations"]), 2) == persisted["total_incremental_cost"]


def test_filters_limit_scope_without_changing_safety_boundary():
    result = run_decision_twin(
        "demand_spike_supplier_delay",
        product_id="P001",
        location_id="L002",
        persist=False,
    )
    assert result["product_location_count"] == 1
    assert result["recommendations"][0]["product_id"] == "P001"
    assert result["recommendations"][0]["location_id"] == "L002"
    assert result["executes_operational_actions"] is False
    assert "human approval" in result["claim_boundary"].lower()
