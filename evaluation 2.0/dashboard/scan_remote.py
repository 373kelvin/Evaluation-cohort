"""Download GitHub archives / prepare zip paths for Project Insight."""
from __future__ import annotations

import re
import tempfile
import time
import zipfile
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
SCANNER = ROOT / "Project-based-entity-diagrams"


class GitHubDownloadError(Exception):
    """Could not download a public GitHub repository archive."""


def normalize_github_url(url: str) -> str:
    """Accept common GitHub URL shapes (with .git, www, git@, extra spaces)."""
    url = url.strip()
    if url.startswith("git@"):
        m = re.match(r"git@github\.com:([^/]+)/([^/\s#?]+)", url)
        if m:
            return f"https://github.com/{m.group(1)}/{m.group(2).removesuffix('.git')}"
    if not url.startswith("http"):
        url = "https://" + url.lstrip("/")
    return url.rstrip("/")


def parse_github_url(url: str) -> tuple[str, str, str | None]:
    """Return owner, repo, optional branch from a GitHub URL."""
    url = normalize_github_url(url)
    m = re.match(r"https?://(?:www\.)?github\.com/([^/]+)/([^/#?]+)", url)
    if not m:
        raise ValueError(
            "Use a public GitHub link like https://github.com/owner/repo "
            "(.git at the end is OK too)"
        )
    owner, repo = m.group(1), m.group(2).removesuffix(".git")
    branch = None
    branch_m = re.search(r"/tree/([^/]+)", url)
    if branch_m:
        branch = branch_m.group(1)
    return owner, repo, branch


def prepare_scan_root(source_path: Path) -> tuple[Path, tempfile.TemporaryDirectory[str] | None]:
    """If source is a zip, extract to a temp folder for B1 + B2."""
    if source_path.suffix.lower() != ".zip":
        return source_path, None
    tmp = tempfile.TemporaryDirectory(prefix="insight_scan_")
    with zipfile.ZipFile(source_path) as zf:
        zf.extractall(tmp.name)
    entries = list(Path(tmp.name).iterdir())
    dirs = [e for e in entries if e.is_dir()]
    root = dirs[0] if len(dirs) == 1 and len(entries) == 1 else Path(tmp.name)
    return root, tmp


def github_slug(owner: str, repo: str) -> str:
    return f"github-{owner}-{repo}"[:48]


def _resolve_default_branch(owner: str, repo: str, timeout: float = 15.0) -> str:
    """Ask GitHub API for the repo default branch (public, no token)."""
    api = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "Evaluation20-ProjectInsight"}
    try:
        r = httpx.get(api, headers=headers, timeout=timeout, follow_redirects=True)
        if r.status_code == 200:
            return r.json().get("default_branch") or "main"
        if r.status_code == 404:
            raise GitHubDownloadError(
                f"Repository {owner}/{repo} not found — check spelling or use a public repo URL."
            )
        if r.status_code == 403:
            raise GitHubDownloadError(
                "GitHub rate limit — wait a minute or upload a .zip instead (Code → Download ZIP)."
            )
    except httpx.HTTPError as e:
        raise GitHubDownloadError(f"Could not reach GitHub API: {e}") from e
    return "main"


def _archive_urls(owner: str, repo: str, branch: str) -> list[str]:
    """Zip download URLs to try (new + legacy formats)."""
    b = branch
    return [
        f"https://github.com/{owner}/{repo}/archive/refs/heads/{b}.zip",
        f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{b}",
        f"https://github.com/{owner}/{repo}/archive/{b}.zip",
    ]


def download_github_zip(url: str, dest: Path, timeout: float = 120.0) -> tuple[Path, str, str]:
    """
    Download repo zip. Returns (path, slug, branch_used).
    Tries API default branch, then main/master/develop fallbacks.
    """
    owner, repo, branch_from_url = parse_github_url(url)
    slug = github_slug(owner, repo)
    dest.parent.mkdir(parents=True, exist_ok=True)

    branches_to_try: list[str] = []
    if branch_from_url:
        branches_to_try.append(branch_from_url)
    else:
        try:
            branches_to_try.append(_resolve_default_branch(owner, repo))
        except GitHubDownloadError:
            raise
    for fallback in ("main", "master", "develop"):
        if fallback not in branches_to_try:
            branches_to_try.append(fallback)

    last_err = ""
    for branch in branches_to_try:
        for zip_url in _archive_urls(owner, repo, branch):
            try:
                with httpx.stream(
                    "GET", zip_url, follow_redirects=True, timeout=timeout,
                    headers={"User-Agent": "Evaluation20-ProjectInsight"},
                ) as r:
                    if r.status_code == 404:
                        last_err = f"404 for branch '{branch}'"
                        continue
                    r.raise_for_status()
                    with dest.open("wb") as f:
                        for chunk in r.iter_bytes():
                            f.write(chunk)
                if dest.stat().st_size < 500:
                    last_err = "Download too small — empty or blocked"
                    continue
                return dest, slug, branch
            except httpx.HTTPStatusError as e:
                last_err = f"HTTP {e.response.status_code} for branch '{branch}'"
            except httpx.HTTPError as e:
                last_err = str(e)

    raise GitHubDownloadError(
        f"Could not download {owner}/{repo}. Tried branches: {', '.join(branches_to_try)}. "
        f"Last error: {last_err}. Tip: paste the full tree URL with branch, or upload a .zip."
    )


