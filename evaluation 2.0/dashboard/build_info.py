"""Dashboard build metadata — bump VERSION / BUILD_LABEL when you ship UI fixes."""

from __future__ import annotations

# Increment VERSION for every deploy you want to verify in the browser corner.
VERSION = "2.0.22"
BUILD_LABEL = "open-url-json-api"
BUILD_DATE = "2026-06-22"

CHANGELOG: list[str] = [
    "Open buttons use JSON /api/open-url (no redirect/CORS failures)",
    "Fix Open API/Web buttons (CORS redirect bug) + scan report HEAD→GET",
    "Multi-stack scanner: Django, FastAPI, Flask, Express, SQL, SQLAlchemy, Prisma",
    "Reports show Scanner coverage — honest gaps when something is missing",
    "GitHub scan: unzip before B1+B2, .git URLs accepted",
    "Build badge always visible in corner + footer (no JS required)",
    "GitHub scan resolves default branch (main/master/develop)",
    "Scan failures show detail on Download step only",
    "Corner build badge + password dev activity log",
    "Zip/GitHub scan progress toasts + drag-drop",
    "Report viewer + Your Reports gallery",
    "One-click Open links (no raw localhost in UI)",
]


def build_info() -> dict:
    return {
        "version": VERSION,
        "label": BUILD_LABEL,
        "date": BUILD_DATE,
        "display": f"v{VERSION}",
        "full": f"v{VERSION} · {BUILD_LABEL}",
        "changelog": CHANGELOG,
    }
