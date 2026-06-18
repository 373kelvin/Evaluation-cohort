#!/usr/bin/env python3
"""Project Insight — analyze a codebase and generate an interactive HTML report.

Usage:
    python analyze.py <path-to-project-or-zip> [-o output.html]
"""
import argparse
import os
import sys
import tempfile
import zipfile

from insight.model import Project
from insight import scan, stack, schema, features, design, render


def _prepare(path):
    """Return a directory to analyze (unzip if needed) and a display name."""
    if path.lower().endswith(".zip"):
        tmp = tempfile.mkdtemp(prefix="insight_")
        with zipfile.ZipFile(path) as z:
            z.extractall(tmp)
        name = os.path.splitext(os.path.basename(path))[0]
        # if zip contains a single top folder, use it
        entries = [os.path.join(tmp, e) for e in os.listdir(tmp)]
        dirs = [e for e in entries if os.path.isdir(e)]
        root = dirs[0] if len(dirs) == 1 and len(entries) == 1 else tmp
        return root, name
    return path, os.path.basename(os.path.abspath(path.rstrip("/\\")))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate an interactive insight report for a codebase.")
    ap.add_argument("path", help="Path to a project folder or a .zip")
    ap.add_argument("-o", "--output", default=None, help="Output HTML path (default: <name>-insight.html)")
    args = ap.parse_args(argv)

    if not os.path.exists(args.path):
        print(f"error: path not found: {args.path}", file=sys.stderr)
        return 2

    root, name = _prepare(args.path)
    project = Project(name=name)
    project.file_count = sum(1 for _ in scan.iter_files(root))

    stack.detect(project, root)
    schema.analyze_schema(project, root)
    features.detect(project, root)
    features.find_smells(project, root)
    design.analyze_design(project, root)

    out = args.output or f"{name}-insight.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(render.render(project))

    print(f"[ok] {name}")
    print(f"     stack:    {', '.join(project.languages) or '?'} / {', '.join(project.frameworks) or '?'}")
    print(f"     verdict:  {project.verdict}")
    print(f"     tables:   {len(project.tables)}  ({'DDL' if project.has_ddl else 'inferred'})")
    print(f"     features: {len(project.features)}")
    print(f"     files:    {project.file_count}")
    print(f"     -> wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
