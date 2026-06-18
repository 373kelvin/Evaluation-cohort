"""Tests for the FastAPI service using Starlette's TestClient (no live server)."""

from fastapi.testclient import TestClient

from app.main import app, _reset

client = TestClient(app)


def setup_function() -> None:
    # Fresh in-memory store before each test.
    _reset()


def test_ingest_then_appears_in_pending() -> None:
    resp = client.post(
        "/transactions",
        json={"amount": 12000, "currency": "INR", "hour": 3, "country": "RU"},
    )
    assert resp.status_code == 201
    created = resp.json()
    assert created["id"] == 1
    assert created["status"] == "pending"

    pending = client.get("/transactions/pending").json()
    assert len(pending) == 1
    assert pending[0]["id"] == 1


def test_submit_score_marks_scored_and_get_returns_it() -> None:
    client.post(
        "/transactions",
        json={"amount": 12000, "currency": "INR", "hour": 3, "country": "RU"},
    )
    resp = client.post(
        "/transactions/1/score",
        json={"score": 90, "reasons": ["large amount", "unusual hour", "high-risk country"]},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "scored"

    got = client.get("/transactions/1").json()
    assert got["status"] == "scored"
    assert got["score"] == 90
    assert got["reasons"] == ["large amount", "unusual hour", "high-risk country"]
    # It should no longer be pending.
    assert client.get("/transactions/pending").json() == []


def test_invalid_ingest_returns_422() -> None:
    # Negative amount, bad hour, 3-letter country -> validation error.
    resp = client.post(
        "/transactions",
        json={"amount": -5, "currency": "INR", "hour": 99, "country": "XXX"},
    )
    assert resp.status_code == 422


def test_score_unknown_transaction_returns_404() -> None:
    resp = client.post("/transactions/999/score", json={"score": 10, "reasons": []})
    assert resp.status_code == 404
