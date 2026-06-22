"""Parse entity tables documented in README.md (common in DBMS college projects)."""
from __future__ import annotations

import re

from .model import Column, Table
from .scan import iter_files, read

ENTITY_SECTION_RE = re.compile(
    r"###?\s*\d*\.?\s*Entities and their Attributes",
    re.IGNORECASE,
)
ENTITY_ROW_RE = re.compile(
    r"^\|\s*([A-Za-z][A-Za-z0-9_]*)\s*\|",
    re.MULTILINE,
)
REL_SECTION_RE = re.compile(
    r"###?\s*\d*\.?\s*Entities and Relations",
    re.IGNORECASE,
)
REL_ROW_RE = re.compile(
    r"^\|\s*([A-Za-z][A-Za-z0-9_]*)\s*\|\s*([A-Za-z][A-Za-z0-9_\s]+?)\s*\|",
    re.MULTILINE,
)


def _line_of(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


def detect_readme_entities(project, root: str) -> bool:
    if project.tables:
        return False
    for ap, rel in iter_files(root):
        if not rel.lower().endswith("readme.md"):
            continue
        text = read(ap)
        sec = ENTITY_SECTION_RE.search(text)
        if not sec:
            continue
        chunk = text[sec.start() : sec.start() + 8000]
        tables: list[Table] = []
        skip = {"entities", "entity", "attributes", "attribute", "type", "entities"}
        for m in ENTITY_ROW_RE.finditer(chunk):
            name = m.group(1).strip()
            if name.lower() in skip or name.upper() == "ENTITIES":
                continue
            line = _line_of(chunk, m.start())
            tbl = Table(
                name=name,
                source=f"{rel}:{line}",
                inferred=True,
            )
            tbl.columns.append(Column(name="id", type="string", pk=True, notes="from README (details in repo)"))
            tables.append(tbl)
        if tables:
            project.tables = tables
            project.data_layer = project.data_layer or "Documented in README (MariaDB/SQL schema not in repo files)"
            project.findings.append(
                "Entity list parsed from README.md — SQL implementation may be in PDF/external DB, not in this zip."
            )
            return True
    return False
