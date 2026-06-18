"""Detect languages, frameworks, run commands and data layer from manifests."""
import json
import os
from .scan import read

JS_FRAMEWORKS = {
    "express": "Express", "react": "React", "next": "Next.js",
    "vue": "Vue", "@angular/core": "Angular", "koa": "Koa", "fastify": "Fastify",
}
JS_DB = {"mysql": "MySQL", "mysql2": "MySQL", "pg": "PostgreSQL",
         "mongoose": "MongoDB", "sqlite3": "SQLite", "sequelize": "Sequelize (ORM)",
         "prisma": "Prisma (ORM)", "typeorm": "TypeORM (ORM)"}
PY_FRAMEWORKS = {"flask": "Flask", "django": "Django", "fastapi": "FastAPI"}
PY_DB = {"sqlalchemy": "SQLAlchemy (ORM)", "psycopg2": "PostgreSQL",
         "mysqlclient": "MySQL", "pymysql": "MySQL", "sqlite3": "SQLite"}


def _find(root, name):
    for dp, dn, fns in os.walk(root):
        dn[:] = [d for d in dn if d not in ("node_modules", "vendor", "venv", ".git")]
        if name in fns:
            return os.path.join(dp, name)
    return None


def detect(project, root):
    langs, fws, dbs, runs, entries = set(), set(), set(), [], []

    # --- Node / JS ---
    for pj in _all(root, "package.json"):
        try:
            data = json.loads(read(pj))
        except Exception:
            continue
        rel = os.path.relpath(pj, root).replace("\\", "/")
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        if deps:
            langs.add("JavaScript")
        for k, v in JS_FRAMEWORKS.items():
            if k in deps:
                fws.add(v)
        for k, v in JS_DB.items():
            if k in deps:
                dbs.add(v)
        scripts = data.get("scripts", {})
        if "start" in scripts:
            folder = os.path.dirname(rel) or "."
            runs.append((f"cd {folder} && npm install && npm start", f"{rel} (scripts.start)"))

    # --- PHP ---
    cj = _find(root, "composer.json")
    if cj:
        langs.add("PHP")
        try:
            data = json.loads(read(cj))
            req = data.get("require", {})
            for k in req:
                if "phpmailer" in k:
                    fws.add("PHPMailer")
                if "laravel" in k:
                    fws.add("Laravel")
        except Exception:
            pass
        runs.append(("Serve with PHP/Apache (e.g. XAMPP) from the web root", "composer.json present"))

    # --- Python ---
    for req in _all(root, "requirements.txt"):
        langs.add("Python")
        txt = read(req).lower()
        for k, v in PY_FRAMEWORKS.items():
            if k in txt:
                fws.add(v)
        for k, v in PY_DB.items():
            if k in txt:
                dbs.add(v)
        if "flask" in txt:
            runs.append(("pip install -r requirements.txt && flask run", "requirements.txt (flask)"))

    project.languages = sorted(langs)
    project.frameworks = sorted(fws)
    project.how_to_run = [f"{c}  —  {s}" for c, s in runs]
    project.verdict = _verdict(langs, fws, dbs)
    if dbs:
        project.data_layer = ", ".join(sorted(dbs))
    return dbs


def _all(root, name):
    out = []
    for dp, dn, fns in os.walk(root):
        dn[:] = [d for d in dn if d not in ("node_modules", "vendor", "venv", ".git", ".conda")]
        if name in fns:
            out.append(os.path.join(dp, name))
    return out


def _verdict(langs, fws, dbs):
    has_front = bool({"React", "Vue", "Angular", "Next.js"} & fws)
    has_back = bool({"Express", "Flask", "Django", "FastAPI", "Koa", "Laravel"} & fws) or "PHP" in langs
    if has_front and has_back:
        return "Full-stack web application"
    if "PHP" in langs:
        return "Server-rendered PHP web application"
    if {"Flask", "Django", "FastAPI"} & fws:
        return "Python web service / API"
    if has_back:
        return "Backend web service"
    return "Application"
