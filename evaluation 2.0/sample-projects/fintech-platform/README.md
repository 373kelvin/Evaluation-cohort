# Fintech Platform (Sample Project)

**Purpose:** Rich demo codebase for **B1** artifact inventory and **B2** endpoint mapping.
Designed to impress evaluators with multi-layer architecture detectable by Project Insight.

## Stack

- **Python / FastAPI** — accounts, payments, fraud alerts, admin
- **Node.js / Express** — API gateway webhooks
- **MySQL DDL** — 5 tables with foreign keys in `schema.sql`

## Run (optional)

```bash
pip install -r requirements.txt
uvicorn app.main:app --port 8002
```

## Scan from dashboard

Click **B1 Scan** or **B2 Map** on the Fintech Platform card, or:

```bash
python ../../Project-based-entity-diagrams/inventory.py . -o ../../outputs/b1-artifact-inventory/fintech-platform-inventory.md
python ../../Project-based-entity-diagrams/analyze.py . -o ../../outputs/b2-endpoint-map/fintech-platform-insight.html
```

Expected: **10+ endpoints**, **5 DB tables**, **4 FK relationships**, **20+ artifacts**.
