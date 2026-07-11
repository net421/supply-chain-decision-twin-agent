"""
Local agentic analytics workflow placeholder.

This module documents the intended local workflow:

1. Plan the analysis.
2. Retrieve governed KPI definitions through RAG/Dify.
3. Query SQL operational data.
4. Validate SQL results.
5. Generate a recommendation.
6. Write SQL memory.
7. Require human approval when needed.

Dify should perform the orchestration; this file exists so the repo has a clear
code-side representation of the agentic workflow pattern.
"""

AGENT_WORKFLOW_STEPS = [
    "plan",
    "retrieve_semantic_context",
    "query_operational_sql",
    "validate_results",
    "generate_recommendation",
    "write_sql_memory",
    "require_human_approval",
]
