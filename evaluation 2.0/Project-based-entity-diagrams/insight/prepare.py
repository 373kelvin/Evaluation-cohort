"""Prepare scan root from folder or zip (shared by analyze.py and inventory.py)."""
from __future__ import annotations

import os
import tempfile
import zipfile


def prepare(path: str) -> tuple[str, str]:
    """Return (root_dir, display_name)."""
    if path.lower().endswith(".zip"):
        tmp = tempfile.mkdtemp(prefix="insight_")
        with zipfile.ZipFile(path) as zf:
            zf.extractall(tmp)
        name = os.path.splitext(os.path.basename(path))[0]
        entries = [os.path.join(tmp, e) for e in os.listdir(tmp)]
        dirs = [e for e in entries if os.path.isdir(e)]
        root = dirs[0] if len(dirs) == 1 and len(entries) == 1 else tmp
        return root, name
    root = os.path.abspath(path.rstrip("/\\"))
    return root, os.path.basename(root)
