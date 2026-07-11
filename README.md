# Supply Chain Decision Twin Agent

## Executive Summary

This repository is a starter template for a **synthetic supply chain decision-support lab** using:

- governed supply chain KPIs,
- SQL operational data,
- SQL memory for decision traces,
- Dify RAG workflow documentation,
- validation checks,
- human approval checkpoints,
- safe claim boundaries.

The project is designed to demonstrate an AI-native analytics workflow without claiming production deployment or autonomous supply chain execution.

## Business Problem

Supply chain teams need to identify product-location pairs at risk of stockout, understand the KPIs behind the risk, review recommended actions, and preserve a traceable decision record.

## Architecture

```text
Synthetic Supply Chain Data
        ↓
SQL Operational Layer
        ↓
Governed KPI Dictionary + Semantic Contract
        ↓
Dify RAG Workflow
        ↓
SQL Query / Scenario Retrieval
        ↓
SQL Memory Layer
        ↓
Validation Checks
        ↓
Human Approval
        ↓
Decision-Support Recommendation
```

## What This Repository Demonstrates

- Supply Chain Decision Intelligence
- Semantic BI and governed KPI definitions
- SQL operational analytics
- SQL memory for decision traces
- RAG-ready documentation for Dify
- Dify Chatflow orchestration with RAG + deterministic HTTP/SQL backend
- Human-validated AI workflow
- Reproducible validation and claim boundaries

## Portfolio Demo Evidence

See [docs/PORTFOLIO_DEMO.md](docs/PORTFOLIO_DEMO.md) for screenshots and a
practical walkthrough of the local Dify configuration:

- Dify Studio app overview
- Chatflow with User Input, Knowledge Retrieval, HTTP Request, LLM, and Answer
- local FastAPI endpoint used for deterministic SQL results
- demo question and expected answer

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python src/create_database.py
python src/query_stockout_risk.py
pytest
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src/create_database.py
$env:PYTHONPATH=(Get-Location).Path
python -m src.query_stockout_risk
python -m pytest
```

## Local FastAPI Backend for Dify

Run the deterministic SQL API:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src/create_database.py
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

Useful local URLs:

```text
http://localhost:8000/health
http://localhost:8000/stockout-risks/high
http://localhost:8000/stockout-risks?threshold=0.70
http://localhost:8000/decision-memory
http://localhost:8000/openapi.json
```

Dify runs in Docker, so configure the API tool with:

```text
http://host.docker.internal:8000/openapi.json
```

Use `GET /stockout-risks/high` for the demo question:

```text
Which product-location pairs have high stockout risk, and what actions are recommended?
```

## Dify Setup

See:

```text
START_HERE_ES.md
dify/workflow_design.md
dify/system_prompt.md
dify/rag_sources.md
dify/sql_tool_policy.md
dify/memory_tool_policy.md
docs/dify_api_tool_setup.md
```

Dify was run locally from the official open-source project. The related fork
used for reference is:

```text
https://github.com/net421/dify
```

## Dify + SQL Responsibility Split

RAG is used for:

- project documentation,
- semantic contract,
- glossary,
- limitations,
- claim boundaries,
- human approval rules.

SQL/API is used for:

- exact KPI values,
- deterministic thresholds,
- stockout risk rows,
- inventory gap,
- supplier risk,
- recommended action,
- decision memory.

The LLM is used for:

- final explanation,
- summarization,
- decision-support wording,
- human approval framing.

## Claim Boundary

This repository demonstrates a **synthetic/local decision-support workflow**.

It does **not** demonstrate:

- production deployment,
- autonomous purchasing,
- real supplier recommendations,
- guaranteed business impact,
- enterprise implementation.
