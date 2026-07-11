from __future__ import annotations

import math
import uuid
from statistics import fmean
from typing import Any

from src.twin_models import CLAIM_BOUNDARY, ActionEvaluation, evaluate_action
from src.twin_repository import load_inputs, persist_run


def transfer_capacity(
    inputs: dict[tuple[str, str], dict[str, Any]],
    product_id: str,
    location_id: str,
) -> int:
    capacity = 0
    for (other_product, other_location), item in inputs.items():
        if other_product != product_id or other_location == location_id:
            continue
        protected_demand = math.ceil(item["forecast_weekly_units"] * 1.5)
        capacity += max(item["inventory_on_hand"] - protected_demand, 0)
    return capacity


def build_recommendation(
    *,
    item: dict[str, Any],
    scenario: dict[str, Any],
    inputs: dict[tuple[str, str], dict[str, Any]],
) -> tuple[dict[str, Any], list[ActionEvaluation]]:
    horizon_days = max(7, math.ceil(item["lead_time_days"] * scenario["lead_time_multiplier"]))
    horizon_weeks = max(1, math.ceil(horizon_days / 7))
    projected_demand = math.ceil(
        item["forecast_weekly_units"] * horizon_weeks * scenario["demand_multiplier"]
    )
    inbound_available = math.floor(
        item["inventory_in_transit"] * scenario["inbound_availability"]
    )
    available_before_action = item["inventory_on_hand"] + inbound_available
    baseline_shortage = max(projected_demand - available_before_action, 0)

    common = {
        "available_before_action": available_before_action,
        "projected_demand": projected_demand,
        "unit_cost": item["unit_cost"],
        "demand_variability": item["demand_variability"],
        "supplier_risk": item["supplier_risk"],
        "lead_time_multiplier": scenario["lead_time_multiplier"],
    }
    actions = [
        evaluate_action(
            action_name="no_action", action_units=0, incremental_cost=0.0, **common
        )
    ]

    missing_inbound = max(item["inventory_in_transit"] - inbound_available, 0)
    expedite_units = min(baseline_shortage, missing_inbound)
    if expedite_units > 0:
        actions.append(
            evaluate_action(
                action_name="expedite_inbound_review",
                action_units=expedite_units,
                incremental_cost=expedite_units * item["expedite_cost_per_unit"],
                **common,
            )
        )

    transfer_units = min(
        baseline_shortage,
        transfer_capacity(inputs, item["product_id"], item["location_id"]),
        50,
    )
    if transfer_units > 0:
        actions.append(
            evaluate_action(
                action_name="inventory_transfer_review",
                action_units=transfer_units,
                incremental_cost=transfer_units * 2.50,
                **common,
            )
        )

    if baseline_shortage > 0:
        replenishment_units = baseline_shortage + math.ceil(
            item["forecast_weekly_units"] * 0.25
        )
        actions.append(
            evaluate_action(
                action_name="planned_replenishment_review",
                action_units=replenishment_units,
                incremental_cost=replenishment_units * item["unit_cost"] * 0.08,
                **common,
            )
        )

    best = min(actions, key=lambda action: (action.decision_score, action.incremental_cost))
    baseline = next(action for action in actions if action.action_name == "no_action")
    avoided_shortage = max(baseline.shortage_units - best.shortage_units, 0)
    human_review_required = (
        best.action_name != "no_action"
        or baseline.stockout_risk >= 0.70
        or best.incremental_cost >= 250.0
    )
    recommendation = {
        "product_id": item["product_id"],
        "location_id": item["location_id"],
        "forecast_weekly_units": round(item["forecast_weekly_units"], 2),
        "horizon_days": horizon_days,
        "projected_demand_units": projected_demand,
        "available_units_before_action": available_before_action,
        "baseline_shortage_units": baseline.shortage_units,
        "baseline_service_level": baseline.service_level,
        "baseline_stockout_risk": baseline.stockout_risk,
        "recommended_action": best.action_name,
        "action_units": best.action_units,
        "incremental_cost": best.incremental_cost,
        "projected_inventory_after_action": best.projected_inventory,
        "service_level_after_action": best.service_level,
        "stockout_risk_after_action": best.stockout_risk,
        "avoided_shortage_units": avoided_shortage,
        "decision_score": best.decision_score,
        "human_review_required": human_review_required,
        "rationale": (
            f"{best.action_name} has the lowest governed decision score "
            f"({best.decision_score:.2f}) across {len(actions)} evaluated actions; "
            f"it avoids {avoided_shortage} shortage units."
        ),
    }
    return recommendation, actions


def run_decision_twin(
    scenario_id: str,
    *,
    product_id: str | None = None,
    location_id: str | None = None,
    persist: bool = True,
) -> dict[str, Any]:
    inputs, scenarios = load_inputs()
    if scenario_id not in scenarios:
        raise ValueError(
            f"Unknown scenario_id '{scenario_id}'. Allowed: {', '.join(sorted(scenarios))}"
        )
    scenario = scenarios[scenario_id]
    recommendations: list[dict[str, Any]] = []
    all_actions: dict[tuple[str, str], list[ActionEvaluation]] = {}

    for (item_product, item_location), item in inputs.items():
        if product_id and item_product != product_id:
            continue
        if location_id and item_location != location_id:
            continue
        recommendation, actions = build_recommendation(
            item=item, scenario=scenario, inputs=inputs
        )
        recommendations.append(recommendation)
        all_actions[(item_product, item_location)] = actions

    if not recommendations:
        raise ValueError("No product-location pairs matched the requested filters.")

    result = {
        "run_id": f"run_{uuid.uuid4().hex[:12]}",
        "scenario_id": scenario_id,
        "scenario_description": scenario["description"],
        "horizon_days": max(row["horizon_days"] for row in recommendations),
        "product_filter": product_id,
        "location_filter": location_id,
        "product_location_count": len(recommendations),
        "high_risk_count": sum(
            row["baseline_stockout_risk"] >= 0.70 for row in recommendations
        ),
        "total_incremental_cost": round(
            sum(row["incremental_cost"] for row in recommendations), 2
        ),
        "average_service_level": round(
            fmean(row["service_level_after_action"] for row in recommendations), 4
        ),
        "human_review_required": any(
            row["human_review_required"] for row in recommendations
        ),
        "executes_operational_actions": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "recommendations": recommendations,
    }
    if persist:
        persist_run(result, all_actions)
    return result
