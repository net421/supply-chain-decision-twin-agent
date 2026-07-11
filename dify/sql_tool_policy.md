# SQL Tool Policy

The SQL tool may query:

- products
- locations
- inventory
- demand_forecast
- scenario_results

The SQL tool must not:

- modify operational data,
- execute external actions,
- invent KPIs,
- ignore validation rules.

Recommended MVP query:

```sql
SELECT
  product_id,
  location_id,
  stockout_risk,
  projected_inventory,
  service_level,
  recommended_action,
  human_review_required
FROM scenario_results
WHERE stockout_risk >= 0.70;
```
