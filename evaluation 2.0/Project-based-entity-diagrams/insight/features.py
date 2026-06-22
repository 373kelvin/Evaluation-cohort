"""Enumerate behavioral features: routes (Express/Flask/FastAPI/Django) and PHP endpoints."""
import os
import re
from .model import Feature
from .scan import iter_files, read
from .schema import _strip_comments, STOPWORDS
from . import django_scan
from . import react_scan

EXPRESS_RE = re.compile(r"\b(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*[\"'`]([^\"'`]+)", re.IGNORECASE)
FLASK_RE = re.compile(r"@\w+\.route\s*\(\s*[\"']([^\"']+)[\"'](?:.*?methods\s*=\s*\[([^\]]*)\])?", re.IGNORECASE | re.DOTALL)
FASTAPI_RE = re.compile(
    r"@(?:app|router)\.(get|post|put|delete|patch|head|options)\(\s*[\"']([^\"']+)[\"']",
    re.IGNORECASE,
)
FASTAPI_MOUNT_RE = re.compile(
    r"(?:app|router)\.mount\s*\(\s*[\"']([^\"']+)[\"']",
    re.IGNORECASE,
)
PHP_ACTION_RE = re.compile(r"isset\s*\(\s*\$_(?:POST|GET|REQUEST)\s*\[\s*[\"'](\w+)[\"']", re.IGNORECASE)

OP_RES = [
    ("INSERT", re.compile(r"INSERT\s+INTO\s+[`\"]?(\w+)", re.IGNORECASE)),
    ("UPDATE", re.compile(r"\bUPDATE\s+[`\"]?(\w+)", re.IGNORECASE)),
    ("DELETE", re.compile(r"DELETE\s+FROM\s+[`\"]?(\w+)", re.IGNORECASE)),
    ("SELECT", re.compile(r"\bFROM\s+[`\"]?(\w+)", re.IGNORECASE)),
]


def _line_of(text, idx):
    return text.count("\n", 0, idx) + 1


def _ops_in(segment):
    ops = []
    for label, rx in OP_RES:
        for m in rx.finditer(segment):
            tbl = m.group(1)
            if tbl.lower() in STOPWORDS:
                continue
            tag = f"{label} {tbl}"
            if tag not in ops:
                ops.append(tag)
    return ops


def _role(text):
    t = text.lower()
    if any(k in t for k in ("login", "signup", "register", "session", "auth", "password", "logout")):
        return "auth"
    if any(k in t for k in ("admin", "add_course", "delete", "fetch_courses", "allocation_detail")):
        return "admin"
    if any(k in t for k in ("student", "preference", "alloc", "get_courses", "seat", "diagnose", "appt")):
        return "student"
    return "general"


