SELECT *
FROM scenario_results
WHERE stockout_risk < 0
   OR stockout_risk > 1
   OR service_level < 0
   OR service_level > 1;
