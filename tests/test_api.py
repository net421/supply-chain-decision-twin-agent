import subprocess
import sys

from fastapi.testclient import TestClient

from src.api import app


client = TestClient(app)


def setup_module():
    subprocess.run([sys.executable, "src/create_database.py"], check=True)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["executes_purchase_orders"] is False
    assert body["human_approval_required"] is True


def test_high_stockout_risks_returns_expected_rows():
    response = client.get("/stockout-risks/high")

    assert response.status_code == 200
    rows = response.json()
    assert rows == [
        {
            "product_id": "P001",
            "location_id": "L002",
            "stockout_risk": 0.92,
            "inventory_gap": -30,
            "supplier_risk": 0.72,
            "recommended_action": "Expedite replenishment",
            "requires_human_approval": True,
        },
        {
            "product_id": "P002",
            "location_id": "L002",
            "stockout_risk": 0.81,
            "inventory_gap": -10,
            "supplier_risk": 0.76,
            "recommended_action": "Review supplier capacity",
            "requires_human_approval": True,
        },
    ]


def test_stockout_risks_threshold_filter():
    response = client.get("/stockout-risks?threshold=0.90")

    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 1
    assert rows[0]["product_id"] == "P001"
    assert rows[0]["stockout_risk"] == 0.92


def test_decision_memory_create_and_read():
    create_response = client.post(
        "/decision-memory",
        json={
            "user_question": "Which product-location pairs have high stockout risk?",
            "sql_result_summary": "2 product-location pairs exceeded the stockout risk threshold.",
            "recommendation": "Review expedited replenishment or supplier-capacity actions.",
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["memory_id"].startswith("mem_")
    assert created["human_review_required"] is True

    read_response = client.get("/decision-memory")
    assert read_response.status_code == 200
    rows = read_response.json()
    assert any(row["memory_id"] == created["memory_id"] for row in rows)
