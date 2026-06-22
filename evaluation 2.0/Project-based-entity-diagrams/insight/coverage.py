"""Summarize what the static scanner detected (honest coverage notes)."""
from __future__ import annotations

from .model import Project

ROUTE_DETECTORS = {
    "Express/Koa": lambda p: any(f.source.endswith((".js", ".ts")) for f in p.features),
    "Flask": lambda p: "Flask" in p.frameworks and any("route" in f.detail.lower() for f in p.features),
    "FastAPI": lambda p: "FastAPI" in p.frameworks and any("FastAPI" in f.detail for f in p.features),
    "React Router": lambda p: "React Router" in p.frameworks and any("React Router" in f.detail for f in p.features),
    "json-server": lambda p: "json-server" in p.frameworks and any("json-server" in f.detail for f in p.features),
    "Django": lambda p: "Django" in p.frameworks and any("Django" in f.detail for f in p.features),
    "PHP": lambda p: any(f.source.endswith(".php") for f in p.features),
}

SCHEMA_SOURCES = {
    "SQL DDL": lambda p: p.has_ddl and "Django" not in (p.data_layer or "") and "SQLAlchemy" not in (p.data_layer or "") and "Prisma" not in (p.data_layer or ""),
    "Django ORM": lambda p: "Django" in (p.data_layer or ""),
    "SQLAlchemy ORM": lambda p: "SQLAlchemy" in (p.data_layer or ""),
    "Prisma": lambda p: "Prisma" in (p.data_layer or ""),
    "json-server DB": lambda p: "json-server" in (p.data_layer or ""),
    "README docs": lambda p: "README" in (p.data_layer or ""),
    "Query inference": lambda p: p.tables and not p.has_ddl,
}


def annotate(project: Project) -> list[str]:
    """Return human-readable coverage lines; append gaps to findings."""
    lines: list[str] = []
    langs = ", ".join(project.languages) or "unknown"
    fws = ", ".join(project.frameworks) or "none detected"
    lines.append(f"Languages: {langs} · Frameworks: {fws}")

    route_hits = [name for name, fn in ROUTE_DETECTORS.items() if fn(project)]
    if project.features:
        lines.append(f"Routes/endpoints: {len(project.features)} found" + (f" ({', '.join(route_hits)})" if route_hits else ""))
    else:
        lines.append("Routes/endpoints: none detected — may be an unsupported stack or server-rendered-only app")

    if project.tables:
        src = next((n for n, fn in SCHEMA_SOURCES.items() if fn(project)), "schema")
        lines.append(f"Data model: {len(project.tables)} entities via {src}")
    else:
        lines.append("Data model: no tables/entities — in-memory API, missing ORM files, or unsupported ORM")

    gaps: list[str] = []
    if "Django" in project.frameworks and not any("Django" in f.detail for f in project.features):
        gaps.append("Django detected but no urlpatterns parsed — check urls.py layout")
    if "React" in project.frameworks and not any("React Router" in f.detail or "json-server" in f.detail for f in project.features):
        gaps.append("React app detected but no routes found — check App.js for Route components")
    if project.features and not project.tables:
        gaps.append("API routes found but no persistence layer in code (common for stateless services)")

    project.scan_coverage = lines
    if gaps:
        for g in gaps:
            if g not in project.findings:
                project.findings.append(g)
    return lines
