"""Detect languages, frameworks, run commands and data layer from manifests."""
import json
import os
import re
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


def _load_package_json(path):
    text = read(path)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        fixed = re.sub(r",\s*}", "}", text)
        fixed = re.sub(r",\s*]", "]", fixed)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass
    deps = {}
    scripts = {}
    for m in re.finditer(r'"([^"]+)":\s*"([^"]+)"', text):
        k, v = m.group(1), m.group(2)
        if k in ("start", "start-server", "build", "test"):
            scripts[k] = v
        elif k in JS_FRAMEWORKS or k in JS_DB or k in ("react", "react-dom", "react-router-dom", "json-server"):
            deps[k] = v
    return {"dependencies": deps, "scripts": scripts}


def detect(project, root):
    langs, fws, dbs, runs, entries = set(), set(), set(), [], []

    # --- Node / JS ---
    for pj in _all(root, "package.json"):
        try:
            data = _load_package_json(pj)
        except Exception:
            continue
        rel = os.path.relpath(pj, root).replace("\\", "/")
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        if deps:
            langs.add("JavaScript")
        if "react" in deps or "react-dom" in deps:
            fws.add("React")
        if "react-router-dom" in deps:
            fws.add("React Router")
        if "json-server" in deps:
            fws.add("json-server")
        for k, v in JS_FRAMEWORKS.items():
            if k in deps:
                fws.add(v)
        for k, v in JS_DB.items():
            if k in deps:
                dbs.add(v)
        scripts = data.get("scripts", {})
        folder = os.path.dirname(rel) or "."
        if "start" in scripts:
            runs.append((f"cd {folder} && npm install && npm start", f"{rel} (scripts.start)"))
        if "start-server" in scripts:
            runs.append((f"cd {folder} && npm run start-server", f"{rel} (json-server mock API)"))

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
        if "django" in txt:
            runs.append(("pip install -r requirements.txt && python manage.py runserver", "requirements.txt (django)"))
        if "fastapi" in txt or "uvicorn" in txt:
            folder = os.path.relpath(os.path.dirname(req), root).replace("\\", "/") or "."
            runs.append((f"cd {folder} && pip install -r requirements.txt && uvicorn app.main:app --reload", "requirements.txt (fastapi)"))

    mp = _find(root, "manage.py")
    if mp and "Django" in fws:
        folder = os.path.relpath(os.path.dirname(mp), root).replace("\\", "/") or "."
        cmd = f"cd {folder} && pip install -r requirements.txt && python manage.py runserver"
        if not any("manage.py" in s for _, s in runs):
            runs.append((cmd, "manage.py"))

    project.languages = sorted(langs)
    project.frameworks = sorted(fws)
    project.how_to_run = [f"{c}  —  {s}" for c, s in runs]
    project.verdict = _verdict(langs, fws, dbs)
    if dbs:
        project.data_layer = ", ".join(sorted(dbs))
    # README hints (MariaDB college projects often document DB only in README)
    for rp in _all(root, "README.md"):
        txt = read(rp).lower()
        if "mariadb" in txt or "mysql" in txt:
            if not project.data_layer:
                project.data_layer = "MariaDB/MySQL (documented in README)"
            dbs.add("MariaDB")
        break
    if dbs and not project.data_layer:
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
