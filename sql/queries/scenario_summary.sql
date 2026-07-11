SELECT
  scenario_id,
  COUNT(*) AS rows_evaluated,
  SUM(CASE WHEN stockout_risk >= 0.70 THEN 1 ELSE 0 END) AS high_risk_count,
  SUM(CASE WHEN human_review_required THEN 1 ELSE 0 END) AS human_review_count
FROM scenario_results
GROUP BY scenario_id;
