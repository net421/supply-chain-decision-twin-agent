CREATE TABLE IF NOT EXISTS products (
  product_id TEXT PRIMARY KEY,
  product_name TEXT NOT NULL,
  category TEXT NOT NULL,
  unit_cost REAL NOT NULL CHECK (unit_cost >= 0)
);

CREATE TABLE IF NOT EXISTS locations (
  location_id TEXT PRIMARY KEY,
  location_name TEXT NOT NULL,
  region TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS inventory (
  product_id TEXT NOT NULL,
  location_id TEXT NOT NULL,
  inventory_on_hand INTEGER NOT NULL CHECK (inventory_on_hand >= 0),
  inventory_in_transit INTEGER NOT NULL CHECK (inventory_in_transit >= 0),
  PRIMARY KEY (product_id, location_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id),
  FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

CREATE TABLE IF NOT EXISTS demand_forecast (
  product_id TEXT NOT NULL,
  location_id TEXT NOT NULL,
  forecast_date TEXT NOT NULL,
  forecast_units INTEGER NOT NULL CHECK (forecast_units >= 0)
);

-- Compatibility table used by the original Dify demo endpoint.
CREATE TABLE IF NOT EXISTS scenario_results (
  scenario_id TEXT NOT NULL,
  product_id TEXT NOT NULL,
  location_id TEXT NOT NULL,
  projected_inventory INTEGER NOT NULL,
  stockout_risk REAL NOT NULL CHECK (stockout_risk BETWEEN 0 AND 1),
  service_level REAL NOT NULL CHECK (service_level BETWEEN 0 AND 1),
  recommended_action TEXT NOT NULL,
  human_review_required BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS demand_history (
  product_id TEXT NOT NULL,
  location_id TEXT NOT NULL,
  demand_week TEXT NOT NULL,
  actual_units INTEGER NOT NULL CHECK (actual_units >= 0),
  PRIMARY KEY (product_id, location_id, demand_week)
);

CREATE TABLE IF NOT EXISTS supplier_profiles (
  product_id TEXT PRIMARY KEY,
  supplier_id TEXT NOT NULL,
  lead_time_days REAL NOT NULL CHECK (lead_time_days > 0),
  lead_time_stddev_days REAL NOT NULL CHECK (lead_time_stddev_days >= 0),
  supplier_risk REAL NOT NULL CHECK (supplier_risk BETWEEN 0 AND 1),
  expedite_cost_per_unit REAL NOT NULL CHECK (expedite_cost_per_unit >= 0)
);

CREATE TABLE IF NOT EXISTS scenario_definitions (
  scenario_id TEXT PRIMARY KEY,
  description TEXT NOT NULL,
  demand_multiplier REAL NOT NULL CHECK (demand_multiplier > 0),
  lead_time_multiplier REAL NOT NULL CHECK (lead_time_multiplier > 0),
  inbound_availability REAL NOT NULL CHECK (inbound_availability BETWEEN 0 AND 1)
);

CREATE TABLE IF NOT EXISTS decision_twin_runs (
  run_id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  scenario_id TEXT NOT NULL,
  horizon_days INTEGER NOT NULL CHECK (horizon_days > 0),
  product_filter TEXT,
  location_filter TEXT,
  product_location_count INTEGER NOT NULL,
  high_risk_count INTEGER NOT NULL,
  total_incremental_cost REAL NOT NULL,
  average_service_level REAL NOT NULL,
  human_review_required BOOLEAN NOT NULL,
  claim_boundary TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS decision_twin_results (
  run_id TEXT NOT NULL,
  scenario_id TEXT NOT NULL,
  product_id TEXT NOT NULL,
  location_id TEXT NOT NULL,
  forecast_weekly_units REAL NOT NULL,
  projected_demand_units INTEGER NOT NULL,
  available_units_before_action INTEGER NOT NULL,
  baseline_shortage_units INTEGER NOT NULL,
  baseline_service_level REAL NOT NULL,
  baseline_stockout_risk REAL NOT NULL,
  recommended_action TEXT NOT NULL,
  action_units INTEGER NOT NULL,
  incremental_cost REAL NOT NULL,
  projected_inventory_after_action INTEGER NOT NULL,
  service_level_after_action REAL NOT NULL,
  stockout_risk_after_action REAL NOT NULL,
  avoided_shortage_units INTEGER NOT NULL,
  decision_score REAL NOT NULL,
  human_review_required BOOLEAN NOT NULL,
  rationale TEXT NOT NULL,
  PRIMARY KEY (run_id, product_id, location_id),
  FOREIGN KEY (run_id) REFERENCES decision_twin_runs(run_id)
);

CREATE TABLE IF NOT EXISTS decision_twin_action_evaluations (
  run_id TEXT NOT NULL,
  product_id TEXT NOT NULL,
  location_id TEXT NOT NULL,
  action_name TEXT NOT NULL,
  action_units INTEGER NOT NULL,
  incremental_cost REAL NOT NULL,
  projected_inventory INTEGER NOT NULL,
  shortage_units INTEGER NOT NULL,
  service_level REAL NOT NULL,
  stockout_risk REAL NOT NULL,
  decision_score REAL NOT NULL,
  PRIMARY KEY (run_id, product_id, location_id, action_name),
  FOREIGN KEY (run_id) REFERENCES decision_twin_runs(run_id)
);
