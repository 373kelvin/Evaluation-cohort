const $ = (sel) => document.querySelector(sel);

function hideLoader() {
  const el = $("#page-loader");
  if (el) el.classList.add("hidden");
}

function showError(msg) {
  hideLoader();
  let banner = $("#error-banner");
  if (!banner) {
    banner = document.createElement("div");
    banner.id = "error-banner";
    banner.className = "error-banner";
    document.body.appendChild(banner);
  }
  banner.textContent = msg;
  banner.classList.add("show");
}

async function fetchJson(url, ms = 4000) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), ms);
  try {
    const res = await fetch(url, { signal: ctrl.signal });
    if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
    return await res.json();
  } finally {
    clearTimeout(timer);
  }
}

async function postJson(url, ms = 120000) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), ms);
  try {
    const res = await fetch(url, { method: "POST", signal: ctrl.signal });
    if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
    return await res.json();
  } finally {
    clearTimeout(timer);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const terminal = $("#terminal-body");
  const terminalLabel = $("#terminal-label");
  const RING_C = 2 * Math.PI * 52;

  let lastProjects = [];
  let selectedProjectId = null;
  let projectAIChat = null;

  function initProjectAI(projectId, projectName) {
    const root = $("#ai-chat-root");
    const badge = $("#guide-badge");
    if (!root) return;
    selectedProjectId = projectId;
    if (badge) badge.textContent = projectName || projectId;
    root.innerHTML = "";
    projectAIChat = new ProjectAIChat(root, projectId);
    $("#walkthrough-panel").hidden = true;
    $("#guide-panel")?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function renderDemoResultsPanel(data) {
    const panel = $("#demo-results-panel");
    const body = $("#demo-results-body");
    if (!panel || !body) return;
    panel.hidden = false;
    const scoreSteps = (data.steps || []).filter((s) => s.score != null);
    body.innerHTML = `
      <p class="demo-result-summary"><strong>${data.passed}/${data.total} passed</strong> — ${data.summary || ""}</p>
      ${scoreSteps.length ? `<div class="score-cards">${scoreSteps.map((s) => `
        <div class="score-card risk-${(s.risk || "low").toLowerCase()}">
          <span class="score-num">${s.score}</span>
          <span class="score-label">${s.risk} RISK</span>
          <span class="score-detail">${s.transaction?.country || ""} · ₹${(s.transaction?.amount || 0).toLocaleString()}</span>
          <span class="score-reasons">${(s.reasons || []).join(" · ")}</span>
        </div>`).join("")}</div>` : ""}
      <ul class="demo-steps">${(data.steps || []).map((s) => `
        <li class="demo-step ${s.status}">
          <span class="step-icon">${s.status === "pass" ? "✓" : "✗"}</span>
          <div><strong>${s.name}</strong><p>${s.detail}</p>${s.capability ? `<em>${s.capability}</em>` : ""}</div>
        </li>`).join("")}</ul>
      <button type="button" class="btn btn-primary btn-sm" id="rerun-demo-inline">↻ Run Again (new scenario)</button>`;
    $("#rerun-demo-inline")?.addEventListener("click", () => runDemoTests(selectedProjectId));
    panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function log(msg, clear = false) {
    if (!terminal) return;
    if (clear) terminal.textContent = "";
    terminal.textContent += (clear ? "" : terminal.textContent ? "\n" : "") + msg;
    terminal.scrollTop = terminal.scrollHeight;
  }

  function formatDemoResults(data) {
    const lines = [];
    lines.push(`═══ Demo Tests · ${data.project} ═══`);
    lines.push(`Run ID: ${data.run_id}`);
    lines.push(`Agent: ${data.agent}`);
    lines.push(`Result: ${data.passed}/${data.total} passed`);
    lines.push(data.summary || "");
    lines.push("");
    (data.steps || []).forEach((s, i) => {
      const icon = s.status === "pass" ? "✓" : "✗";
      lines.push(`${icon} Step ${i + 1}: ${s.name}`);
      lines.push(`  Action: ${s.action}`);
      lines.push(`  ${s.detail}`);
      if (s.capability) lines.push(`  → ${s.capability}`);
      if (s.score != null) {
        lines.push(`  ★ Fraud Score: ${s.score}/100 (${s.risk || "?"}) — ${(s.reasons || []).join(", ")}`);
      }
      lines.push("");
    });
    if (data.tip) lines.push(`Tip: ${data.tip}`);
    return lines.join("\n");
  }

  function statusLabel(s) {
    return { complete: "Complete", partial: "Partial", pending: "Pending" }[s] || s;
  }

  function setProgress(pct) {
    const ring = $("#ring-fg");
    const label = $("#ring-label");
    if (!ring) return;
    ring.style.strokeDasharray = RING_C;
    ring.style.stroke = "var(--accent)";
    ring.style.strokeDashoffset = RING_C - (pct / 100) * RING_C;
    if (label) label.textContent = pct + "%";
  }

  function initTheme() {
    const saved = localStorage.getItem("eval20-theme") || "dark";
    document.documentElement.setAttribute("data-theme", saved);
  }

  function toggleTheme() {
    const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("eval20-theme", next);
    window.dispatchEvent(new Event("themechange"));
  }

  function renderDemoInGuide(data) {
    renderDemoResultsPanel(data);
  }

  async function runWalkthrough(projectId) {
    selectedProjectId = projectId;
    const proj = lastProjects.find((p) => p.id === projectId);
    $("#guide-badge").textContent = proj?.name || projectId;
    $("#demo-results-panel").hidden = true;
    const panel = $("#walkthrough-panel");
    log(`Step-by-step walkthrough for ${projectId} (~3 sec per step)…`, true);
    if (terminalLabel) terminalLabel.textContent = "walkthrough · " + projectId;
    $("#guide-panel")?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    try {
      await window.runGuidedDemo(projectId, panel, (_, data) => {
        if (data) {
          log(formatDemoResults(data));
          renderDemoResultsPanel(data);
        }
      });
    } catch (e) {
      log("Walkthrough failed: " + e.message);
    }
  }

  async function runQuickDemo(projectId) {
    selectedProjectId = projectId;
    log("Quick validation check…", true);
    if (terminalLabel) terminalLabel.textContent = "quick check · " + projectId;
    $("#walkthrough-panel").hidden = true;
    document.body.classList.add("loading");
    try {
      const data = await postJson(`/api/demo-tests/${projectId}`, 15000);
      log(formatDemoResults(data));
      renderDemoResultsPanel(data);
      $("#guide-panel")?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    } catch (e) {
      log("Quick check failed: " + e.message);
    } finally {
      document.body.classList.remove("loading");
    }
  }

  async function runDemoTests(projectId) {
    return runWalkthrough(projectId);
  }

  async function showGuide(projectId) {
    const proj = lastProjects.find((p) => p.id === projectId);
    initProjectAI(projectId, proj?.name || projectId);
  }

  async function showCapabilities(projectId) {
    initProjectAI(projectId, lastProjects.find((p) => p.id === projectId)?.name);
    log("Checking capabilities…", true);
    try {
      const data = await fetchJson(`/api/capabilities/${projectId}`);
      const lines = [`${data.project.name}`, ""];
      (data.capabilities || []).forEach((c) => {
        const sym = c.status === "ok" ? "✓" : c.status === "warn" ? "!" : "✗";
        lines.push(`${sym} ${c.name}: ${typeof c.detail === "string" ? c.detail : JSON.stringify(c.detail)}`);
      });
      lines.push("", `${data.agent_intro.name}: ${data.agent_intro.greeting}`);
      log(lines.join("\n"));
      if (projectAIChat) {
        projectAIChat.addMessage("bot", lines.slice(2).join("\n"), { agent: data.agent_intro.name, role: "Capability Check" });
      }
    } catch (e) {
      log("Capability check failed: " + e.message);
    }
  }

  function renderProjects(projects) {
    const grid = $("#project-grid");
    if (!grid) return;
    const count = $("#project-count");
    if (count) count.textContent = projects.length + " systems";
    grid.innerHTML = projects.map((p) => {
      const isCli = p.kind === "cli" || p.health?.detail === "no health endpoint";
      const online = p.health?.online;
      const checking = p.health?.detail === "not checked";
      const statusText = isCli
        ? "Ready · CLI tool (no server needed)"
        : checking
          ? "Checking…"
          : online
            ? `Online · ${p.health.latency_ms}ms`
            : "Offline — start service for live demo";
      const dotClass = isCli ? "online" : online ? "online" : checking ? "" : "offline";
      const featured = p.featured ? " featured" : "";
      return `
      <article class="project-card${featured}" style="--card-accent: ${p.color}">
        <div class="project-icon">${p.icon}</div>
        <div class="project-name">${p.name}</div>
        <div class="project-sub">${p.subtitle}</div>
        <div class="status-row">
          <span class="status-dot ${dotClass}"></span>
          <span>${statusText}</span>
        </div>
        <div class="task-tags">${p.tasks.map((t) => `<span class="tag">${t}</span>`).join("")}</div>
        <div class="card-actions">
          <button class="btn btn-sm btn-primary" type="button" data-walk="${p.id}" title="Like a person clicking — 3 sec per step">👁 Step-by-Step Demo</button>
          <button class="btn btn-sm btn-secondary" type="button" data-quick="${p.id}" title="Fast check, all results at once">⚡ Quick Check</button>
          <button class="btn btn-sm btn-secondary" type="button" data-guide="${p.id}">💬 Ask Guide</button>
          <button class="btn btn-sm btn-secondary" type="button" data-inv="${p.id}">📋 Scan Files (B1)</button>
          <button class="btn btn-sm btn-secondary" type="button" data-analyze="${p.id}">🗺 Map Routes (B2)</button>
          <a class="btn btn-sm btn-secondary" href="/room/${p.id}">Open Project Page</a>
        </div>
      </article>`;
    }).join("");

    grid.querySelectorAll("[data-walk]").forEach((btn) => {
      btn.addEventListener("click", () => runWalkthrough(btn.dataset.walk));
    });
    grid.querySelectorAll("[data-quick]").forEach((btn) => {
      btn.addEventListener("click", () => runQuickDemo(btn.dataset.quick));
    });
    grid.querySelectorAll("[data-guide]").forEach((btn) => {
      btn.addEventListener("click", () => showGuide(btn.dataset.guide));
    });
    grid.querySelectorAll("[data-inv]").forEach((btn) => {
      btn.addEventListener("click", () => runInventory(btn.dataset.inv));
    });
    grid.querySelectorAll("[data-analyze]").forEach((btn) => {
      btn.addEventListener("click", () => runAnalyze(btn.dataset.analyze));
    });
  }

  function renderAgents(tasks) {
    const grid = $("#agent-grid");
    if (!grid) return;
    grid.innerHTML = tasks.map((t) => `
      <div class="agent-row">
        <span class="agent-id">${t.id}</span>
        <span class="agent-name">${t.name}</span>
        <span class="status-chip ${t.status}">${statusLabel(t.status)}</span>
      </div>
    `).join("");
  }

  function renderOutputs(items) {
    const list = $("#output-list");
    if (!list) return;
    const top = items.slice(0, 24);
    list.innerHTML = top.length
      ? top.map((o) => {
          const isHtml = o.path.endsWith(".html");
          const href = isHtml ? `/api/reports/${o.path.split("/").pop().replace(".html", "")}` : "#";
          return `<li><a class="path" href="${href}" ${isHtml ? 'target="_blank"' : ""}>${o.path}</a><span class="size">${(o.size / 1024).toFixed(1)} KB</span></li>`;
        }).join("")
      : "<li><span class='path'>No outputs yet</span></li>";
  }

  async function loadHealth() {
    try {
      const data = await fetchJson("/api/projects/health", 4000);
      lastProjects = lastProjects.map((p) => ({
        ...p,
        health: data.health[p.id] || p.health,
      }));
      renderProjects(lastProjects);
    } catch (_) {
      /* health is optional */
    }
  }

  async function load() {
    try {
      const data = await fetchJson("/api/overview", 4000);
      $("#stat-total").textContent = data.summary.total_tasks;
      $("#stat-complete").textContent = data.summary.complete;
      $("#stat-progress").textContent = data.summary.progress_pct + "%";
      setProgress(data.summary.progress_pct);
      lastProjects = data.projects;
      renderProjects(lastProjects);
      renderAgents(data.tasks);
      const updated = $("#last-updated");
      if (updated) updated.textContent = "Updated " + new Date().toLocaleTimeString();
    } catch (e) {
      showError("Dashboard API not responding. Run: bash scripts/start_dashboard.sh");
      log("Failed: " + e.message, true);
    } finally {
      hideLoader();
    }

    try {
      const outData = await fetchJson("/api/outputs", 3000);
      renderOutputs(outData.outputs || []);
    } catch (_) {
      /* outputs optional — page still usable */
    }

    loadHealth();
  }

  async function post(url) {
    log("→ " + url);
    if (terminalLabel) terminalLabel.textContent = "agent output";
    document.body.classList.add("loading");
    try {
      const data = await postJson(url);
      log(data.ok ? "✓ Success" : "✗ Failed (exit " + data.code + ")");
      if (data.log_tail) log(data.log_tail.slice(-1200));
      else if (data.stdout) log(data.stdout.slice(-800));
      if (data.stderr) log(data.stderr.slice(-400));
      if (data.output) log("📄 " + data.output);
      if (data.action === "analyze" && data.ok && data.report_url) {
        log("Opening HTML report…");
        window.open(data.report_url, "_blank", "noopener");
      }
      if (data.preview) log("\n— preview —\n" + data.preview.slice(0, 600));
      if (data.steps) log(formatDemoResults(data));
      await load();
      return data;
    } catch (e) {
      log("Error: " + e.message);
    } finally {
      document.body.classList.remove("loading");
    }
  }

  const runInventory = (key) => post(`/api/actions/inventory/${key}`);
  const runAnalyze = (key) => post(`/api/actions/analyze/${key}`);

  initTheme();
  const themeBtn = $("#theme-toggle");
  if (themeBtn) themeBtn.addEventListener("click", toggleTheme);
  const refreshBtn = $("#btn-refresh");
  if (refreshBtn) refreshBtn.addEventListener("click", () => { log("Refreshing…", true); load(); });

  const runTestsBtn = document.querySelector('[data-action="run-tests"]');
  if (runTestsBtn) runTestsBtn.addEventListener("click", () => post("/api/actions/run-tests"));

  const invAll = document.querySelector('[data-action="inventory-all"]');
  if (invAll) invAll.addEventListener("click", async () => {
    log("B1 — scanning all projects…", true);
    for (const k of ["entity-diagrams", "fastapi-tx", "fraud-score", "fintech-demo"]) {
      await runInventory(k);
    }
  });

  const analyzeAll = document.querySelector('[data-action="analyze-all"]');
  if (analyzeAll) analyzeAll.addEventListener("click", async () => {
    log("B2 — endpoint mapping…", true);
    for (const k of ["fastapi-tx", "fraud-score", "fintech-demo"]) {
      await runAnalyze(k);
    }
  });

  const demoBtn = document.querySelector('[data-action="demo-fintech"]');
  if (demoBtn) demoBtn.addEventListener("click", async () => {
    log("🏦 Fintech Platform demo scan (B1 + B2)…", true);
    await runInventory("fintech-demo");
    await runAnalyze("fintech-demo");
    log("\nExpected: 5 tables · 12 endpoints · 27 artifacts");
  });

  load();
  setTimeout(hideLoader, 6000);
  setInterval(load, 60000);
});
