# Artifact Inventory — fastapi_transactions

**Summary:** 29 artifacts (class: 4, function: 21, model: 1, service: 1, test: 2)

## Classs

| Name | Source | Detail |
|------|--------|--------|
| `TransactionCreate` | `app/models.py:13` | Python class |
| `Transaction` | `app/models.py:26` | Python class |
| `Balance` | `app/models.py:31` | Python class |
| `TransactionType` | `app/models.py:8` | Python class |

## Functions

| Name | Source | Detail |
|------|--------|--------|
| `serve_ui` | `app/main.py:46` | Python function |
| `create_transaction` | `app/main.py:51` | Python function |
| `list_transactions` | `app/main.py:61` | Python function |
| `get_transaction` | `app/main.py:66` | Python function |
| `get_balance` | `app/main.py:74` | Python function |
| `health` | `app/main.py:85` | Python function |
| `showToast` | `app/static/app.js:29` | JavaScript function |
| `formatAmount` | `app/static/app.js:38` | JavaScript function |
| `fetchJSON` | `app/static/app.js:43` | JavaScript function |
| `renderTransactions` | `app/static/app.js:56` | JavaScript function |
| `escapeHtml` | `app/static/app.js:90` | JavaScript function |
| `loadData` | `app/static/app.js:98` | JavaScript function |
| `reset_store` | `tests/test_main.py:11` | Python function |
| `test_health_check` | `tests/test_main.py:19` | Python function |
| `test_list_transactions_empty` | `tests/test_main.py:25` | Python function |
| `test_create_credit_transaction` | `tests/test_main.py:31` | Python function |
| `test_create_debit_transaction` | `tests/test_main.py:45` | Python function |
| `test_balance_reflects_credits_and_debits` | `tests/test_main.py:54` | Python function |
| `test_rejects_non_positive_amount` | `tests/test_main.py:66` | Python function |
| `test_rejects_invalid_transaction_type` | `tests/test_main.py:74` | Python function |
| `test_get_single_transaction_and_404` | `tests/test_main.py:79` | Python function |

## Models

| Name | Source | Detail |
|------|--------|--------|
| `models.py` | `app/models.py` | data model / schema |

## Services

| Name | Source | Detail |
|------|--------|--------|
| `app.js` | `app/static/app.js` | Node.js process |

## Tests

| Name | Source | Detail |
|------|--------|--------|
| `README.md` | `.pytest_cache/README.md` | test file |
| `test_main.py` | `tests/test_main.py` | test file |
