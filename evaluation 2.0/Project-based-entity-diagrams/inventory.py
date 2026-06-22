#!/usr/bin/env python3
"""B1 — Generate a markdown artifact inventory for a codebase.

Usage:
    python inventory.py <path-to-project> [-o outputs/b1-artifact-inventory/report.md]
"""
import argparse
import os
import sys

from insight.prepare import prepare
from insight.artifacts import detect, to_markdown


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate B1 artifact inventory (markdown).")
    ap.add_argument("path", help="Path to project folder or .zip")
    ap.add_argument("-o", "--output", default=None, help="Output markdown path")
    args = ap.parse_args(argv)

    if not os.path.exists(args.path):
        print(f"error: path not found: {args.path}", file=sys.stderr)
        return 2

    root, name = prepare(args.path)
    inv = detect(root)
    md = to_markdown(inv, name)

    out = args.output or f"outputs/b1-artifact-inventory/{name}-inventory.md"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(md)

    groups = inv.by_kind()
    print(f"[ok] {name}: {len(inv.artifacts)} artifacts")
    for kind, items in sorted(groups.items()):
        print(f"     {kind}: {len(items)}")
    print(f"     -> wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
