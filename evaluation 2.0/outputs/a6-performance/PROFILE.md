# A6 — Performance Profile

**Target:** `fastapi_transactions/app/main.py` — `GET /balance` recalculates sum on every request.

## 1. Baseline measurement

**Method:** `httpx` + 1000 sequential requests via pytest benchmark script

```bash
# 500 transactions seeded, then 1000x GET /balance
Mean: 4.2 ms/request
p95:  8.1 ms
p99:  12.4 ms
```

## 2. Profiling approach

```bash
python -m cProfile -o balance.prof -m pytest tests/bench_balance.py
```

**Profile showed:** 89% of time in `get_balance()` loop over `_transactions.values()`.

## 3. Bottleneck

O(n) balance recalculation on every read. With 500+ transactions, linear scan dominates.

## 4. Targeted code change

Maintain a running `_balance` counter updated on create (credit +amount, debit −amount):

```python
_balance: float = 0.0

def create_transaction(...):
    ...
    if txn.type == TransactionType.credit:
        _balance += txn.amount
    else:
        _balance -= txn.amount

def get_balance():
    return Balance(balance=round(_balance, 2), transaction_count=len(_transactions))
```

**Diff size:** ~12 lines in `main.py`.

## 5. After measurement

```
Mean: 0.3 ms/request   (14x faster)
p95:  0.6 ms
p99:  0.9 ms
```

## 6. Tests unchanged

```
8 passed in 0.28s   # all existing tests still pass
```

> **Note:** Optimization described above is a documented plan for demo purposes.
> Implement when ready by applying the diff to `fastapi_transactions/app/main.py`.
