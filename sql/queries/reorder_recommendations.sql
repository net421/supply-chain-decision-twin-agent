SELECT
  scenario_id,
  product_id,
  location_id,
  recommended_action,
  human_review_required
FROM scenario_results
WHERE recommended_action <> 'No action required';
