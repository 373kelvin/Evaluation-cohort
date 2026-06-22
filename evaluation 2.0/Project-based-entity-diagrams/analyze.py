#!/usr/bin/env python3
"""Project Insight — analyze a codebase and generate an interactive HTML report.

Usage:
    python analyze.py <path-to-project-or-zip> [-o output.html]
"""
import argparse
import os
import sys

from insight.model import Project
from insight.prepare import prepare
from insight import scan, stack, schema, features, design, render, coverage


def _prepare(path):
    """Backward-compatible wrapper."""
    return prepare(path)


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
    coverage.annotate(project)

    out = args.output or f"{name}-insight.html"
    out_dir = os.path.dirname(out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
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
