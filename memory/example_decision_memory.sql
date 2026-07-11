SELECT
  memory_id,
  created_at,
  user_question,
  business_decision,
  kpi_used,
  recommendation,
  validation_status,
  human_review_required,
  approved_by_human,
  claim_boundary
FROM decision_memory
ORDER BY created_at DESC;
