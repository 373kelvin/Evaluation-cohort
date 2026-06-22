# Artifact Inventory — fraud-score-system

**Summary:** 23 artifacts (class: 2, config: 2, function: 15, service: 1, test: 3)

## Classs

| Name | Source | Detail |
|------|--------|--------|
| `TransactionIn` | `service/app/main.py:19` | Python class |
| `Score` | `service/app/main.py:34` | Python class |

## Configs

| Name | Source | Detail |
|------|--------|--------|
| `conftest.py` | `service/conftest.py` | configuration file |
| `package.json` | `worker/package.json` | configuration file |

## Functions

| Name | Source | Detail |
|------|--------|--------|
| `test_end_to_end_rust_and_service` | `integration/test_integration.py:38` | Python function |
| `health` | `service/app/main.py:108` | Python function |
| `create_transaction` | `service/app/main.py:62` | Python function |
| `list_pending` | `service/app/main.py:81` | Python function |
| `submit_score` | `service/app/main.py:87` | Python function |
| `get_transaction` | `service/app/main.py:99` | Python function |
| `setup_function` | `service/tests/test_service.py:10` | Python function |
| `test_ingest_then_appears_in_pending` | `service/tests/test_service.py:15` | Python function |
| `test_submit_score_marks_scored_and_get_returns_it` | `service/tests/test_service.py:30` | Python function |
| `test_invalid_ingest_returns_422` | `service/tests/test_service.py:50` | Python function |
| `test_score_unknown_transaction_returns_404` | `service/tests/test_service.py:59` | Python function |
| `sleep` | `worker/worker.js:21` | JavaScript function |
| `scoreTransaction` | `worker/worker.js:24` | JavaScript function |
| `processOne` | `worker/worker.js:65` | JavaScript function |
| `main` | `worker/worker.js:79` | JavaScript function |

## Services

| Name | Source | Detail |
|------|--------|--------|
| `worker.js` | `worker/worker.js` | Node.js process |

## Tests

| Name | Source | Detail |
|------|--------|--------|
| `test_integration.py` | `integration/test_integration.py` | test file |
| `conftest.py` | `service/conftest.py` | test file |
| `test_service.py` | `service/tests/test_service.py` | test file |
