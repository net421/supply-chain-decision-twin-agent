.PHONY: setup db demo twin validate test verify clean

setup:
	python -m pip install -r requirements.txt

db:
	python src/create_database.py

demo:
	python src/query_stockout_risk.py

twin:
	python -m src.run_decision_twin --scenario demand_spike_supplier_delay

validate:
	python -m validation.validate_decision_twin

test:
	python -m pytest -q

verify: clean db validate test

clean:
	rm -f data/supply_chain.db
	rm -f artifacts/*.json
