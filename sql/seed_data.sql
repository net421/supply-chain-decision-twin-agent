INSERT INTO products VALUES
('P001', 'Battery Pack', 'Electronics', 25.0),
('P002', 'Sensor Unit', 'Electronics', 40.0),
('P003', 'Packaging Kit', 'Supplies', 5.0);

INSERT INTO locations VALUES
('L001', 'Dallas DC', 'South'),
('L002', 'Chicago DC', 'Midwest');

INSERT INTO inventory VALUES
('P001', 'L001', 120, 40),
('P001', 'L002', 20, 10),
('P002', 'L001', 80, 20),
('P002', 'L002', 15, 5),
('P003', 'L001', 500, 100);

INSERT INTO scenario_results VALUES
('demand_spike', 'P001', 'L002', -30, 0.92, 0.72, 'Expedite replenishment', 1),
('demand_spike', 'P002', 'L002', -10, 0.81, 0.76, 'Review supplier capacity', 1),
('baseline', 'P003', 'L001', 420, 0.10, 0.98, 'No action required', 0);
