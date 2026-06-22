"""React Router + json-server mock API detection."""
from __future__ import annotations

import json
import os
import re

from .model import Column, Feature, Table
from .scan import iter_files, read

ROUTE_TAG_RE = re.compile(
    r"<Route\b[^>]*?\bpath\s*=\s*[\"']([^\"']+)[\"']",
    re.IGNORECASE | re.DOTALL,
)
ROUTE_V6_RE = re.compile(
    r"path\s*=\s*[\"']([^\"']+)[\"']\s+element\s*=",
    re.IGNORECASE,
)
FETCH_URL_RE = re.compile(
    r"""fetch\s*\(\s*[`'"]([^`'"]+)[`'"]""",
    re.IGNORECASE,
)


def _line_of(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


def detect_react_routes(project, root: str) -> None:
    if "React" not in project.frameworks and not any(
        rel.endswith((".jsx", ".tsx")) for _, rel in iter_files(root)
    ):
        return
    feats: list[Feature] = []
    for ap, rel in iter_files(root):
        if not rel.endswith((".js", ".jsx", ".tsx")):
            continue
        text = read(ap)
        if "Route" not in text and "route" not in text.lower():
            continue
        seen_paths: set[str] = set()
        for m in ROUTE_TAG_RE.finditer(text):
            path = m.group(1)
            if path in seen_paths:
                continue
            seen_paths.add(path)
            role = _route_role(path)
            feats.append(
                Feature(
                    name=f"GET {path}",
                    role=role,
                    detail="React Router page (client-side route)",
                    source=f"{rel}:{_line_of(text, m.start())}",
                    http="GET",
                    ops=[],
                )
            )
        for m in ROUTE_V6_RE.finditer(text):
            path = m.group(1)
            if path in seen_paths:
                continue
            seen_paths.add(path)
            feats.append(
                Feature(
                    name=f"GET {path}",
                    role=_route_role(path),
                    detail="React Router v6 page",
                    source=f"{rel}:{_line_of(text, m.start())}",
                    http="GET",
                    ops=[],
                )
            )
        for m in FETCH_URL_RE.finditer(text):
            url = m.group(1)
            if url.startswith("http") or url.startswith("/"):
                feats.append(
                    Feature(
                        name=f"GET {url.split('?')[0]}",
                        role="general",
                        detail="fetch() API call from React component",
                        source=f"{rel}:{_line_of(text, m.start())}",
                        http="GET",
                        ops=[],
                    )
                )
    if feats:
        _merge_features(project, feats)


def detect_json_server_schema(project, root: str) -> bool:
    """json-server db.json top-level keys → table shapes."""
    for ap, rel in iter_files(root):
        base = os.path.basename(rel).lower()
        if base not in ("db.json", "database.json") and "/api/" not in rel.replace("\\", "/"):
            continue
        text = read(ap)
        if not text.strip().startswith("{"):
            continue
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            continue
        tables: list[Table] = []
        for collection, rows in data.items():
            if not isinstance(rows, list) or not rows or not isinstance(rows[0], dict):
                continue
            tbl = Table(name=collection, source=f"{rel}:1", inferred=False)
            for key, val in rows[0].items():
                tbl.columns.append(Column(name=key, type=type(val).__name__))
            tables.append(tbl)
        if tables:
            project.tables = tables
            project.has_ddl = True
            project.data_layer = project.data_layer or "json-server mock DB (db.json)"
            project.findings.append(
                "Data model from json-server db.json — demo/mock API; MariaDB schema may be documented in README/PDF only."
            )
            return True
    return False


def detect_json_server_routes(project, root: str) -> None:
    """json-server db.json → mock REST routes + table shapes."""
    for ap, rel in iter_files(root):
        base = os.path.basename(rel).lower()
        if base not in ("db.json", "database.json") and "/api/" not in rel.replace("\\", "/"):
            continue
        text = read(ap)
        if not text.strip().startswith("{"):
            continue
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        routes: list[Feature] = []
        for collection, rows in data.items():
            if not isinstance(rows, list):
                continue
            path = f"/{collection}"
            routes.append(
                Feature(
                    name=f"GET {path}",
                    role="general",
                    detail=f"json-server collection ({len(rows)} records)",
                    source=f"{rel}:1",
                    http="GET",
                    ops=[],
                )
            )
            routes.append(
                Feature(
                    name=f"POST {path}",
                    role="general",
                    detail="json-server create",
                    source=f"{rel}:1",
                    http="POST",
                    ops=[],
                )
            )
        if routes:
            _merge_features(project, routes)
        return


def _route_role(path: str) -> str:
    p = path.lower()
    if any(k in p for k in ("login", "register", "auth")):
        return "auth"
    if "admin" in p:
        return "admin"
    if any(k in p for k in ("cart", "product", "order")):
        return "student"
    return "general"


def _merge_features(project, new_feats: list[Feature]) -> None:
    existing = {(f.http, f.name) for f in project.features}
    for f in new_feats:
        key = (f.http, f.name)
        if key not in existing:
            project.features.append(f)
            existing.add(key)
    project.features.sort(key=lambda x: (x.role, x.source))
