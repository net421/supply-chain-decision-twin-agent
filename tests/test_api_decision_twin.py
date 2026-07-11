import subprocess
import sys

from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


def setup_module():
    subprocess.run([sys.executable, "src/create_database.py"], check=True)


def test_scenarios_endpoint():
    response = client.get("/decision-twin/scenarios")
    assert response.status_code == 200
    assert len(response.json()) == 4


def test_run_and_read_decision_twin_endpoint():
    create = client.post(
        "/decision-twin/run",
        json={"scenario_id": "demand_spike_supplier_delay", "persist": True},
    )
    assert create.status_code == 201
    result = create.json()
    assert result["product_location_count"] == 6
    assert result["executes_operational_actions"] is False
    assert result["human_review_required"] is True

    read = client.get(f"/decision-twin/runs/{result['run_id']}")
    assert read.status_code == 200
    assert read.json()["run_id"] == result["run_id"]


def test_invalid_scenario_returns_422():
    response = client.post(
        "/decision-twin/run", json={"scenario_id": "invented_scenario"}
    )
    assert response.status_code == 422
    assert "Unknown scenario_id" in response.json()["detail"]


def test_recommendations_endpoint_does_not_persist():
    response = client.get(
        "/decision-twin/recommendations?scenario_id=baseline&product_id=P003"
    )
    assert response.status_code == 200
    body = response.json()
    assert body["product_location_count"] == 2
    assert body["executes_operational_actions"] is False
