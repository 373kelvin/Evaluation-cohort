/**
 * Corner build badge + password-protected activity log (passwords: 2509 / jaico123).
 * Loads early — patches fetch and captures clicks globally.
 */
(function () {
  const STORAGE_KEY = "eval20-dev-events";
  const UNLOCK_KEY = "eval20-dev-unlocked";
  const MAX_CLIENT = 600;
  const PASSWORDS = new Set(["2509", "jaico123"]);

  let build = { version: "?", label: "loading", display: "v?" };
  let panelOpen = false;
  let refreshTimer = null;

  function ts() {
    return new Date().toISOString();
  }

  function loadClientEvents() {
    try {
      return JSON.parse(sessionStorage.getItem(STORAGE_KEY) || "[]");
    } catch {
      return [];
    }
  }

  function saveClientEvents(events) {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(events.slice(-MAX_CLIENT)));
    } catch (_) { /* quota */ }
  }

  function clientLog(category, event, detail) {
    const entry = { ts: ts(), category, event, detail, source: "browser" };
    const events = loadClientEvents();
    events.push(entry);
    saveClientEvents(events);
    if (panelOpen && isUnlocked()) renderLog();
    return entry;
  }

  window.DevConsole = { log: clientLog };

  function isUnlocked() {
    return sessionStorage.getItem(UNLOCK_KEY) === "1";
  }

  function setUnlocked(ok) {
    if (ok) sessionStorage.setItem(UNLOCK_KEY, "1");
    else sessionStorage.removeItem(UNLOCK_KEY);
  }

  function el(tag, cls, html) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  }

  function fmtTime(isoOrTs) {
    try {
      const d = typeof isoOrTs === "number" ? new Date(isoOrTs * 1000) : new Date(isoOrTs);
      return d.toLocaleTimeString() + "." + String(d.getMilliseconds()).padStart(3, "0");
    } catch {
      return String(isoOrTs);
    }
  }

  function detailStr(d) {
    if (d == null) return "";
    if (typeof d === "string") return d;
    try {
      return JSON.stringify(d);
    } catch {
      return String(d);
    }
  }

  function ensureUI() {
    let badge = document.getElementById("dev-badge");
    if (!badge) {
      badge = el("button", "dev-badge", build.display || "v?");
      badge.id = "dev-badge";
      badge.type = "button";
      document.body.appendChild(badge);
    }
    if (!badge.dataset.devWired) {
      badge.dataset.devWired = "1";
      badge.addEventListener("click", onBadgeClick);
    }

    if (document.getElementById("dev-overlay")) {
      updateBadge();
      return;
    }

    const overlay = el("div", "dev-overlay hidden");
    overlay.id = "dev-overlay";

    const panel = el("div", "dev-panel hidden");
    panel.id = "dev-panel";
    panel.innerHTML = `
      <div class="dev-panel-head">
        <div>
          <strong class="dev-panel-title">Dev Activity Log</strong>
          <p class="dev-panel-sub" id="dev-build-line">—</p>
        </div>
        <button type="button" class="dev-close" id="dev-close" aria-label="Close">×</button>
      </div>
      <div class="dev-auth" id="dev-auth">
        <p class="dev-auth-hint">Enter dev password to view full activity (clicks, API calls, scans).</p>
        <input type="password" id="dev-pass" class="dev-pass-input" placeholder="Password" autocomplete="off" />
        <button type="button" class="btn btn-sm btn-primary" id="dev-unlock-btn">Unlock</button>
        <p class="dev-auth-err hidden" id="dev-auth-err">Wrong password</p>
      </div>
      <div class="dev-body hidden" id="dev-body">
        <div class="dev-toolbar">
          <button type="button" class="btn btn-sm btn-secondary" id="dev-refresh">↻ Refresh</button>
          <button type="button" class="btn btn-sm btn-secondary" id="dev-export">Export</button>
          <button type="button" class="btn btn-sm btn-ghost" id="dev-clear-client">Clear browser log</button>
          <button type="button" class="btn btn-sm btn-ghost" id="dev-lock">Lock</button>
        </div>
        <details class="dev-changelog" open>
          <summary>This build</summary>
          <ul id="dev-changelog"></ul>
        </details>
        <pre class="dev-log" id="dev-log"></pre>
      </div>`;

    document.body.appendChild(overlay);
    document.body.appendChild(panel);

    overlay.addEventListener("click", closePanel);
    document.getElementById("dev-close")?.addEventListener("click", closePanel);
    document.getElementById("dev-unlock-btn")?.addEventListener("click", tryUnlock);
    document.getElementById("dev-pass")?.addEventListener("keydown", (e) => {
      if (e.key === "Enter") tryUnlock();
    });
    document.getElementById("dev-refresh")?.addEventListener("click", () => renderLog(true));
    document.getElementById("dev-export")?.addEventListener("click", exportLog);
    document.getElementById("dev-clear-client")?.addEventListener("click", () => {
      saveClientEvents([]);
      clientLog("dev", "clear_client_log");
      renderLog(true);
    });
    document.getElementById("dev-lock")?.addEventListener("click", () => {
      setUnlocked(false);
      try { sessionStorage.removeItem("eval20-dev-pass-cache"); } catch (_) { /* ignore */ }
      showAuth();
    });

    updateBadge();
  }

  let badgeClicks = 0;
  let badgeTimer = null;

  function onBadgeClick() {
    badgeClicks += 1;
    clearTimeout(badgeTimer);
    badgeTimer = setTimeout(() => { badgeClicks = 0; }, 700);
    if (badgeClicks >= 3) {
      badgeClicks = 0;
      openPanel();
    }
  }

  function updateBadge() {
    const b = document.getElementById("dev-badge");
    if (!b) return;
    b.textContent = build.display || "v?";
    b.title = `${build.full || build.display} — triple-click for dev log`;
  }

  function openPanel() {
    ensureUI();
    panelOpen = true;
    document.getElementById("dev-overlay")?.classList.remove("hidden");
    document.getElementById("dev-panel")?.classList.remove("hidden");
    const line = document.getElementById("dev-build-line");
    if (line) line.textContent = build.full || build.display;
    const cl = document.getElementById("dev-changelog");
    if (cl) {
      cl.innerHTML = (build.changelog || [])
        .map((c) => `<li>${c}</li>`)
        .join("") || "<li>No changelog entries</li>";
    }
    if (isUnlocked()) showBody();
    else showAuth();
    renderLog(true);
    if (refreshTimer) clearInterval(refreshTimer);
    refreshTimer = setInterval(() => { if (panelOpen && isUnlocked()) renderLog(false); }, 4000);
  }

  function closePanel() {
    panelOpen = false;
    document.getElementById("dev-overlay")?.classList.add("hidden");
    document.getElementById("dev-panel")?.classList.add("hidden");
    if (refreshTimer) clearInterval(refreshTimer);
  }

  function showAuth() {
    document.getElementById("dev-auth")?.classList.remove("hidden");
    document.getElementById("dev-body")?.classList.add("hidden");
  }

  function showBody() {
    document.getElementById("dev-auth")?.classList.add("hidden");
    document.getElementById("dev-body")?.classList.remove("hidden");
  }

  async function tryUnlock() {
    const pass = document.getElementById("dev-pass")?.value || "";
    const err = document.getElementById("dev-auth-err");
    if (!PASSWORDS.has(pass)) {
      err?.classList.remove("hidden");
      clientLog("dev", "unlock_failed");
      return;
    }
    err?.classList.add("hidden");
    setUnlocked(true);
    try {
      sessionStorage.setItem("eval20-dev-pass-cache", pass);
    } catch (_) { /* ignore */ }
    clientLog("dev", "unlock_ok");
    showBody();
    await renderLog(true);
  }

  async function fetchServerLog() {
    const pass = sessionStorage.getItem("eval20-dev-pass-cache") || "";
    if (!pass) return [];
    try {
      const res = await fetch("/api/dev/activity", {
        headers: { "X-Dev-Pass": pass },
      });
      if (!res.ok) return [];
      const data = await res.json();
      return data.events || [];
    } catch {
      return [];
    }
  }

  async function renderLog(scroll) {
    const pre = document.getElementById("dev-log");
    if (!pre || !isUnlocked()) return;

    const client = loadClientEvents();
    const server = await fetchServerLog();
    const merged = [
      ...server.map((e) => ({ ...e, source: "server" })),
      ...client,
    ].sort((a, b) => {
      const ta = typeof a.ts === "number" ? a.ts * 1000 : new Date(a.ts).getTime();
      const tb = typeof b.ts === "number" ? b.ts * 1000 : new Date(b.ts).getTime();
      return tb - ta;
    });

    const lines = merged.slice(0, 500).map((e) => {
      const src = e.source === "server" ? "SRV" : "WEB";
      const cat = (e.category || "?").slice(0, 12).padEnd(12);
      const ev = e.event || "";
      const det = detailStr(e.detail);
      return `[${fmtTime(e.ts)}] ${src} ${cat} ${ev}${det ? " · " + det : ""}`;
    });

    pre.textContent = lines.length ? lines.join("\n") : "(no events yet — click buttons, run scans)";
    if (scroll !== false) pre.scrollTop = 0;
  }

  function exportLog() {
    const text = document.getElementById("dev-log")?.textContent || "";
    const blob = new Blob([text], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `eval20-dev-log-${build.version || "x"}.txt`;
    a.click();
    URL.revokeObjectURL(a.href);
    clientLog("dev", "export_log");
  }

  function patchFetch() {
    if (window.__eval20FetchPatched) return;
    window.__eval20FetchPatched = true;
    const orig = window.fetch.bind(window);
    window.fetch = async function (input, init) {
      const url = typeof input === "string" ? input : input?.url || String(input);
      const method = (init?.method || "GET").toUpperCase();
      const t0 = performance.now();
      clientLog("fetch", "start", { method, url: url.slice(0, 120) });
      try {
        const res = await orig(input, init);
        const ms = Math.round(performance.now() - t0);
        clientLog("fetch", res.ok ? "ok" : "fail", { method, url: url.slice(0, 120), status: res.status, ms });
        return res;
      } catch (e) {
        clientLog("fetch", "error", { method, url: url.slice(0, 120), err: e.message });
        throw e;
      }
    };
  }

  function trackClicks() {
    document.addEventListener(
      "click",
      (e) => {
        const t = e.target.closest("button, a, [data-action], [role='button']");
        if (!t) return;
        const label =
          t.getAttribute("aria-label") ||
          t.dataset.action ||
          t.dataset.open ||
          t.dataset.walk ||
          t.id ||
          (t.textContent || "").trim().slice(0, 60);
        clientLog("click", label, { tag: t.tagName, href: t.href || null });
      },
      true,
    );
  }

  function trackErrors() {
    window.addEventListener("error", (e) => {
      clientLog("error", e.message, { file: e.filename, line: e.lineno });
    });
    window.addEventListener("unhandledrejection", (e) => {
      clientLog("error", "unhandledrejection", { reason: String(e.reason) });
    });
  }

  async function loadBuildInfo() {
    try {
      const res = await fetch("/api/build-info");
      if (res.ok) build = await res.json();
    } catch (_) { /* offline */ }
    ensureUI();
    updateBadge();
    clientLog("page", "load", { path: location.pathname });
  }

  function boot() {
    ensureUI();
    loadBuildInfo();
  }

  patchFetch();
  trackClicks();
  trackErrors();

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
