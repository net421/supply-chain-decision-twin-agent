# Decision Traceability Record

## Example Decision

Business decision:

```text
Should product P001 be expedited to location L002?
```

Governed KPIs:

- Stockout Risk
- Service Level
- Projected Inventory

Scenario:

```text
Demand spike
```

Recommendation:

```text
Review expedited replenishment.
```

Evidence:

- `sql/queries/stockout_risk.sql`
- `reports/scenario_results.md`
- `reports/validation_report.md`

Human approval:

```text
Required before any operational action.
```

Claim boundary:

```text
Synthetic lab decision-support workflow only.
```
