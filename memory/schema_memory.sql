CREATE TABLE IF NOT EXISTS decision_memory (
  memory_id TEXT PRIMARY KEY,
  created_at TIMESTAMP NOT NULL,
  user_question TEXT NOT NULL,
  business_decision TEXT NOT NULL,
  scenario_id TEXT,
  kpi_used TEXT NOT NULL,
  sql_query TEXT NOT NULL,
  sql_result_summary TEXT NOT NULL,
  recommendation TEXT NOT NULL,
  validation_status TEXT NOT NULL,
  human_review_required BOOLEAN NOT NULL,
  approved_by_human BOOLEAN NOT NULL,
  claim_boundary TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_trace (
  trace_id TEXT PRIMARY KEY,
  memory_id TEXT NOT NULL,
  step_name TEXT NOT NULL,
  input_summary TEXT NOT NULL,
  output_summary TEXT NOT NULL,
  validation_passed BOOLEAN NOT NULL,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS approval_memory (
  approval_id TEXT PRIMARY KEY,
  memory_id TEXT NOT NULL,
  approval_status TEXT NOT NULL,
  reviewer_role TEXT,
  approval_notes TEXT,
  created_at TIMESTAMP NOT NULL
);
