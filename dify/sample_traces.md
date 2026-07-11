# Sample Trace

User question:

```text
Which SKUs are at stockout risk next week and why?
```

Expected trace:

```text
1. Retrieve KPI dictionary.
2. Retrieve semantic contract.
3. Query scenario_results where stockout_risk >= 0.70.
4. Validate risk and service level ranges.
5. Summarize high-risk SKUs.
6. Write decision_memory.
7. Require human approval.
8. Return claim boundary.
```
