import pytest
from fastapi.testclient import TestClient

from app import main
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_store():
    """Reset the in-memory transaction store before every test so tests
    don't leak state into one another."""
    main._transactions.clear()
    main._next_id = 1
    yield


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_list_transactions_empty():
    resp = client.get("/transactions")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_credit_transaction():
    resp = client.post(
        "/transactions",
        json={"amount": 100.0, "type": "credit", "description": "Salary"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == 1
    assert body["amount"] == 100.0
    assert body["type"] == "credit"
    assert body["description"] == "Salary"
    assert "created_at" in body


def test_create_debit_transaction():
    resp = client.post(
        "/transactions",
        json={"amount": 40.0, "type": "debit", "description": "Groceries"},
    )
    assert resp.status_code == 201
    assert resp.json()["type"] == "debit"


def test_balance_reflects_credits_and_debits():
    client.post("/transactions", json={"amount": 100.0, "type": "credit"})
    client.post("/transactions", json={"amount": 30.0, "type": "debit"})
    client.post("/transactions", json={"amount": 20.0, "type": "credit"})

    resp = client.get("/balance")
    assert resp.status_code == 200
    body = resp.json()
    assert body["balance"] == 90.0
    assert body["transaction_count"] == 3


def test_rejects_non_positive_amount():
    resp = client.post("/transactions", json={"amount": 0, "type": "credit"})
    assert resp.status_code == 422

    resp = client.post("/transactions", json={"amount": -5, "type": "debit"})
    assert resp.status_code == 422


def test_rejects_invalid_transaction_type():
    resp = client.post("/transactions", json={"amount": 10, "type": "deposit"})
    assert resp.status_code == 422


def test_get_single_transaction_and_404():
    create_resp = client.post("/transactions", json={"amount": 50.0, "type": "credit"})
    txn_id = create_resp.json()["id"]

    resp = client.get(f"/transactions/{txn_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == txn_id

    missing_resp = client.get("/transactions/9999")
    assert missing_resp.status_code == 404
