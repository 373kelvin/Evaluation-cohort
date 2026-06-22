from pathlib import Path
from threading import Lock
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.models import Balance, Transaction, TransactionCreate, TransactionType

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="Transactions Service",
    description="A small service for recording transactions and tracking balance.",
    version="1.0.0",
)

# In-memory map keyed by transaction id. A Lock guards against race conditions
# if requests are handled concurrently (FastAPI can run sync code in a threadpool).
_lock = Lock()
_transactions: Dict[int, Transaction] = {}
_next_id = 1


def _seed_dummy_data() -> None:
    global _next_id
    dummy_rows = [
        {"amount": 500.0, "type": TransactionType.credit, "description": "Opening balance"},
        {"amount": 75.5, "type": TransactionType.debit, "description": "Coffee shop"},
        {"amount": 1200.0, "type": TransactionType.credit, "description": "Freelance payment"},
        {"amount": 200.0, "type": TransactionType.debit, "description": "Electric bill"},
    ]
    for row in dummy_rows:
        txn = Transaction(id=_next_id, **row)
        _transactions[_next_id] = txn
        _next_id += 1


_seed_dummy_data()

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def serve_ui() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/transactions", response_model=Transaction, status_code=201)
def create_transaction(payload: TransactionCreate) -> Transaction:
    global _next_id
    with _lock:
        txn = Transaction(id=_next_id, **payload.model_dump())
        _transactions[_next_id] = txn
        _next_id += 1
    return txn


@app.get("/transactions", response_model=List[Transaction])
def list_transactions() -> List[Transaction]:
    return list(_transactions.values())


@app.get("/transactions/{transaction_id}", response_model=Transaction)
def get_transaction(transaction_id: int) -> Transaction:
    txn = _transactions.get(transaction_id)
    if txn is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn


@app.get("/balance", response_model=Balance)
def get_balance() -> Balance:
    total = 0.0
    for txn in _transactions.values():
        if txn.type == TransactionType.credit:
            total += txn.amount
        else:
            total -= txn.amount
    return Balance(balance=round(total, 2), transaction_count=len(_transactions))


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
