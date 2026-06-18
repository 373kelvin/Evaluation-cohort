"""Walk a project tree, skipping dependency/build noise."""
import os

IGNORE_DIRS = {
    "node_modules", "vendor", "venv", "env", ".venv", ".conda", "site-packages",
    ".git", "dist", "build", "__pycache__", ".next", ".idea", ".vscode",
    "logo", "pictures", "images", "screenshots", "img",
}
TEXT_EXT = {
    ".php", ".js", ".ts", ".jsx", ".tsx", ".py", ".sql", ".json", ".html",
    ".java", ".go", ".rb", ".cs", ".env",
}


def iter_files(root):
    """Yield (abspath, relpath) for source files, skipping noise dirs."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d.lower() not in IGNORE_DIRS]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in TEXT_EXT:
                ap = os.path.join(dirpath, fn)
                rel = os.path.relpath(ap, root).replace("\\", "/")
                yield ap, rel


def read(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""
