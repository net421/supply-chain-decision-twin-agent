from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from statistics import fmean, pstdev
from typing import Any

from src.twin_models import ActionEvaluation, weighted_forecast
from src.utils import get_connection


def list_scenarios() -> list[dict[str, Any]]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT scenario_id, description, demand_multiplier,
                   lead_time_multiplier, inbound_availability
            FROM scenario_definitions
            ORDER BY CASE scenario_id
                WHEN 'baseline' THEN 1
                WHEN 'demand_spike' THEN 2
                WHEN 'supplier_delay' THEN 3
                ELSE 4
            END
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def load_inputs() -> tuple[dict[tuple[str, str], dict[str, Any]], dict[str, dict[str, Any]]]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        inventory_rows = conn.execute(
            """
            SELECT i.product_id, i.location_id, p.unit_cost,
                   i.inventory_on_hand, i.inventory_in_transit,
                   s.lead_time_days, s.lead_time_stddev_days,
                   s.supplier_risk, s.expedite_cost_per_unit
            FROM inventory i
            JOIN products p USING (product_id)
            JOIN supplier_profiles s USING (product_id)
            ORDER BY i.product_id, i.location_id
            """
        ).fetchall()
        scenario_rows = conn.execute("SELECT * FROM scenario_definitions").fetchall()
        inputs: dict[tuple[str, str], dict[str, Any]] = {}
        for row in inventory_rows:
            history = conn.execute(
                """
                SELECT actual_units FROM demand_history
                WHERE product_id = ? AND location_id = ?
                ORDER BY demand_week
                """,
                (row["product_id"], row["location_id"]),
            ).fetchall()
            values = [int(item["actual_units"]) for item in history]
            if len(values) < 4:
                raise ValueError(
                    f"Insufficient demand history for {row['product_id']}-{row['location_id']}"
                )
            mean = fmean(values[-8:])
            inputs[(row["product_id"], row["location_id"])] = {
                **dict(row),
                "history": values,
                "forecast_weekly_units": weighted_forecast(values[-4:]),
                "demand_variability": pstdev(values[-8:]) / mean if mean else 0.0,
            }
        scenarios = {row["scenario_id"]: dict(row) for row in scenario_rows}
        return inputs, scenarios
    finally:
        conn.close()


def persist_run(
    result: dict[str, Any],
    all_actions: dict[tuple[str, str], list[ActionEvaluation]],
) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO decision_twin_runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                result["run_id"], datetime.now(timezone.utc).isoformat(),
                result["scenario_id"], result["horizon_days"],
                result["product_filter"], result["location_filter"],
                result["product_location_count"], result["high_risk_count"],
                result["total_incremental_cost"], result["average_service_level"],
                int(result["human_review_required"]), result["claim_boundary"],
            ),
        )
        for recommendation in result["recommendations"]:
            conn.execute(
                """
                INSERT INTO decision_twin_results VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    result["run_id"], result["scenario_id"],
                    recommendation["product_id"], recommendation["location_id"],
                    recommendation["forecast_weekly_units"],
                    recommendation["projected_demand_units"],
                    recommendation["available_units_before_action"],
                    recommendation["baseline_shortage_units"],
                    recommendation["baseline_service_level"],
                    recommendation["baseline_stockout_risk"],
                    recommendation["recommended_action"], recommendation["action_units"],
                    recommendation["incremental_cost"],
                    recommendation["projected_inventory_after_action"],
                    recommendation["service_level_after_action"],
                    recommendation["stockout_risk_after_action"],
                    recommendation["avoided_shortage_units"], recommendation["decision_score"],
                    int(recommendation["human_review_required"]), recommendation["rationale"],
                ),
            )
            key = (recommendation["product_id"], recommendation["location_id"])
            for action in all_actions[key]:
                conn.execute(
                    "INSERT INTO decision_twin_action_evaluations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        result["run_id"], recommendation["product_id"],
                        recommendation["location_id"], action.action_name,
                        action.action_units, action.incremental_cost,
                        action.projected_inventory, action.shortage_units,
                        action.service_level, action.stockout_risk, action.decision_score,
                    ),
                )
        conn.commit()
    finally:
        conn.close()


def get_persisted_run(run_id: str) -> dict[str, Any] | None:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        run = conn.execute(
            "SELECT * FROM decision_twin_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        if run is None:
            return None
        rows = conn.execute(
            "SELECT * FROM decision_twin_results WHERE run_id = ? ORDER BY product_id, location_id",
            (run_id,),
        ).fetchall()
        payload = dict(run)
        payload["human_review_required"] = bool(payload["human_review_required"])
        payload["executes_operational_actions"] = False
        payload["recommendations"] = []
        for row in rows:
            item = dict(row)
            item["human_review_required"] = bool(item["human_review_required"])
            payload["recommendations"].append(item)
        return payload
    finally:
        conn.close()


def get_action_evaluations(run_id: str) -> list[dict[str, Any]]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT * FROM decision_twin_action_evaluations
            WHERE run_id = ?
            ORDER BY product_id, location_id, decision_score, action_name
            """,
            (run_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
