# Supply Chain Decision Twin: Dify + Quantitative Scenario Engine

This repository preserves the original **Dify + RAG + FastAPI + SQLite** portfolio demo and extends it with a deterministic quantitative decision twin for demand forecasting, scenario simulation, action ranking, decision memory and human approval.

It is a synthetic/local decision-support lab. It does not execute purchase orders, inventory transfers or supplier commitments.

## Preserved Dify evidence

The existing local Dify implementation remains the integration core:

```text
Dify Chatflow
  -> Knowledge Retrieval for governance and semantic context
  -> HTTP request to FastAPI
  -> deterministic SQLite evidence
  -> LLM explanation
  -> human approval boundary
```

![Dify Studio apps overview](docs/screenshots/dify-studio-apps-overview.png)

![Dify chatflow with RAG, HTTP request, LLM, and answer](docs/screenshots/dify-chatflow-http-rag-llm-answer.png)

The Dify fork reference used for the local setup is `net421/dify`. See `docs/PORTFOLIO_DEMO.md` for the original screenshot-based walkthrough.

## What was added

The quantitative engine now:

1. forecasts weekly demand with a transparent weighted moving average;
2. evaluates baseline, demand-spike, supplier-delay and combined scenarios;
3. simulates inventory availability across the adjusted lead-time horizon;
4. evaluates no action, expedite, transfer and planned-replenishment review options;
5. ranks alternatives using cost, shortage, service and stockout-risk penalties;
6. persists every candidate evaluation and selected recommendation;
7. preserves a mandatory human-approval and non-execution boundary.

See `docs/DECISION_TWIN_MODEL.md` for formulas, assumptions and governance.

## Architecture

```text
User question
  -> Dify RAG governance context
  -> FastAPI
       -> preserved SQL risk endpoint
       -> demand forecast
       -> scenario simulation
       -> candidate-action evaluation
       -> governed ranking
       -> run and action evidence in SQLite
  -> LLM summary grounded in backend JSON
  -> human-reviewed decision support
```

## API contracts

### Preserved Dify endpoints

```text
GET  /health
GET  /stockout-risks/high
GET  /stockout-risks?threshold=0.70
GET  /decision-memory
POST /decision-memory
```

`GET /stockout-risks/high` retains the exact response used by the original chatflow and screenshots.

### Quantitative decision twin endpoints

```text
GET  /decision-twin/scenarios
GET  /decision-twin/recommendations?scenario_id=baseline
POST /decision-twin/run
GET  /decision-twin/runs/{run_id}
GET  /openapi.json
```

Example run request:

```json
{
  "scenario_id": "demand_spike_supplier_delay",
  "product_id": null,
  "location_id": null,
  "persist": true
}
```

Every response states `executes_operational_actions: false` and includes the claim boundary.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
make verify
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src/create_database.py
python -m validation.validate_decision_twin
python -m pytest -q
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

Run the original Dify-compatible demo:

```bash
make demo
```

Run the combined quantitative scenario:

```bash
make twin
```

## Dify integration

The current chatflow can continue using:

```text
http://host.docker.internal:8000/stockout-risks/high
```

A new HTTP node may call `POST /decision-twin/run`. See `dify/decision_twin_api_contract.md` for the payload, responsibility split and required answer fields.

## Validation evidence

`make verify` performs a clean rebuild and validates:

- preserved legacy Dify API contract;
- source-table counts and constraints;
- four scenario runs across six product-location pairs;
- bounded service and risk metrics;
- scenario monotonicity;
- action-ranking evidence;
- persisted run reconciliation;
- API behavior and refusal boundaries;
- full pytest suite.

Generated evidence is written to `artifacts/` and uploaded by GitHub Actions rather than committed.

## Repository map

```text
src/api.py                         FastAPI contracts for Dify and the twin
src/decision_twin.py               Forecast, simulation and ranking engine
src/run_decision_twin.py           CLI scenario runner
src/create_database.py             Deterministic SQLite rebuild
src/query_stockout_risk.py         Original Dify-compatible SQL demo
src/write_memory.py                Decision-memory writer
sql/                               Operational schema, scenarios and seed data
memory/                            Decision, trace and approval memory
validation/validate_decision_twin.py End-to-end evidence checks
tests/                             Legacy compatibility and twin tests
docs/PORTFOLIO_DEMO.md             Original Dify screenshots and walkthrough
docs/DECISION_TWIN_MODEL.md        Quantitative model and governance
dify/decision_twin_api_contract.md Optional upgraded Dify HTTP node
```

## Claim boundary

This repository demonstrates synthetic/local decision-support patterns. It does not demonstrate production deployment, autonomous purchasing, real supplier recommendations, guaranteed business impact or enterprise implementation.