def github_archive_url(url: str) -> tuple[str, str]:
    """Legacy helper — slug + first archive URL (prefer download_github_zip)."""
    owner, repo, branch = parse_github_url(url)
    branch = branch or "main"
    slug = github_slug(owner, repo)
    return _archive_urls(owner, repo, branch)[0], slug


def save_uploaded_zip(content: bytes, filename: str) -> Path:
    safe = re.sub(r"[^\w.\-]", "-", Path(filename).name)[:80] or "upload.zip"
    if not safe.lower().endswith(".zip"):
        safe += ".zip"
    tmp_dir = ROOT / "outputs" / "uploads"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    path = tmp_dir / f"{int(time.time())}-{safe}"
    path.write_bytes(content)
    return path


def run_insight_scan(source_path: Path, slug: str, source_label: str = "") -> dict:
    """Run B1 inventory + B2 analyze on a folder or zip path."""
    import subprocess

    t0 = time.time()
    steps: list[dict] = []

    if not source_path.exists():
        return {"ok": False, "stderr": f"Path not found: {source_path}", "steps": []}

    size_kb = round(source_path.stat().st_size / 1024, 1) if source_path.is_file() else 0
    label = source_label or source_path.name
    steps.append({
        "label": "Receive source",
        "status": "pass",
        "detail": f"{label} ({size_kb} KB)" if size_kb else label,
    })

    out_inv = ROOT / "outputs" / "b1-artifact-inventory" / f"{slug}-inventory.md"
    out_html = ROOT / "outputs" / "b2-endpoint-map" / f"{slug}-insight.html"
    out_inv.parent.mkdir(parents=True, exist_ok=True)
    out_html.parent.mkdir(parents=True, exist_ok=True)

    inv_script = SCANNER / "inventory.py"
    analyze_script = SCANNER / "analyze.py"

    tmp_dir: tempfile.TemporaryDirectory[str] | None = None
    try:
        scan_root, tmp_dir = prepare_scan_root(source_path)
        target = str(scan_root)

        inv = subprocess.run(
            ["python3", str(inv_script), target, "-o", str(out_inv)],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=ROOT,
        )
        inv_ok = inv.returncode == 0 and out_inv.is_file()
        inv_line = (inv.stdout or inv.stderr or "").strip().splitlines()
        steps.append({
            "label": "B1 — file inventory",
            "status": "pass" if inv_ok else "fail",
            "detail": inv_line[-1][:120] if inv_line else ("inventory.md written" if inv_ok else (inv.stderr or inv.stdout or "")[:120]),
        })

        analyze = subprocess.run(
            ["python3", str(analyze_script), target, "-o", str(out_html)],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=ROOT,
        )
    finally:
        if tmp_dir is not None:
            tmp_dir.cleanup()
    analyze_ok = analyze.returncode == 0 and out_html.is_file()
    analyze_lines = (analyze.stdout or "").strip().splitlines()
    features = tables = files = "?"
    for line in analyze_lines:
        if "features:" in line:
            features = line.split("features:")[-1].strip()
        if "tables:" in line:
            tables = line.split("tables:")[-1].strip().split()[0]
        if "files:" in line:
            files = line.split("files:")[-1].strip()

    steps.append({
        "label": "B2 — route map + diagram",
        "status": "pass" if analyze_ok else "fail",
        "detail": f"{features} routes · {tables} tables · {files} files" if analyze_ok else (analyze.stderr or analyze.stdout or "")[:120],
    })

    html_kb = round(out_html.stat().st_size / 1024, 1) if out_html.is_file() else 0
    steps.append({
        "label": "Save HTML report",
        "status": "pass" if analyze_ok else "fail",
        "detail": f"outputs/b2-endpoint-map/{slug}-insight.html ({html_kb} KB)" if analyze_ok else "Report not created",
    })

    preview = out_inv.read_text(encoding="utf-8")[:1500] if out_inv.exists() else ""
    ok = analyze_ok
    elapsed = round(time.time() - t0, 1)
    summary = (
        f"Scan complete in {elapsed}s — report at /api/reports/{slug}"
        if ok
        else f"Scan failed after {elapsed}s"
    )
    if ok and not inv_ok:
        summary = f"Report ready in {elapsed}s (B1 inventory skipped partial — B2 OK)"
    return {
        "ok": ok,
        "code": analyze.returncode,
        "slug": slug,
        "output": str(out_html.relative_to(ROOT)) if out_html.exists() else "",
        "inventory": str(out_inv.relative_to(ROOT)) if out_inv.exists() else "",
        "report_url": f"/api/reports/{slug}",
        "stdout": (analyze.stdout or "")[-2000:],
        "stderr": (analyze.stderr or inv.stderr or "")[-1500:],
        "preview": preview,
        "action": "analyze",
        "steps": steps,
        "summary": summary,
        "elapsed_s": elapsed,
    }
