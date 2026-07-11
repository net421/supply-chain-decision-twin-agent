CREATE TABLE IF NOT EXISTS products (
  product_id TEXT PRIMARY KEY,
  product_name TEXT NOT NULL,
  category TEXT NOT NULL,
  unit_cost REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS locations (
  location_id TEXT PRIMARY KEY,
  location_name TEXT NOT NULL,
  region TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS inventory (
  product_id TEXT NOT NULL,
  location_id TEXT NOT NULL,
  inventory_on_hand INTEGER NOT NULL,
  inventory_in_transit INTEGER NOT NULL,
  PRIMARY KEY (product_id, location_id)
);

CREATE TABLE IF NOT EXISTS demand_forecast (
  product_id TEXT NOT NULL,
  location_id TEXT NOT NULL,
  forecast_date TEXT NOT NULL,
  forecast_units INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS scenario_results (
  scenario_id TEXT NOT NULL,
  product_id TEXT NOT NULL,
  location_id TEXT NOT NULL,
  projected_inventory INTEGER NOT NULL,
  stockout_risk REAL NOT NULL,
  service_level REAL NOT NULL,
  recommended_action TEXT NOT NULL,
  human_review_required BOOLEAN NOT NULL
);