def detect(project, root):
    feats = []

    for ap, rel in iter_files(root):
        text = read(ap)
        if not text:
            continue

        if rel.endswith((".js", ".ts")):
            matches = list(EXPRESS_RE.finditer(text))
            for i, m in enumerate(matches):
                verb, path = m.group(1).upper(), m.group(2)
                start = m.start()
                end = matches[i + 1].start() if i + 1 < len(matches) else min(len(text), start + 1500)
                ops = _ops_in(_strip_comments(text[start:end]))
                detail = ("touches " + ", ".join(ops)) if ops else "request handler"
                feats.append(Feature(name=f"{verb} {path}", role=_role(path + " " + text[start:end]),
                                     detail=detail, source=f"{rel}:{_line_of(text, start)}", http=verb, ops=ops))

        elif rel.endswith(".py"):
            for m in FLASK_RE.finditer(text):
                path = m.group(1)
                methods = (m.group(2) or "GET").replace("'", "").replace('"', "").strip()
                start = m.start()
                seg = text[start:start + 1500]
                ops = _ops_in(_strip_comments(seg))
                detail = ("touches " + ", ".join(ops)) if ops else "request handler"
                feats.append(Feature(name=f"{methods} {path}", role=_role(path + " " + seg),
                                     detail=detail, source=f"{rel}:{_line_of(text, start)}", http=methods, ops=ops))

            for m in FASTAPI_RE.finditer(text):
                verb, path = m.group(1).upper(), m.group(2)
                start = m.start()
                seg = text[start:start + 1500]
                ops = _ops_in(_strip_comments(seg))
                detail = ("touches " + ", ".join(ops)) if ops else "FastAPI route handler"
                feats.append(Feature(name=f"{verb} {path}", role=_role(path + " " + seg),
                                     detail=detail, source=f"{rel}:{_line_of(text, start)}", http=verb, ops=ops))

            for m in FASTAPI_MOUNT_RE.finditer(text):
                path = m.group(1)
                feats.append(Feature(name=f"GET {path}", role="general",
                                     detail="static files mount", source=f"{rel}:{_line_of(text, m.start())}",
                                     http="GET", ops=[]))

        elif rel.endswith(".php"):
            ops = _ops_in(_strip_comments(text))
            if not ops and "$_" not in text:
                continue  # not a behavioral endpoint
            actions = sorted(set(PHP_ACTION_RE.findall(text)))
            bits = []
            if actions:
                bits.append("actions: " + ", ".join(actions))
            if ops:
                bits.append("SQL: " + ", ".join(ops))
            if "mail->send" in text.lower() or "phpmailer" in text.lower():
                bits.append("sends email")
            detail = " · ".join(bits) if bits else "PHP endpoint"
            feats.append(Feature(name=os.path.basename(rel), role=_role(rel + " " + text[:400]),
                                 detail=detail, source=f"{rel}:1", http="HTTP", ops=ops))

    # entry points heuristic
    entries = []
    for ap, rel in iter_files(root):
        base = os.path.basename(rel).lower()
        if base in ("app.js", "index.js", "server.js", "main.py", "app.py", "manage.py",
                    "login.php", "index.php", "www"):
            entries.append(rel)
    project.entry_points = sorted(set(entries))[:8]

    feats.sort(key=lambda f: (f.role, f.source))
    project.features = feats
    django_scan.detect_django_routes(project, root)
    react_scan.detect_react_routes(project, root)
    react_scan.detect_json_server_routes(project, root)


def find_smells(project, root):
    f = project.findings
    inter = plain = smtp = db_cred = empty = False
    JS_PWD = re.compile(r"""password\s*:\s*["']([^"']*)["']""", re.IGNORECASE)   # JS/JSON conn field
    PHP_PWD = re.compile(r"""\$password\s*=\s*["']([^"']*)["']""", re.IGNORECASE) # PHP conn var
    MAIL_PWD = re.compile(r"""->Password\s*=\s*["']([^"']{3,})["']""")            # PHPMailer/Nodemailer
    for ap, rel in iter_files(root):
        text = read(ap)
        low = text.lower()
        if re.search(r"(query|sql|statement)\s*=.*\$\w+", text) or re.search(r"\$\{[^}]+\}.*(from|where|insert|select)", low):
            inter = True
        is_mailer = ("smtp" in low or "phpmailer" in low or "->host" in low or "gmail.com" in low)
        is_conn = any(k in low for k in ("createconnection", "new mysqli", "mysqli_connect",
                                         "mysql_connect", "createpool", "psycopg2.connect"))
        if is_conn:
            for v in JS_PWD.findall(text) + PHP_PWD.findall(text):
                if len(v) == 0:
                    empty = True
                elif len(v) >= 3:
                    db_cred = True
        if is_mailer and MAIL_PWD.search(text):
            smtp = True
        if "password" in low and ("insert into" in low or "select * from" in low or "where email" in low):
            plain = True
    if inter:
        f.append("SQL appears to be built by string interpolation of variables → risk of SQL injection.")
    if plain:
        f.append("Passwords appear to be stored/compared as plain text (no hashing).")
    if db_cred:
        f.append("Hardcoded database credentials in source (a password literal in a DB connection).")
    if empty:
        f.append("A database connection uses an empty password (default dev credentials).")
    if smtp:
        f.append("Hardcoded SMTP/email credentials detected in source — rotate them (values not reproduced).")
