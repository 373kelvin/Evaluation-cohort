"""B1 artifact inventory: classes, models, services, configs, utilities."""
import os
import re
from dataclasses import dataclass, field
from typing import List

from .scan import iter_files, read

PY_CLASS = re.compile(r"^class\s+(\w+)", re.MULTILINE)
PY_DEF = re.compile(r"^def\s+(\w+)", re.MULTILINE)
RUST_STRUCT = re.compile(r"^struct\s+(\w+)", re.MULTILINE)
RUST_FN = re.compile(r"^fn\s+(\w+)", re.MULTILINE)
JS_FN = re.compile(r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>)")

CONFIG_NAMES = {
    "cargo.toml", "package.json", "requirements.txt", "pyproject.toml",
    "dockerfile", "docker-compose.yml", "docker-compose.yaml",
    ".gitignore", "conftest.py", "run.sh",
}


@dataclass
class Artifact:
    kind: str
    name: str
    source: str
    detail: str = ""


@dataclass
class Inventory:
    artifacts: List[Artifact] = field(default_factory=list)

    def by_kind(self):
        groups = {}
        for a in self.artifacts:
            groups.setdefault(a.kind, []).append(a)
        return groups


def _line_of(text, idx):
    return text.count("\n", 0, idx) + 1


def detect(root) -> Inventory:
    inv = Inventory()

    for ap, rel in iter_files(root):
        base = os.path.basename(rel).lower()
        if base in CONFIG_NAMES or rel.endswith((".toml", ".yaml", ".yml", ".env.example")):
            inv.artifacts.append(Artifact("config", base, rel, "configuration file"))

        text = read(ap)
        if not text:
            continue

        if rel.endswith(".py"):
            for m in PY_CLASS.finditer(text):
                inv.artifacts.append(Artifact(
                    "class", m.group(1), f"{rel}:{_line_of(text, m.start())}", "Python class"))
            for m in PY_DEF.finditer(text):
                name = m.group(1)
                if not name.startswith("_"):
                    inv.artifacts.append(Artifact(
                        "function", name, f"{rel}:{_line_of(text, m.start())}", "Python function"))

        elif rel.endswith(".rs"):
            for m in RUST_STRUCT.finditer(text):
                inv.artifacts.append(Artifact(
                    "struct", m.group(1), f"{rel}:{_line_of(text, m.start())}", "Rust struct"))
            for m in RUST_FN.finditer(text):
                name = m.group(1)
                if name not in ("main",):
                    inv.artifacts.append(Artifact(
                        "function", name, f"{rel}:{_line_of(text, m.start())}", "Rust function"))
            if "fn main" in text:
                inv.artifacts.append(Artifact("entrypoint", "main", rel, "Rust CLI entry"))

        elif rel.endswith((".js", ".ts")):
            if "worker" in base or "server" in base or base == "app.js":
                inv.artifacts.append(Artifact("service", os.path.basename(rel), rel, "Node.js process"))
            for m in JS_FN.finditer(text):
                name = m.group(1) or m.group(2)
                if name:
                    inv.artifacts.append(Artifact(
                        "function", name, f"{rel}:{_line_of(text, m.start())}", "JavaScript function"))

        low = rel.lower()
        if "test" in low or low.endswith("_test.py") or "/tests/" in low.replace("\\", "/"):
            inv.artifacts.append(Artifact("test", os.path.basename(rel), rel, "test file"))
        if "model" in low or "schema" in low:
            inv.artifacts.append(Artifact("model", os.path.basename(rel), rel, "data model / schema"))

    inv.artifacts.sort(key=lambda a: (a.kind, a.source))
    return inv


def to_markdown(inv: Inventory, project_name: str) -> str:
    lines = [f"# Artifact Inventory — {project_name}", ""]
    groups = inv.by_kind()
    summary = ", ".join(f"{k}: {len(v)}" for k, v in sorted(groups.items()))
    lines.append(f"**Summary:** {len(inv.artifacts)} artifacts ({summary})")
    lines.append("")
    for kind in sorted(groups):
        lines.append(f"## {kind.title()}s")
        lines.append("")
        lines.append("| Name | Source | Detail |")
        lines.append("|------|--------|--------|")
        for a in groups[kind]:
            lines.append(f"| `{a.name}` | `{a.source}` | {a.detail} |")
        lines.append("")
    return "\n".join(lines)
