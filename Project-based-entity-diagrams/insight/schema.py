"""Recover the data model: parse SQL DDL, else infer tables/columns from queries."""
import re
from .model import Table, Column, Relationship
from .scan import iter_files, read

CREATE_RE = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`\"]?(\w+)[`\"]?\s*\((.*?)\)\s*;",
    re.IGNORECASE | re.DOTALL,
)
DBNAME_RES = [
    re.compile(r"CREATE\s+DATABASE\s+[`\"]?(\w+)", re.IGNORECASE),
    re.compile(r"\bdbname\s*[=:]\s*[\"'](\w+)[\"']", re.IGNORECASE),
    re.compile(r"\bdatabase\s*[=:]\s*[\"'](\w+)[\"']", re.IGNORECASE),
]


def _split_top(body):
    """Split a CREATE TABLE body on commas not nested in parentheses."""
    parts, depth, cur = [], 0, ""
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur.strip()); cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur.strip())
    return parts


def _line_of(text, idx):
    return text.count("\n", 0, idx) + 1


def parse_ddl(text, rel, project):
    found = []
    for m in CREATE_RE.finditer(text):
        name = m.group(1)
        body = m.group(2)
        line = _line_of(text, m.start())
        tbl = Table(name=name, source=f"{rel}:{line}")
        cols = {}
        for part in _split_top(body):
            up = part.upper()
            if up.startswith("PRIMARY KEY"):
                for c in re.findall(r"[`\"]?(\w+)[`\"]?", part[part.find("(") + 1:part.rfind(")")]):
                    if c in cols:
                        cols[c].pk = True
                continue
            if up.startswith("FOREIGN KEY"):
                fm = re.search(r"FOREIGN\s+KEY\s*\(\s*[`\"]?(\w+)[`\"]?\s*\)\s*REFERENCES\s+[`\"]?(\w+)[`\"]?\s*\(\s*[`\"]?(\w+)", part, re.IGNORECASE)
                if fm and fm.group(1) in cols:
                    cols[fm.group(1)].fk_to = f"{fm.group(2)}.{fm.group(3)}"
                continue
            if up.startswith(("KEY ", "UNIQUE", "INDEX", "CONSTRAINT", "CHECK")):
                continue
            cm = re.match(r"[`\"]?(\w+)[`\"]?\s+([A-Za-z]+(?:\([\d,]+\))?)", part)
            if not cm:
                continue
            col = Column(name=cm.group(1), type=cm.group(2).lower())
            if "PRIMARY KEY" in up:
                col.pk = True
            if "NOT NULL" in up:
                col.notes = "NOT NULL"
            if "UNIQUE" in up:
                col.notes = (col.notes + " UNIQUE").strip()
            cols[col.name] = col
            tbl.columns.append(col)
        found.append(tbl)
    return found


# ---- query-based inference (no DDL) ----
INSERT_RE = re.compile(r"INSERT\s+INTO\s+[`\"]?(\w+)[`\"]?\s*\(([^)]*)\)", re.IGNORECASE)
FROM_RE = re.compile(r"\bFROM\s+[`\"]?(\w+)[`\"]?", re.IGNORECASE)
UPDATE_RE = re.compile(r"\bUPDATE\s+[`\"]?(\w+)[`\"]?\s+SET\s+(.+?)(?:WHERE|$)", re.IGNORECASE | re.DOTALL)
SET_COL_RE = re.compile(r"[`\"]?(\w+)[`\"]?\s*=", )
NOISE_TABLES = {"dual", "information_schema"}

STOPWORDS = {"the","a","an","this","that","it","your","actual","database","form","query",
             "table","name","data","db","dual","select","where","values","set","into","from"}

def _strip_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)   # /* */
    out = []
    for line in text.splitlines():
        line = re.sub(r"//.*$", "", line)
        line = re.sub(r"#.*$", "", line)
        line = re.sub(r"--.*$", "", line)
        out.append(line)
    return "\n".join(out)



