SELECT
  product_id,
  location_id,
  stockout_risk,
  projected_inventory,
  service_level,
  recommended_action,
  human_review_required
FROM scenario_results
WHERE stockout_risk >= 0.70
ORDER BY stockout_risk DESC;
