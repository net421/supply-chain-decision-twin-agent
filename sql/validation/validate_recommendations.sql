SELECT *
FROM scenario_results
WHERE stockout_risk >= 0.70
  AND human_review_required <> 1;
