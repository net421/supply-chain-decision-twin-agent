# Dify API Tool Setup

This project uses Dify for orchestration and explanation, but exact stockout
risk values come from the local FastAPI backend and SQLite.

## 1. Run the local API

From Windows PowerShell in the repository:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src/create_database.py
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

Check these URLs in your browser:

```text
http://localhost:8000/health
http://localhost:8000/stockout-risks/high
http://localhost:8000/openapi.json
```

## 2. Add the API tool in Dify

Because Dify runs in Docker, use this OpenAPI URL:

```text
http://host.docker.internal:8000/openapi.json
```

Do not use `http://localhost:8000/openapi.json` inside Dify Docker.

In Dify:

1. Open the workspace tools or tool/provider area.
2. Add a custom API tool from an OpenAPI schema.
3. Paste `http://host.docker.internal:8000/openapi.json`.
4. Save the tool.
5. Confirm Dify shows operations for:
   - `GET /health`
   - `GET /stockout-risks/high`
   - `GET /stockout-risks`
   - `GET /decision-memory`
   - `POST /decision-memory`

## 3. Connect the tool in the Chatflow

Use this practical flow:

```text
User Input
  -> Knowledge Retrieval
  -> API Tool: GET /stockout-risks/high
  -> LLM
  -> Answer
```

Use `GET /stockout-risks/high` for the demo question.

## 4. LLM prompt

Use a prompt like this in the LLM node:

```text
You are a supply chain decision-support assistant for a synthetic/local lab.

Use the Knowledge Retrieval context only for documentation, limitations,
semantic contract, claim boundaries, and human approval rules.

Use the API tool result as the source of truth for exact stockout_risk,
inventory_gap, supplier_risk, recommended_action, and
requires_human_approval values.

Do not calculate or invent KPI values. Do not use RAG to determine numeric
thresholds. Do not claim this is a production autonomous AI system.

Answer the user's question clearly. Include each high-risk product-location
pair, its exact KPI values, the recommended action, and whether human approval
is required.

Always state:
- This is a synthetic/local decision-support lab.
- The system does not execute purchase orders.
- Human approval is required before operational action.
```

## 5. Demo question

Ask:

```text
Which product-location pairs have high stockout risk, and what actions are recommended?
```

## 6. Expected successful answer

A successful answer should include:

- `P001-L002`
  - `stockout_risk`: `0.92`
  - `inventory_gap`: `-30`
  - `supplier_risk`: `0.72`
  - `recommended_action`: `Expedite replenishment`
  - `requires_human_approval`: `true`

- `P002-L002`
  - `stockout_risk`: `0.81`
  - `inventory_gap`: `-10`
  - `supplier_risk`: `0.76`
  - `recommended_action`: `Review supplier capacity`
  - `requires_human_approval`: `true`

The final answer must also say that this is a synthetic/local
decision-support lab, the system does not execute purchase orders, and human
approval is required before operational action.
