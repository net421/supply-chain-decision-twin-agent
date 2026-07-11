# Portfolio Demo: Dify + RAG + Deterministic SQL

This project demonstrates a synthetic/local supply-chain decision-support lab.
It combines Dify orchestration, RAG documentation retrieval, a deterministic
FastAPI SQL backend, and decision-memory records.

It is not a production autonomous AI system. It does not execute purchase
orders, write back to ERP systems, or make operational changes without human
approval.

## What the Demo Shows

- A Dify Chatflow that orchestrates user input, knowledge retrieval, an HTTP
  request to the local SQL API, an LLM response, and the final answer.
- A local FastAPI backend that reads deterministic stockout-risk values from
  SQLite.
- A responsibility split where RAG explains governance and limitations, while
  SQL/backend code provides exact KPI values and recommendations.
- Human-in-the-loop boundaries for operational actions.

## Screenshots

### Dify Studio App List

![Dify Studio apps overview](screenshots/dify-studio-apps-overview.png)

This shows the local Dify Studio workspace with the Supply Chain Decision Twin
Assistant app and related test chatflows.

### Dify Chatflow Orchestration

![Dify chatflow with RAG, HTTP request, LLM, and answer](screenshots/dify-chatflow-http-rag-llm-answer.png)

This shows the configured chatflow:

```text
User Input
  -> Knowledge Retrieval
  -> HTTP Request to local FastAPI SQL endpoint
  -> LLM
  -> Answer
```

The HTTP request node calls the local backend endpoint for high stockout-risk
rows. The LLM should use that API result as the source of truth for exact KPI
values.

## Local Components

### Dify

Dify was run locally with Docker from the official Dify project:

```powershell
cd C:\Users\net42\Desktop\dify\dify\docker
docker compose up -d
```

Local Dify URL:

```text
http://localhost
```

### Supply Chain API

Run the local deterministic SQL API:

```powershell
cd C:\Users\net42\Desktop\supply-chain-decision-twin-agent-starter\supply-chain-decision-twin-agent-starter
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src/create_database.py
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

Useful endpoints:

```text
http://localhost:8000/health
http://localhost:8000/stockout-risks/high
http://localhost:8000/stockout-risks?threshold=0.70
http://localhost:8000/decision-memory
http://localhost:8000/openapi.json
```

When Dify runs in Docker, it should call the host API through:

```text
http://host.docker.internal:8000/openapi.json
```

or, for a direct HTTP request node:

```text
http://host.docker.internal:8000/stockout-risks/high
```

## Demo Question

```text
Which product-location pairs have high stockout risk, and what actions are recommended?
```

## Expected Deterministic API Result

```json
[
  {
    "product_id": "P001",
    "location_id": "L002",
    "stockout_risk": 0.92,
    "inventory_gap": -30,
    "supplier_risk": 0.72,
    "recommended_action": "Expedite replenishment",
    "requires_human_approval": true
  },
  {
    "product_id": "P002",
    "location_id": "L002",
    "stockout_risk": 0.81,
    "inventory_gap": -10,
    "supplier_risk": 0.76,
    "recommended_action": "Review supplier capacity",
    "requires_human_approval": true
  }
]
```

## LLM Responsibility

The LLM should summarize the result and preserve the human-approval boundary.
It should not calculate stockout risk, invent thresholds, or use RAG as the
source of truth for exact numeric KPI values.

The final answer should state:

- This is a synthetic/local decision-support lab.
- The system does not execute purchase orders.
- Human approval is required before operational action.

## Related Dify Notes

See:

- `docs/dify_api_tool_setup.md`
- `dify/workflow_design.md`
- `dify/system_prompt.md`
- `dify/sql_tool_policy.md`
- `dify/memory_tool_policy.md`
