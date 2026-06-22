# Artifact Inventory — evaluation 2.0

**Summary:** 192 artifacts (class: 27, config: 3, function: 148, model: 5, service: 4, test: 5)

## Classs

| Name | Source | Detail |
|------|--------|--------|
| `Artifact` | `Project-based-entity-diagrams/insight/artifacts.py:23` | Python class |
| `Inventory` | `Project-based-entity-diagrams/insight/artifacts.py:31` | Python class |
| `Table` | `Project-based-entity-diagrams/insight/model.py:17` | Python class |
| `Relationship` | `Project-based-entity-diagrams/insight/model.py:29` | Python class |
| `Feature` | `Project-based-entity-diagrams/insight/model.py:38` | Python class |
| `Project` | `Project-based-entity-diagrams/insight/model.py:48` | Python class |
| `Column` | `Project-based-entity-diagrams/insight/model.py:7` | Python class |
| `TransactionCreate` | `fastapi_transactions/app/models.py:13` | Python class |
| `Transaction` | `fastapi_transactions/app/models.py:26` | Python class |
| `Balance` | `fastapi_transactions/app/models.py:31` | Python class |
| `TransactionType` | `fastapi_transactions/app/models.py:8` | Python class |
| `TransactionIn` | `fraud-score-system/service/app/main.py:19` | Python class |
| `Score` | `fraud-score-system/service/app/main.py:34` | Python class |
| `UserCreate` | `sample-projects/fintech-platform/app/models.py:15` | Python class |
| `User` | `sample-projects/fintech-platform/app/models.py:20` | Python class |
| `Account` | `sample-projects/fintech-platform/app/models.py:27` | Python class |
| `TransactionType` | `sample-projects/fintech-platform/app/models.py:34` | Python class |
| `TransactionCreate` | `sample-projects/fintech-platform/app/models.py:40` | Python class |
| `FraudAlert` | `sample-projects/fintech-platform/app/models.py:47` | Python class |
| `KycStatus` | `sample-projects/fintech-platform/app/models.py:9` | Python class |
| `AccountRepository` | `sample-projects/fintech-platform/app/repositories.py:15` | Python class |
| `TransactionRepository` | `sample-projects/fintech-platform/app/repositories.py:24` | Python class |
| `FraudRepository` | `sample-projects/fintech-platform/app/repositories.py:34` | Python class |
| `UserRepository` | `sample-projects/fintech-platform/app/repositories.py:5` | Python class |
| `PaymentService` | `sample-projects/fintech-platform/app/services.py:14` | Python class |
| `ReportingService` | `sample-projects/fintech-platform/app/services.py:31` | Python class |
| `AuthService` | `sample-projects/fintech-platform/app/services.py:6` | Python class |

## Configs

| Name | Source | Detail |
|------|--------|--------|
| `conftest.py` | `fraud-score-system/service/conftest.py` | configuration file |
| `package.json` | `fraud-score-system/worker/package.json` | configuration file |
| `package.json` | `sample-projects/fintech-platform/package.json` | configuration file |

## Functions

