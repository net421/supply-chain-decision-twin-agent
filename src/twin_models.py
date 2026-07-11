from __future__ import annotations

from dataclasses import dataclass

CLAIM_BOUNDARY = (
    "Synthetic/local decision-support only. Recommendations do not execute "
    "purchase orders, transfers, or supplier commitments; human approval is required."
)


@dataclass(frozen=True)
class ActionEvaluation:
    action_name: str
    action_units: int
    incremental_cost: float
    projected_inventory: int
    shortage_units: int
    service_level: float
    stockout_risk: float
    decision_score: float


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def weighted_forecast(values: list[int]) -> float:
    if not values:
        raise ValueError("At least one demand-history value is required.")
    weights = list(range(1, len(values) + 1))
    return sum(value * weight for value, weight in zip(values, weights)) / sum(weights)


def risk_score(
    shortage_units: int,
    projected_demand: int,
    demand_variability: float,
    supplier_risk: float,
    lead_time_multiplier: float,
) -> float:
    shortage_ratio = shortage_units / projected_demand if projected_demand else 0.0
    lead_time_stress = max(lead_time_multiplier - 1.0, 0.0)
    raw = (
        0.02
        + 0.64 * shortage_ratio
        + 0.10 * min(demand_variability, 1.0)
        + 0.14 * supplier_risk
        + 0.10 * min(lead_time_stress, 1.0)
    )
    return round(clamp(raw, 0.0, 0.99), 4)


def evaluate_action(
    *,
    action_name: str,
    action_units: int,
    incremental_cost: float,
    available_before_action: int,
    projected_demand: int,
    unit_cost: float,
    demand_variability: float,
    supplier_risk: float,
    lead_time_multiplier: float,
) -> ActionEvaluation:
    projected_inventory = available_before_action + action_units - projected_demand
    shortage_units = max(-projected_inventory, 0)
    service_level = (
        1.0
        if projected_demand == 0
        else clamp(1.0 - (shortage_units / projected_demand))
    )
    stockout_risk = risk_score(
        shortage_units,
        projected_demand,
        demand_variability,
        supplier_risk,
        lead_time_multiplier,
    )
    shortage_penalty = shortage_units * unit_cost * 4.0
    service_penalty = (1.0 - service_level) * 1500.0
    risk_penalty = stockout_risk * 750.0
    decision_score = round(
        incremental_cost + shortage_penalty + service_penalty + risk_penalty,
        2,
    )
    return ActionEvaluation(
        action_name=action_name,
        action_units=action_units,
        incremental_cost=round(incremental_cost, 2),
        projected_inventory=projected_inventory,
        shortage_units=shortage_units,
        service_level=round(service_level, 4),
        stockout_risk=stockout_risk,
        decision_score=decision_score,
    )
