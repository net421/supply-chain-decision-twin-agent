SELECT
  trace_id,
  memory_id,
  step_name,
  input_summary,
  output_summary,
  validation_passed,
  created_at
FROM agent_trace
ORDER BY created_at ASC;
