"""Automated end-to-end integration test (Rust engine <-> FastAPI service).

Drives the full contract the same way the Node worker does, but in one
scripted Python process:

  ingest -> read pending -> run the REAL Rust binary on the txn ->
  submit the score -> assert the transaction is now `scored` with score 90.

Skips (not fails) if the Rust binary hasn't been built yet, with a hint.
Run:  pytest -q integration/test_integration.py   (from the project root)
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
SERVICE_DIR = ROOT / "service"
sys.path.insert(0, str(SERVICE_DIR))

from app.main import app, _reset  # noqa: E402


def _engine_path() -> Path | None:
    """Return the built Rust binary path, or None if it isn't there."""
    base = ROOT / "engine" / "target" / "release"
    for name in ("engine", "engine.exe"):
        candidate = base / name
        if candidate.exists():
            return candidate
    return None


def test_end_to_end_rust_and_service() -> None:
    engine = _engine_path()
    if engine is None:
        pytest.skip(
            "Rust engine not built. Run: cd engine && cargo build --release"
        )

    _reset()
    client = TestClient(app)

    # 1. Ingest the brief's example transaction.
    created = client.post(
        "/transactions",
        json={"amount": 12000, "currency": "INR", "hour": 3, "country": "RU"},
    ).json()
    txn_id = created["id"]

    # 2. Read it off the pending list (what the worker polls).
    pending = client.get("/transactions/pending").json()
    assert len(pending) == 1
    txn = pending[0]

    # 3. Run the real Rust engine on it (JSON over stdin/stdout).
    proc = subprocess.run(
        [str(engine)],
        input=json.dumps(txn),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    score = json.loads(proc.stdout)
    assert score["score"] == 90
    assert score["reasons"] == ["large amount", "unusual hour", "high-risk country"]

    # 4. Submit the score back.
    client.post(f"/transactions/{txn_id}/score", json=score)

    # 5. The transaction is now scored.
    final = client.get(f"/transactions/{txn_id}").json()
    assert final["status"] == "scored"
    assert final["score"] == 90
