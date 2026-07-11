# Dify Workflow Design

## Workflow

```text
User Question
  ↓
Classify Intent
  ↓
Retrieve RAG Documentation
  ↓
Check Semantic Contract
  ↓
Generate SQL or Select SQL Query
  ↓
Execute SQL
  ↓
Validate SQL Result
  ↓
Generate Recommendation
  ↓
Write SQL Memory
  ↓
Return Answer with Human Approval and Claim Boundary
```

## Nodes to Create in Dify

1. Start / User Input
2. Knowledge Retrieval
3. Intent Classification
4. SQL Tool Call
5. Validation / Rule Check
6. Response Generator
7. Memory Write Tool
8. Final Answer
