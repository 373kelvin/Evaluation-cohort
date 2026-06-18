"""FastAPI ingestion service + in-memory message bus.

A transaction is POSTed here, stored as `pending`, and exposed on
GET /transactions/pending. The Node worker polls that list, gets a score
from the Rust engine, and POSTs it back to /transactions/{id}/score, which
flips the status to `scored`. No DB/Redis — state lives in a plain dict.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Fraud-Score Service")

# ---------------------------------------------------------------------------
# Models (Pydantic does the validation; bad input -> 422 automatically)
# ---------------------------------------------------------------------------


class TransactionIn(BaseModel):
    """What a client sends to create a transaction."""

    amount: float = Field(gt=0)              # must be positive
    currency: str = Field(min_length=1)      # non-empty, e.g. "INR"
    hour: int = Field(ge=0, le=23)           # 0-23
    country: str = Field(min_length=2, max_length=2)  # 2-letter code

    @field_validator("country")
    @classmethod
    def upper_country(cls, v: str) -> str:
        # Normalize so "in" and "IN" score the same in the Rust allowlist.
        return v.upper()


class Score(BaseModel):
    """What the worker submits after the Rust engine scores a txn."""

    score: int = Field(ge=0, le=100)
    reasons: list[str]


# ---------------------------------------------------------------------------
# In-memory store
# ---------------------------------------------------------------------------

_transactions: dict[int, dict] = {}
_next_id = 1


def _reset() -> None:
    """Clear state — used by tests to isolate cases."""
    global _transactions, _next_id
    _transactions = {}
    _next_id = 1


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.post("/transactions", status_code=201)
def create_transaction(txn: TransactionIn) -> dict:
    """Validate + store as pending, assign id, return it."""
    global _next_id
    record = {
        "id": _next_id,
        "amount": txn.amount,
        "currency": txn.currency,
        "hour": txn.hour,
        "country": txn.country,
        "status": "pending",
        "score": None,
        "reasons": None,
    }
    _transactions[_next_id] = record
    _next_id += 1
    return record


@app.get("/transactions/pending")
def list_pending() -> list[dict]:
    """List all pending transactions (the worker polls this)."""
    return [t for t in _transactions.values() if t["status"] == "pending"]


@app.post("/transactions/{txn_id}/score")
def submit_score(txn_id: int, score: Score) -> dict:
    """Attach {score, reasons}, set status to scored."""
    txn = _transactions.get(txn_id)
    if txn is None:
        raise HTTPException(status_code=404, detail="transaction not found")
    txn["score"] = score.score
    txn["reasons"] = score.reasons
    txn["status"] = "scored"
    return txn


@app.get("/transactions/{txn_id}")
def get_transaction(txn_id: int) -> dict:
    """Return the transaction, including score if scored."""
    txn = _transactions.get(txn_id)
    if txn is None:
        raise HTTPException(status_code=404, detail="transaction not found")
    return txn
