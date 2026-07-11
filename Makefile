.PHONY: setup db demo test clean

setup:
	pip install -r requirements.txt

db:
	python src/create_database.py

demo:
	python src/query_stockout_risk.py

test:
	pytest

clean:
	rm -f data/supply_chain.db