def infer_from_queries(root, project):
    tables = {}
    sources = {}

    def ensure(name, rel, line):
        if name.lower() in NOISE_TABLES or name.lower() in STOPWORDS:
            return None
        if name not in tables:
            tables[name] = Table(name=name, inferred=True, source=f"{rel}:{line}")
            sources[name] = set()
        return tables[name]

    for ap, rel in iter_files(root):
        if rel.endswith((".sql",)):
            continue
        text = _strip_comments(read(ap))
        for m in INSERT_RE.finditer(text):
            t = ensure(m.group(1), rel, _line_of(text, m.start()))
            if not t:
                continue
            for c in re.findall(r"[`\"]?(\w+)[`\"]?", m.group(2)):
                if c not in [x.name for x in t.columns]:
                    t.columns.append(Column(name=c, inferred=True))
        for m in FROM_RE.finditer(text):
            ensure(m.group(1), rel, _line_of(text, m.start()))
        for m in UPDATE_RE.finditer(text):
            t = ensure(m.group(1), rel, _line_of(text, m.start()))
            if not t:
                continue
            for c in SET_COL_RE.findall(m.group(2)[:200]):
                if c.lower() not in ("internal_cap",) and c not in [x.name for x in t.columns]:
                    # still add; capture extra columns referenced only in updates
                    t.columns.append(Column(name=c, inferred=True, notes="from UPDATE"))
                elif c not in [x.name for x in t.columns]:
                    t.columns.append(Column(name=c, inferred=True, notes="from UPDATE"))
    return [t for t in tables.values() if t.columns]


def infer_pks(tables):
    """Guess PKs for inferred tables: a column named id/<table>_id or *_no/reg_no used widely."""
    names = [t.name for t in tables]
    # columns shared across many tables are likely keys
    for t in tables:
        if t.pk_cols:
            continue
        for cand in ("id", f"{t.name}_id", "reg_no", "course_no", "email"):
            col = next((c for c in t.columns if c.name == cand), None)
            if col:
                col.pk = True
                col.notes = (col.notes + " PK (inferred)").strip()
                break


def relationships_from_ddl(tables):
    rels = []
    for t in tables:
        for c in t.columns:
            if c.fk_to:
                parent = c.fk_to.split(".")[0]
                rels.append(Relationship(parent=parent, child=t.name,
                                         key=c.name, source=t.source))
    return rels


def relationships_inferred(tables):
    """Link tables that share a column name (a likely common key)."""
    rels, seen = [], set()
    by_col = {}
    for t in tables:
        for c in t.columns:
            by_col.setdefault(c.name, []).append(t.name)
    for col, owners in by_col.items():
        if len(owners) < 2 or col in ("stud_name", "name", "date", "status"):
            continue
        for i in range(len(owners)):
            for j in range(i + 1, len(owners)):
                pair = tuple(sorted((owners[i], owners[j]))) + (col,)
                if pair in seen:
                    continue
                seen.add(pair)
                rels.append(Relationship(parent=owners[i], child=owners[j],
                                         key=col, inferred=True,
                                         source="shared column"))
    return rels


def analyze_schema(project, root):
    # DB name
    for ap, rel in iter_files(root):
        text = read(ap)
        for rx in DBNAME_RES:
            mm = rx.search(text)
            if mm:
                project.db_name = mm.group(1)
                break
        if project.db_name:
            break

    ddl_tables = []
    for ap, rel in iter_files(root):
        if rel.endswith(".sql"):
            ddl_tables += parse_ddl(read(ap), rel, project)

    if ddl_tables:
        project.has_ddl = True
        project.tables = ddl_tables
        project.relationships = relationships_from_ddl(ddl_tables)
        if not project.data_layer:
            project.data_layer = "SQL database (DDL found)"
    else:
        inferred = infer_from_queries(root, project)
        infer_pks(inferred)
        project.tables = inferred
        project.relationships = relationships_inferred(inferred)
        if inferred:
            project.findings.append(
                "No DDL/schema file found — all tables, columns and relationships are INFERRED FROM QUERY.")
