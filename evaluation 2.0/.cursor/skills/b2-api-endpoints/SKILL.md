---
name: b2-api-endpoints
description: B2 evaluation task — map all API and frontend routes with file citations. Use when asked about B2, endpoint map, or route discovery in evaluation 2.0.
---

# B2 API Endpoint Agent

## Commands
```bash
python Project-based-entity-diagrams/analyze.py fastapi_transactions -o outputs/b2-endpoint-map/fastapi_transactions-insight.html
python Project-based-entity-diagrams/analyze.py fraud-score-system/service -o outputs/b2-endpoint-map/fraud-score-service-insight.html
```

Write `outputs/b2-endpoint-map/ENDPOINTS.md` with Method | Route | Source | Description.

FastAPI routes use `@app.get/post` — verify features count > 0.

Prompt: `agents/b2-api-endpoints/PROMPT.md`