| Name | Source | Detail |
|------|--------|--------|
| `main` | `Project-based-entity-diagrams/analyze.py:32` | Python function |
| `detect` | `Project-based-entity-diagrams/insight/artifacts.py:45` | Python function |
| `to_markdown` | `Project-based-entity-diagrams/insight/artifacts.py:98` | Python function |
| `analyze_design` | `Project-based-entity-diagrams/insight/design.py:115` | Python function |
| `build_architecture` | `Project-based-entity-diagrams/insight/design.py:22` | Python function |
| `build_execution` | `Project-based-entity-diagrams/insight/design.py:62` | Python function |
| `build_components` | `Project-based-entity-diagrams/insight/design.py:97` | Python function |
| `find_smells` | `Project-based-entity-diagrams/insight/features.py:130` | Python function |
| `detect` | `Project-based-entity-diagrams/insight/features.py:56` | Python function |
| `render` | `Project-based-entity-diagrams/insight/render.py:48` | Python function |
| `iter_files` | `Project-based-entity-diagrams/insight/scan.py:15` | Python function |
| `read` | `Project-based-entity-diagrams/insight/scan.py:27` | Python function |
| `infer_pks` | `Project-based-entity-diagrams/insight/schema.py:136` | Python function |
| `relationships_from_ddl` | `Project-based-entity-diagrams/insight/schema.py:151` | Python function |
| `relationships_inferred` | `Project-based-entity-diagrams/insight/schema.py:162` | Python function |
| `analyze_schema` | `Project-based-entity-diagrams/insight/schema.py:184` | Python function |
| `parse_ddl` | `Project-based-entity-diagrams/insight/schema.py:38` | Python function |
| `infer_from_queries` | `Project-based-entity-diagrams/insight/schema.py:98` | Python function |
| `detect` | `Project-based-entity-diagrams/insight/stack.py:26` | Python function |
| `main` | `Project-based-entity-diagrams/inventory.py:14` | Python function |
| `chat` | `dashboard/ai_chat.py:101` | Python function |
| `narrate_demo_start` | `dashboard/ai_chat.py:173` | Python function |
| `narrate_demo_results` | `dashboard/ai_chat.py:180` | Python function |
| `project_room` | `dashboard/app.py:223` | Python function |
| `project_detail` | `dashboard/app.py:230` | Python function |
| `get_config` | `dashboard/app.py:246` | Python function |
| `open_service` | `dashboard/app.py:252` | Python function |
| `project_capabilities` | `dashboard/app.py:273` | Python function |
| `index` | `dashboard/app.py:292` | Python function |
| `overview` | `dashboard/app.py:297` | Python function |
| `projects_health` | `dashboard/app.py:312` | Python function |
| `ping` | `dashboard/app.py:323` | Python function |
| `demo_tests` | `dashboard/app.py:328` | Python function |
| `ai_demo_start` | `dashboard/app.py:356` | Python function |
| `run_tests` | `dashboard/app.py:371` | Python function |
| `run_inventory` | `dashboard/app.py:382` | Python function |
| `run_analyze` | `dashboard/app.py:401` | Python function |
| `list_outputs` | `dashboard/app.py:419` | Python function |
| `get_report` | `dashboard/app.py:429` | Python function |
| `recent_logs` | `dashboard/app.py:442` | Python function |
| `run_fastapi_tx_demo` | `dashboard/demo_tests.py:114` | Python function |
| `run_fraud_score_demo` | `dashboard/demo_tests.py:222` | Python function |
| `run_fintech_demo` | `dashboard/demo_tests.py:299` | Python function |
| `run_demo_tests` | `dashboard/demo_tests.py:366` | Python function |
| `run_entity_diagrams_demo` | `dashboard/demo_tests.py:63` | Python function |
| `base_url` | `dashboard/service_urls.py:45` | Python function |
| `health_url` | `dashboard/service_urls.py:52` | Python function |
| `resolve_open_url` | `dashboard/service_urls.py:57` | Python function |
| `open_buttons` | `dashboard/service_urls.py:66` | Python function |
| `deployment_config` | `dashboard/service_urls.py:88` | Python function |
| `mdLite` | `dashboard/static/ai-chat.js:10` | JavaScript function |
| `esc` | `dashboard/static/ai-chat.js:3` | JavaScript function |
| `_statusBlock` | `dashboard/static/ai-knowledge.js:63` | JavaScript function |
| `_isProjectQuestion` | `dashboard/static/ai-knowledge.js:73` | JavaScript function |
| `setProgress` | `dashboard/static/app.js:102` | JavaScript function |
| `initTheme` | `dashboard/static/app.js:112` | JavaScript function |
| `toggleTheme` | `dashboard/static/app.js:117` | JavaScript function |
| `log` | `dashboard/static/app.js:124` | JavaScript function |
| `renderDemoInGuide` | `dashboard/static/app.js:147` | JavaScript function |
| `runWalkthrough` | `dashboard/static/app.js:151` | JavaScript function |
| `runQuickDemo` | `dashboard/static/app.js:172` | JavaScript function |
| `runDemoTests` | `dashboard/static/app.js:190` | JavaScript function |
| `showGuide` | `dashboard/static/app.js:194` | JavaScript function |
| `showCapabilities` | `dashboard/static/app.js:199` | JavaScript function |
| `fetchJson` | `dashboard/static/app.js:21` | JavaScript function |
| `renderProjects` | `dashboard/static/app.js:219` | JavaScript function |
| `renderAgents` | `dashboard/static/app.js:275` | JavaScript function |
| `renderOutputs` | `dashboard/static/app.js:287` | JavaScript function |
| `hideLoader` | `dashboard/static/app.js:3` | JavaScript function |
| `loadHealth` | `dashboard/static/app.js:300` | JavaScript function |
| `load` | `dashboard/static/app.js:313` | JavaScript function |
| `postJson` | `dashboard/static/app.js:33` | JavaScript function |
| `post` | `dashboard/static/app.js:342` | JavaScript function |
| `runInventory` | `dashboard/static/app.js:364` | JavaScript function |
| `runAnalyze` | `dashboard/static/app.js:365` | JavaScript function |
| `initProjectAI` | `dashboard/static/app.js:54` | JavaScript function |
| `renderDemoResultsPanel` | `dashboard/static/app.js:66` | JavaScript function |
| `showError` | `dashboard/static/app.js:8` | JavaScript function |
| `formatDemoResults` | `dashboard/static/app.js:91` | JavaScript function |
| `statusLabel` | `dashboard/static/app.js:98` | JavaScript function |
| `humanIntro` | `dashboard/static/demo-walkthrough.js:15` | JavaScript function |
| `sleep` | `dashboard/static/demo-walkthrough.js:5` | JavaScript function |
| `esc` | `dashboard/static/demo-walkthrough.js:9` | JavaScript function |
| `renderGuide` | `dashboard/static/hub.js:11` | JavaScript function |
| `init` | `dashboard/static/hub.js:127` | JavaScript function |
| `runAction` | `dashboard/static/hub.js:38` | JavaScript function |
| `statusBadge` | `dashboard/static/hub.js:5` | JavaScript function |
| `showCapabilities` | `dashboard/static/hub.js:59` | JavaScript function |
| `renderCards` | `dashboard/static/hub.js:82` | JavaScript function |
| `initGuideChat` | `dashboard/static/project.js:103` | JavaScript function |
| `initTheme` | `dashboard/static/project.js:11` | JavaScript function |
| `init` | `dashboard/static/project.js:114` | JavaScript function |
| `toggleTheme` | `dashboard/static/project.js:16` | JavaScript function |
| `setButtonsBusy` | `dashboard/static/project.js:22` | JavaScript function |
| `renderQuickResults` | `dashboard/static/project.js:29` | JavaScript function |
| `runWalkthrough` | `dashboard/static/project.js:47` | JavaScript function |
| `log` | `dashboard/static/project.js:5` | JavaScript function |
| `runQuickDemo` | `dashboard/static/project.js:68` | JavaScript function |
| `post` | `dashboard/static/project.js:83` | JavaScript function |
| `runAction` | `dashboard/static/project.js:93` | JavaScript function |
| `isLight` | `dashboard/static/three-scene.js:21` | JavaScript function |
| `updateThemeColors` | `dashboard/static/three-scene.js:45` | JavaScript function |
| `animate` | `dashboard/static/three-scene.js:61` | JavaScript function |
| `serve_ui` | `fastapi_transactions/app/main.py:46` | Python function |
| `create_transaction` | `fastapi_transactions/app/main.py:51` | Python function |
| `list_transactions` | `fastapi_transactions/app/main.py:61` | Python function |
| `get_transaction` | `fastapi_transactions/app/main.py:66` | Python function |
| `get_balance` | `fastapi_transactions/app/main.py:74` | Python function |
| `health` | `fastapi_transactions/app/main.py:85` | Python function |
| `showToast` | `fastapi_transactions/app/static/app.js:29` | JavaScript function |
| `formatAmount` | `fastapi_transactions/app/static/app.js:38` | JavaScript function |
| `fetchJSON` | `fastapi_transactions/app/static/app.js:43` | JavaScript function |
| `renderTransactions` | `fastapi_transactions/app/static/app.js:56` | JavaScript function |
| `escapeHtml` | `fastapi_transactions/app/static/app.js:90` | JavaScript function |
| `loadData` | `fastapi_transactions/app/static/app.js:98` | JavaScript function |
| `reset_store` | `fastapi_transactions/tests/test_main.py:11` | Python function |
| `test_health_check` | `fastapi_transactions/tests/test_main.py:19` | Python function |
| `test_list_transactions_empty` | `fastapi_transactions/tests/test_main.py:25` | Python function |
| `test_create_credit_transaction` | `fastapi_transactions/tests/test_main.py:31` | Python function |
| `test_create_debit_transaction` | `fastapi_transactions/tests/test_main.py:45` | Python function |
| `test_balance_reflects_credits_and_debits` | `fastapi_transactions/tests/test_main.py:54` | Python function |
| `test_rejects_non_positive_amount` | `fastapi_transactions/tests/test_main.py:66` | Python function |
| `test_rejects_invalid_transaction_type` | `fastapi_transactions/tests/test_main.py:74` | Python function |
| `test_get_single_transaction_and_404` | `fastapi_transactions/tests/test_main.py:79` | Python function |
| `test_end_to_end_rust_and_service` | `fraud-score-system/integration/test_integration.py:38` | Python function |
| `health` | `fraud-score-system/service/app/main.py:108` | Python function |
| `create_transaction` | `fraud-score-system/service/app/main.py:62` | Python function |
| `list_pending` | `fraud-score-system/service/app/main.py:81` | Python function |
| `submit_score` | `fraud-score-system/service/app/main.py:87` | Python function |
| `get_transaction` | `fraud-score-system/service/app/main.py:99` | Python function |
| `setup_function` | `fraud-score-system/service/tests/test_service.py:10` | Python function |
| `test_ingest_then_appears_in_pending` | `fraud-score-system/service/tests/test_service.py:15` | Python function |
| `test_submit_score_marks_scored_and_get_returns_it` | `fraud-score-system/service/tests/test_service.py:30` | Python function |
| `test_invalid_ingest_returns_422` | `fraud-score-system/service/tests/test_service.py:50` | Python function |
| `test_score_unknown_transaction_returns_404` | `fraud-score-system/service/tests/test_service.py:59` | Python function |
| `sleep` | `fraud-score-system/worker/worker.js:21` | JavaScript function |
| `scoreTransaction` | `fraud-score-system/worker/worker.js:24` | JavaScript function |
| `processOne` | `fraud-score-system/worker/worker.js:65` | JavaScript function |
| `main` | `fraud-score-system/worker/worker.js:79` | JavaScript function |
| `health` | `sample-projects/fintech-platform/app/main.py:14` | Python function |
| `register` | `sample-projects/fintech-platform/app/main.py:19` | Python function |
| `login` | `sample-projects/fintech-platform/app/main.py:24` | Python function |
| `get_account` | `sample-projects/fintech-platform/app/main.py:29` | Python function |
| `list_transactions` | `sample-projects/fintech-platform/app/main.py:34` | Python function |
| `transfer` | `sample-projects/fintech-platform/app/main.py:39` | Python function |
| `daily_report` | `sample-projects/fintech-platform/app/main.py:44` | Python function |
| `fraud_alerts` | `sample-projects/fintech-platform/app/main.py:49` | Python function |
| `admin_users` | `sample-projects/fintech-platform/app/main.py:54` | Python function |

