"""ORM schema detection: SQLAlchemy + Prisma (stdlib regex)."""
from __future__ import annotations

import re

from .model import Column, Relationship, Table
from .scan import iter_files, read

SA_MODEL_RE = re.compile(
    r"class\s+(\w+)\s*\(\s*(?:[\w.]+\.)?(?:Base|DeclarativeBase|db\.Model)\s*\)\s*:",
    re.MULTILINE,
)
SA_COLUMN_RE = re.compile(
    r"^\s+(\w+)\s*=\s*(?:Column|mapped_column)\(\s*(\w+)?",
    re.MULTILINE,
)
SA_TYPED_RE = re.compile(
    r"^\s+(\w+)\s*:\s*Mapped\[.*?\]\s*=\s*mapped_column",
    re.MULTILINE,
)
SA_FK_RE = re.compile(r"ForeignKey\s*\(\s*['\"](\w+)['\"]")

PRISMA_MODEL_RE = re.compile(r"model\s+(\w+)\s*\{([^}]+)\}", re.MULTILINE | re.DOTALL)
PRISMA_FIELD_RE = re.compile(r"^\s+(\w+)\s+(\w+)", re.MULTILINE)


def _line_of(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


def _model_body(text: str, start: int) -> str:
    rest = text[start:]
    nxt = re.search(r"\nclass\s+\w+", rest)
    return rest[: nxt.start()] if nxt else rest[:5000]


def detect_sqlalchemy(project, root: str) -> bool:
    if project.tables:
        return False
    tables: list[Table] = []
    rels: list[Relationship] = []
    for ap, rel in iter_files(root):
        if not rel.endswith(".py"):
            continue
        text = read(ap)
        if "Column(" not in text and "mapped_column" not in text:
            continue
        for m in SA_MODEL_RE.finditer(text):
            cls = m.group(1)
            line = _line_of(text, m.start())
            tbl = Table(name=cls, source=f"{rel}:{line}", inferred=False)
            body = _model_body(text, m.end())
            for cm in SA_COLUMN_RE.finditer(body):
                cname, ctype = cm.group(1), cm.group(2) or "string"
                col = Column(name=cname, type=ctype.lower())
                seg = body[cm.start() : cm.start() + 120]
                if "primary_key=True" in seg or "primary_key = True" in seg:
                    col.pk = True
                fk = SA_FK_RE.search(seg)
                if fk:
                    col.fk_to = f"{fk.group(1)}.id"
                    rels.append(
                        Relationship(
                            parent=fk.group(1),
                            child=cls,
                            key=cname,
                            source=f"{rel}:{line}",
                        )
                    )
                tbl.columns.append(col)
            for tm in SA_TYPED_RE.finditer(body):
                cname = tm.group(1)
                if cname not in [c.name for c in tbl.columns]:
                    tbl.columns.append(Column(name=cname, type="mapped"))
            if tbl.columns:
                tables.append(tbl)
    if tables:
        project.tables = tables
        project.relationships = rels
        project.has_ddl = True
        project.data_layer = project.data_layer or "SQLAlchemy ORM"
        project.findings.append("Tables recovered from SQLAlchemy model classes.")
        return True
    return False


def detect_prisma(project, root: str) -> bool:
    if project.tables:
        return False
    for ap, rel in iter_files(root):
        if not rel.endswith(".prisma") and "schema.prisma" not in rel:
            continue
        text = read(ap)
        if "model " not in text:
            continue
        tables: list[Table] = []
        for m in PRISMA_MODEL_RE.finditer(text):
            name = m.group(1)
            body = m.group(2)
            line = _line_of(text, m.start())
            tbl = Table(name=name, source=f"{rel}:{line}", inferred=False)
            for fm in PRISMA_FIELD_RE.finditer(body):
                fname, ftype = fm.group(1), fm.group(2)
                if fname.startswith("@@") or fname.startswith("@"):
                    continue
                col = Column(name=fname, type=ftype.lower())
                if "@id" in body.split(fname, 1)[-1][:40]:
                    col.pk = True
                tbl.columns.append(col)
            if tbl.columns:
                tables.append(tbl)
        if tables:
            project.tables = tables
            project.has_ddl = True
            project.data_layer = project.data_layer or "Prisma ORM"
            project.findings.append("Tables recovered from schema.prisma.")
            return True
    return False
