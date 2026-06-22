"""Derive software-design views from what the code actually contains:
   system architecture, a representative execution/data flow, and a component map."""
import os
from .scan import iter_files, read

FRONTEND_FWS = {"React", "Vue", "Angular", "Next.js"}
BACKEND_FWS = {"Express", "Koa", "Fastify", "Flask", "Django", "FastAPI", "Laravel"}


def _has_html(root):
    for _, rel in iter_files(root):
        if rel.endswith(".html"):
            return True
    return False


def _mailer(project):
    return any("mail" in f.lower() or f == "PHPMailer" for f in project.frameworks) \
        or any("smtp" in x.lower() or "email" in x.lower() for x in project.findings)


def build_architecture(project, root):
    fws = set(project.frameworks)
    frontend = (FRONTEND_FWS & fws)
    backend = (BACKEND_FWS & fws)
    is_php = "PHP" in project.languages
    db = project.db_name or (project.data_layer if project.data_layer else "Database")

    lines = ["flowchart LR", '    User["User"]']
    last = "User"

    if frontend:
        fe = " / ".join(sorted(frontend))
        lines.append(f'    FE["Frontend: {fe}"]')
        lines.append(f"    {last} --> FE")
        last = "FE"
    elif _has_html(root):
        lines.append('    FE["Frontend: HTML/CSS pages"]')
        lines.append(f"    {last} --> FE")
        last = "FE"

    if backend:
        be = " / ".join(sorted(backend))
        lines.append(f'    API["Backend: {be}"]')
    elif is_php:
        lines.append('    API["Backend: PHP scripts"]')
    else:
        lines.append('    API["Application"]')
    lines.append(f'    {last} -->|"HTTP"| API')

    if project.tables:
        lines.append(f'    DB[("{db}")]')
        lines.append('    API -->|"SQL"| DB')

    if _mailer(project):
        lines.append('    MAIL["Email / SMTP"]')
        lines.append('    API -->|"send"| MAIL')

    return "\n".join(lines)


def build_execution(project):
    """Sequence diagram for the most write-heavy endpoint (best illustrates the flow)."""
    if not project.features:
        return "", ""
    feat = max(project.features, key=lambda f: (len(f.ops), len(f.detail)))
    if not feat.ops:
        # fall back to any feature that touches the DB
        with_ops = [f for f in project.features if f.ops]
        if not with_ops:
            return "", ""
        feat = with_ops[0]

    handler = os.path.basename(feat.source.split(":")[0])
    db = project.db_name or "Database"
    lines = ["sequenceDiagram",
             "    participant C as Client",
             f"    participant S as {handler}",
             f"    participant D as {db}"]
    lines.append(f"    C->>S: {feat.name}")
    for op in feat.ops[:6]:
        lines.append(f"    S->>D: {op}")
        lines.append("    D-->>S: result")
    lines.append("    S-->>C: response")
    return feat.name, "\n".join(lines)


ROLE_HINTS = [
    ("frontend", "Frontend"), ("client", "Frontend"), ("public", "Frontend / static"),
    ("backend", "Backend / API"), ("server", "Backend / API"), ("api", "Backend / API"),
    ("routes", "Routes / controllers"), ("controllers", "Routes / controllers"),
    ("models", "Data models"), ("migrations", "DB migrations"),
    ("views", "Templates / views"), ("src", "Source"), ("test", "Tests"),
]


def build_components(project, root):
    """Immediate sub-areas of the project that contain source, with a guessed role."""
    counts = {}
    for _, rel in iter_files(root):
        top = rel.split("/")[0] if "/" in rel else "(root)"
        counts[top] = counts.get(top, 0) + 1
    comps = []
    for name, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        role = ""
        low = name.lower()
        for hint, label in ROLE_HINTS:
            if hint in low:
                role = label
                break
        comps.append((name, role or "module", n))
    return comps[:12]


def analyze_design(project, root):
    project.architecture = build_architecture(project, root)
    project.exec_title, project.exec_map = build_execution(project)
    project.components = build_components(project, root)
