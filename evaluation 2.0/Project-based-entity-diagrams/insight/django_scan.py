"""Django urlpatterns + models.Model detection (stdlib regex only)."""
from __future__ import annotations

import os
import re

from .model import Column, Feature, Relationship, Table
from .scan import iter_files, read

PATH_RE = re.compile(
    r"(?:path|re_path)\s*\(\s*['\"]([^'\"]*)['\"]\s*,\s*include\s*\(\s*['\"]([^'\"]+)['\"]",
    re.MULTILINE,
)
ROUTE_RE = re.compile(
    r"(?:path|re_path)\s*\(\s*['\"]([^'\"]*)['\"]\s*,",
    re.MULTILINE,
)
MODEL_CLASS_RE = re.compile(r"class\s+(\w+)\s*\(\s*models\.Model\s*\)\s*:", re.MULTILINE)
FIELD_RE = re.compile(
    r"^\s+(\w+)\s*=\s*models\.(\w+)\(([^)]*)\)",
    re.MULTILINE,
)
FK_RE = re.compile(r"ForeignKey\s*\(\s*(?:['\"](\w+)['\"]|(\w+))")


def _line_of(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


def _join_prefix(prefix: str, route: str) -> str:
    p = (prefix or "").rstrip("/")
    r = route or ""
    if not p:
        return "/" + r.lstrip("/") if r else "/"
    if not r:
        return p + "/" if not p.endswith("/") else p
    if r.startswith("^"):
        return p + r
    return (p + "/" + r.lstrip("/")).replace("//", "/")


def _resolve_urls_module(root: str, module: str) -> str | None:
    """info.urls -> .../info/urls.py"""
    parts = module.split(".")
    if parts and parts[-1] == "urls":
        parts = parts[:-1]
    if not parts:
        return None
    candidate = os.path.join(root, *parts, "urls.py")
    return candidate if os.path.isfile(candidate) else None


def _parse_urls_file(root: str, ap: str, rel: str, prefix: str, seen: set[str]) -> list[Feature]:
    if rel in seen:
        return []
    seen.add(rel)
    text = read(ap)
    if not text or "urlpatterns" not in text:
        return []
    feats: list[Feature] = []

    for m in PATH_RE.finditer(text):
        sub_prefix = _join_prefix(prefix, m.group(1))
        sub_mod = m.group(2)
        sub_path = _resolve_urls_module(root, sub_mod)
        if sub_path:
            sub_rel = os.path.relpath(sub_path, root).replace("\\", "/")
            feats.extend(_parse_urls_file(root, sub_path, sub_rel, sub_prefix, seen))

    for m in ROUTE_RE.finditer(text):
        segment = text[m.start() : m.end() + 80]
        if "include(" in segment:
            continue
        route = _join_prefix(prefix, m.group(1))
        line = _line_of(text, m.start())
        role = _route_role(route, segment)
        detail = "Django route"
        if ".as_view()" in segment:
            detail = "Django class-based view"
        elif "admin.site.urls" in segment:
            detail = "Django admin"
            route = _join_prefix(prefix, "admin/")
        feats.append(
            Feature(
                name=f"GET {route}",
                role=role,
                detail=detail,
                source=f"{rel}:{line}",
                http="GET",
                ops=[],
            )
        )
    return feats


def detect_django_routes(project, root: str) -> None:
    if "Django" not in project.frameworks:
        return
    seen: set[str] = set()
    feats: list[Feature] = []
    for ap, rel in iter_files(root):
        if not rel.endswith("urls.py"):
            continue
        feats.extend(_parse_urls_file(root, ap, rel, "", seen))
    if feats:
        existing = {(f.http, f.name) for f in project.features}
        for f in feats:
            key = (f.http, f.name)
            if key not in existing:
                project.features.append(f)
                existing.add(key)
        project.features.sort(key=lambda x: (x.role, x.source))


def _route_role(route: str, segment: str) -> str:
    blob = (route + " " + segment).lower()
    if any(k in blob for k in ("login", "logout", "accounts", "auth")):
        return "auth"
    if "admin" in blob:
        return "admin"
    if any(k in blob for k in ("student", "teacher", "attendance", "marks", "timetable")):
        return "student"
    if "api/" in blob or "/api" in route:
        return "general"
    return "general"


def _model_body(text: str, start: int) -> str:
    rest = text[start:]
    nxt = re.search(r"\nclass\s+\w+", rest)
    return rest[: nxt.start()] if nxt else rest[:4000]


def detect_django_models(project, root: str) -> None:
    if "Django" not in project.frameworks:
        return
    tables: list[Table] = []
    rels: list[Relationship] = []
    by_name: dict[str, Table] = {}

    for ap, rel in iter_files(root):
        if not rel.endswith("models.py"):
            continue
        text = read(ap)
        if "models.Model" not in text:
            continue
        for m in MODEL_CLASS_RE.finditer(text):
            cls = m.group(1)
            tbl_name = cls  # Django default table is app_label_modelname; class name is clearer in reports
            line = _line_of(text, m.start())
            tbl = Table(name=tbl_name, source=f"{rel}:{line}", inferred=False)
            tbl.columns.append(Column(name="id", type="bigint", pk=True, notes="Django auto PK"))
            body = _model_body(text, m.end())
            for fm in FIELD_RE.finditer(body):
                fname, ftype, fargs = fm.group(1), fm.group(2), fm.group(3)
                if fname in ("Meta",):
                    continue
                col = Column(name=fname, type=ftype.lower())
                if ftype == "ForeignKey":
                    ref = FK_RE.search(f"models.{ftype}({fargs})")
                    if ref:
                        parent = ref.group(1) or ref.group(2)
                        col.fk_to = f"{parent}.id"
                        rels.append(
                            Relationship(
                                parent=parent,
                                child=cls,
                                key=fname,
                                source=f"{rel}:{_line_of(body, fm.start())}",
                            )
                        )
                if "primary_key=True" in fargs:
                    col.pk = True
                tbl.columns.append(col)
            tables.append(tbl)
            by_name[cls] = tbl

    if tables:
        project.tables = tables
        project.relationships = rels
        project.has_ddl = True
        project.data_layer = project.data_layer or "Django ORM (models.Model)"
        if not any("INFERRED FROM QUERY" in x for x in project.findings):
            project.findings.append("Tables recovered from Django models.py (ORM, not raw SQL DDL).")
