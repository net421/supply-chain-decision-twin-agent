# Dify Decision Twin API Contract

The original chatflow can continue calling:

```text
GET http://host.docker.internal:8000/stockout-risks/high
```

That response contract is preserved exactly.

## Optional quantitative twin node

A new Dify HTTP Request node may call:

```text
POST http://host.docker.internal:8000/decision-twin/run
Content-Type: application/json
```

Example body:

```json
{
  "scenario_id": "demand_spike_supplier_delay",
  "product_id": null,
  "location_id": null,
  "persist": true
}
```

Use the backend response as the source of truth for forecasts, scenario values, ranked actions, costs and service levels. RAG remains the source for definitions, limitations and approval rules. The LLM may summarize but must not invent values or imply that an action was executed.

## Suggested flow

```text
User Input
  -> Knowledge Retrieval
  -> HTTP Request: POST /decision-twin/run
  -> LLM grounded in returned JSON
  -> Answer with human-approval boundary
```

## Required answer fields

- scenario identifier
- affected product-location pair
- projected demand and available inventory
- baseline shortage and risk
- recommended review action and units
- estimated incremental cost
- expected service level after action
- human-review requirement
- synthetic/local claim boundary
