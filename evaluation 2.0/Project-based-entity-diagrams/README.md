# Project Insight

A static code analyzer that turns any codebase into a single **interactive HTML report** —
stack, every feature/endpoint, the data model (ER diagram + draggable graph), and security
findings. Pure Python, standard library only. **No AI, no API keys, no internet** to run
(the generated report loads its diagram libraries from a CDN when you open it).

## Quick start

```bash
python analyze.py <path-to-project-or-zip>
# example:
python analyze.py ./my-app
python analyze.py ./my-app.zip -o report.html

# B1 artifact inventory (markdown):
python inventory.py ../fastapi_transactions -o ../outputs/b1-artifact-inventory/report.md
```

It prints a summary and writes `<name>-insight.html`. Double-click that file to open the report.

**Evaluation 2.0:** This tool serves **B1** (inventory via `inventory.py`) and **B2** (endpoint map via `analyze.py`). FastAPI routes (`@app.get/post/...`) are detected.

## What it detects

- **Stack** — languages, frameworks and data layer from `package.json`, `composer.json`,
  `requirements.txt` (Node/Express, React, PHP, Flask, Django, MySQL, Postgres, ORMs…).
- **Features** — every route/endpoint/handler, grouped by role (auth / student / admin),
  with the file:line and the tables it touches. PHP files are treated as endpoints.
- **Data model** — parses SQL `CREATE TABLE` (columns, PK, FK). If no DDL exists, it
  **infers** tables and columns from the `INSERT/SELECT/UPDATE` statements in the code and
  labels everything as inferred.
- **Relationships** — declared foreign keys, or inferred links where tables share a key.
- **Design views** — a system-architecture diagram (client → backend → DB → email),
  an execution/data-flow sequence for the most write-heavy endpoint, and a component/module
  breakdown — all derived from the code (it won't invent deployment/infra it can't see).
- **Findings** — common smells: string-interpolated SQL (injection), plaintext passwords,
  empty/hardcoded DB credentials, hardcoded SMTP credentials. (Secret *values* are never printed.)

## Output

A self-contained `index.html` with: overview, feature list, an interactive vis-network
entity graph (drag/zoom), a Mermaid ER diagram, per-table entity tables, a relationships
table, a system-architecture diagram, an execution-flow sequence, a component map, and findings.

## How it works

```
analyze.py            # CLI: prepare input (folder/zip) -> run scanners -> render
insight/
  scan.py             # walk the tree, skip node_modules/vendor/venv/...
  stack.py            # detect languages, frameworks, run commands, data layer
  schema.py           # parse SQL DDL; else infer schema from queries; relationships
  design.py           # architecture diagram, execution flow, component breakdown
  features.py         # detect endpoints (Express/Flask/PHP) + security findings
  render.py           # build the interactive HTML
  model.py            # dataclasses: Project, Table, Column, Relationship, Feature
```

## Tested on

- A Node + Express + **MySQL (DDL)** app → 10 tables, 10 FKs, 27 endpoints.
- A **PHP + MySQL (no schema file)** app → 4 tables inferred, 14 endpoints, relationships
  inferred from shared keys.

See `examples/` for the generated reports.

## Limitations (v1, honest)

- Best on the stacks above; other frameworks get lighter detection.
- Inferred schema only sees tables that appear in queries with columns; a purely
  read-only table may be missed. Inferred column types are guesses.
- Regex-based, not a full parser — it favors precision and clear citations over covering
  every exotic pattern. Diagrams should be sanity-checked for very large schemas.

## Requirements

Python 3.8+. No third-party packages.
