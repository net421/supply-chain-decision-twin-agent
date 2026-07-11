# Quantitative Decision Twin Model

## Purpose

This module extends the preserved Dify + RAG + FastAPI + SQLite demo with a deterministic quantitative decision-support engine. It evaluates inventory exposure under governed scenarios and ranks reviewable actions. It never executes operational actions.

## Inputs

- inventory on hand and in transit by product-location
- eight weeks of synthetic demand history
- unit cost
- supplier lead time, variability, risk and expedite cost
- scenario demand, lead-time and inbound-availability multipliers

## Forecast

The weekly forecast is a four-week weighted moving average with weights `1, 2, 3, 4`, giving greater weight to recent demand. The forecast is deterministic and intentionally simple so reviewers can reproduce it.

## Scenarios

| Scenario | Demand multiplier | Lead-time multiplier | Inbound availability |
| --- | ---: | ---: | ---: |
| baseline | 1.00 | 1.00 | 1.00 |
| demand_spike | 1.35 | 1.00 | 1.00 |
| supplier_delay | 1.00 | 1.60 | 0.35 |
| demand_spike_supplier_delay | 1.35 | 1.60 | 0.35 |

## Candidate actions

- `no_action`
- `expedite_inbound_review`
- `inventory_transfer_review`
- `planned_replenishment_review`

The word `review` is intentional. The engine estimates outcomes and costs but does not modify inventory, place orders or contact suppliers.

## Ranking objective

Each candidate receives a deterministic decision score combining:

- incremental action cost
- shortage units weighted by product cost
- service-level penalty
- stockout-risk penalty

The action with the lowest score is recommended. All candidate evaluations are persisted for auditability.

## Approval boundary

Human review is required whenever the recommended action is not `no_action`, baseline stockout risk is at least `0.70`, or estimated incremental cost is at least `$250`.

## Compatibility

The original Dify endpoint `/stockout-risks/high` and decision-memory endpoints remain unchanged. New capabilities live under `/decision-twin/*`.
