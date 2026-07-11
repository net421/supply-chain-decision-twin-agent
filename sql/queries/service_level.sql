SELECT
  scenario_id,
  product_id,
  location_id,
  service_level
FROM scenario_results
ORDER BY service_level ASC;
