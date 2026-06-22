"""Rich project guides for manager / evaluator walkthrough."""

PROJECT_GUIDES = {
    "entity-diagrams": {
        "theme": "archive",
        "theme_label": "The Archive Room",
        "agent_name": "Archie",
        "agent_role": "Repository Inventory Agent",
        "greeting": "Hello — I'm Archie. I read a codebase like a librarian reads shelves: I list every important file, class, and config so nothing is missed.",
        "summary": "Project Insight reads any codebase with static analysis (not an LLM). Supports FastAPI, Flask, Express, Django, SQL DDL, Django ORM, SQLAlchemy, Prisma. Paste GitHub, upload zip, or scan a local folder.",
        "flow": [
            {"step": 1, "title": "Pick a source", "detail": "Local folder, GitHub URL, or .zip — e.g. Django College-ERP, MERN repos, FastAPI services."},
            {"step": 2, "title": "Scanner reads the code", "detail": "B1 file inventory + B2 routes, entities, ER diagram, how-to-run (30 min task in Cursor for deep work)."},
            {"step": 3, "title": "View the report", "detail": "HTML report shows scanner coverage — what was found and any gaps."},
        ],
        "tasks": ["B1 — find classes, configs, utilities", "B2 — list every API route"],
        "links": [
            {"label": "📋 Scan All Files (B1)", "action": "inventory", "hint": "Creates a markdown list of all code parts"},
            {"label": "🗺 Map API Routes (B2)", "action": "analyze", "hint": "Creates an interactive HTML diagram"},
            {"label": "📊 Open Scan Report", "href": "/api/reports/fintech-demo", "hint": "Fintech demo diagram (from walkthrough or B2)", "needs_report": True},
        ],
        "agents_here": [
            {"id": "B1", "name": "Repo Inventory Agent", "tip": "Finds models, services, configs in 30 minutes"},
            {"id": "B2", "name": "API Endpoint Agent", "tip": "Maps every route with file name and line number"},
        ],
        "start_hint": "No server to start. Click a button below to run the scanner.",
    },
    "fastapi-tx": {
        "theme": "bank",
        "theme_label": "The Ledger Desk",
        "agent_name": "Tessa",
        "agent_role": "Transactions Service Agent",
        "greeting": "Hi — I'm Tessa. I built a small bank ledger: you can add credits and debits, see your balance, and everything is checked before it is saved.",
        "summary": "A working web app for recording money in and money out. Built with Python FastAPI. Good for showing a greenfield API from scratch.",
        "flow": [
            {"step": 1, "title": "Open the web page", "detail": "See sample transactions on screen."},
            {"step": 2, "title": "Add a transaction", "detail": "Credit (money in) or debit (money out). Bad amounts are rejected."},
            {"step": 3, "title": "Check balance", "detail": "The app adds up everything automatically."},
        ],
        "tasks": ["B4 — build FastAPI service", "B3 — run automated tests"],
        "links": [
            {"label": "📋 Scan All Files (B1)", "action": "inventory", "hint": "Markdown inventory of this service"},
            {"label": "🗺 Map API Routes (B2)", "action": "analyze", "hint": "Interactive HTML diagram — opens when done"},
            {"label": "📊 Open Scan Report", "href": "/api/reports/fastapi-tx", "hint": "Run B2 first if missing", "needs_report": True},
            {"label": "🧪 Run Automated Tests (B3)", "action": "run-tests", "hint": "Runs pytest and shows pass/fail"},
        ],
        "agents_here": [
            {"id": "B4", "name": "FastAPI Greenfield Agent", "tip": "Built this service: POST/GET transactions, balance, validation"},
            {"id": "B3", "name": "Test Discovery Agent", "tip": "8 automated tests — run with one click"},
        ],
        "start_cmd": "cd fastapi_transactions && uvicorn app.main:app --port 8000",
    },
    "fraud-score": {
        "theme": "security",
        "theme_label": "The Security Control Room",
        "agent_name": "Sam",
        "agent_role": "Fraud Pipeline Orchestrator",
        "greeting": "Hello — I'm Sam. I connect three programs written in different languages: Python receives transactions, Node.js picks them up, and Rust calculates a fraud score.",
        "summary": "A mini fraud-detection pipeline. A transaction goes in, gets a risk score 0–100, and comes back scored. Shows multi-language system design.",
        "flow": [
            {"step": 1, "title": "Python receives the transaction", "detail": "FastAPI stores it as “pending”."},
            {"step": 2, "title": "Node worker picks it up", "detail": "Polls every second, sends data to Rust."},
            {"step": 3, "title": "Rust scores the risk", "detail": "Large amount + odd hour + risky country = higher score."},
            {"step": 4, "title": "Score is saved back", "detail": "Transaction status changes to “scored”."},
        ],
        "tasks": ["A3 — polyglot mini-system", "B3 — integration tests"],
        "links": [
            {"label": "📋 Scan All Files (B1)", "action": "inventory", "hint": "Inventory Python + Node + Rust parts"},
            {"label": "🗺 Map API Routes (B2)", "action": "analyze", "hint": "Architecture diagram — opens when done"},
            {"label": "📊 Open Scan Report", "href": "/api/reports/fraud-score", "hint": "Run B2 first if missing", "needs_report": True},
            {"label": "🧪 Run Automated Tests (B3)", "action": "run-tests", "hint": "Python + integration tests"},
        ],
        "agents_here": [
            {"id": "A3", "name": "Polyglot System Agent", "tip": "Python + Node + Rust with shared data contract"},
            {"id": "B3", "name": "Test Discovery Agent", "tip": "Unit tests per language + end-to-end path"},
        ],
        "start_cmd": "cd fraud-score-system/service && uvicorn app.main:app --port 8001",
    },
    "fintech-demo": {
        "theme": "corporate",
        "theme_label": "The Demo Floor",
        "agent_name": "Fin",
        "agent_role": "Fintech Demo Guide",
        "greeting": "Welcome — I'm Fin. This is a sample banking platform built on purpose so the scanner has something rich to analyse: 5 database tables, 12 API routes, multiple code layers.",
        "summary": "A demo fintech API with accounts, payments, fraud alerts, and an Express gateway. Best project to show B1/B2 scanning to a manager.",
        "flow": [
            {"step": 1, "title": "Scan with Project Insight", "detail": "Shows 27 artifacts, 12 endpoints, 5 tables."},
            {"step": 2, "title": "Open the HTML report", "detail": "Interactive ER diagram and route list."},
            {"step": 3, "title": "Optional: run the API", "detail": "Click **Open API Docs** when the service is online."},
        ],
        "tasks": ["B1 — best inventory demo", "B2 — best endpoint map demo"],
        "links": [
            {"label": "📋 Scan All Files (B1)", "action": "inventory", "hint": "~27 artifacts, 5 tables"},
            {"label": "🗺 Map API Routes (B2)", "action": "analyze", "hint": "12 routes + ER diagram — opens when done"},
            {"label": "📊 Open Scan Report", "href": "/api/reports/fintech-demo", "hint": "Run B2 first if missing", "needs_report": True},
        ],
        "agents_here": [
            {"id": "B1", "name": "Repo Inventory Agent", "tip": "27 artifacts detected in this demo"},
            {"id": "B2", "name": "API Endpoint Agent", "tip": "12 routes across Python + Node"},
        ],
        "start_cmd": "cd sample-projects/fintech-platform && PYTHONPATH=. uvicorn app.main:app --port 8002",
    },
}