## Models

| Name | Source | Detail |
|------|--------|--------|
| `model.py` | `Project-based-entity-diagrams/insight/model.py` | data model / schema |
| `schema.py` | `Project-based-entity-diagrams/insight/schema.py` | data model / schema |
| `models.py` | `fastapi_transactions/app/models.py` | data model / schema |
| `models.py` | `sample-projects/fintech-platform/app/models.py` | data model / schema |
| `schema.sql` | `sample-projects/fintech-platform/schema.sql` | data model / schema |

## Services

| Name | Source | Detail |
|------|--------|--------|
| `app.js` | `dashboard/static/app.js` | Node.js process |
| `app.js` | `fastapi_transactions/app/static/app.js` | Node.js process |
| `worker.js` | `fraud-score-system/worker/worker.js` | Node.js process |
| `server.js` | `sample-projects/fintech-platform/server.js` | Node.js process |

## Tests

| Name | Source | Detail |
|------|--------|--------|
| `demo_tests.py` | `dashboard/demo_tests.py` | test file |
| `test_main.py` | `fastapi_transactions/tests/test_main.py` | test file |
| `test_integration.py` | `fraud-score-system/integration/test_integration.py` | test file |
| `conftest.py` | `fraud-score-system/service/conftest.py` | test file |
| `test_service.py` | `fraud-score-system/service/tests/test_service.py` | test file |
