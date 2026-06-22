const id = location.pathname.split("/").pop();
let projectAIChat = null;
let walkthroughRunning = false;
let currentReportUrl = null;

function log(msg) {
  const el = document.getElementById("log");
  if (!el) return;
  el.textContent = (el.textContent === "Pick a button to start." ? "" : el.textContent + "\n") + msg;
  el.scrollTop = el.scrollHeight;
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

function setButtonsBusy(busy) {
  ["btn-walkthrough", "btn-quick"].forEach((bid) => {
    const b = document.getElementById(bid);
    if (b) b.disabled = busy;
  });
}

function viewReport(url, title) {
  if (!url) return;
  currentReportUrl = url;
  if (window.showReportViewer) {
    window.showReportViewer(url, title || "Insight Report");
  } else {
    window.open(url, "_blank", "noopener");
  }
}

function renderQuickResults(data) {
  const box = document.getElementById("demo-results");
  if (!box) return;
  box.hidden = false;
  document.getElementById("walkthrough-panel").hidden = true;
  const scoreSteps = (data.steps || []).filter((s) => s.score != null);
  const reportStep = (data.steps || []).find((s) => s.open_href);
  const reportBtn = reportStep?.open_href
    ? `<button type="button" class="btn btn-primary-action" id="demo-view-report" style="margin-top:0.75rem;width:100%">📊 View Report</button>`
    : "";
  box.innerHTML = `
    <p class="demo-summary"><strong>${data.passed}/${data.total} passed</strong> — ${data.summary}</p>
    ${scoreSteps.length ? `<div class="score-row">${scoreSteps.map((s) => `
      <div class="score-pill risk-${(s.risk || "low").toLowerCase()}">
        <span class="num">${s.score}</span><span class="lbl">${s.risk}</span>
        <p class="score-why">${(s.reasons || []).join(", ")}</p>
      </div>`).join("")}</div>` : ""}
    <ul class="demo-list">${(data.steps || []).map((s) => `
      <li class="${s.status}"><span>${s.status === "pass" ? "✓" : "✗"}</span>
        <div><strong>${s.name}</strong><p>${s.detail}</p></div></li>`).join("")}</ul>
    ${reportBtn}`;
  document.getElementById("demo-view-report")?.addEventListener("click", () => {
    viewReport(reportStep.open_href, data.project);
  });
  if (reportStep?.open_href) viewReport(reportStep.open_href, data.project);
}

async function runWalkthrough() {
  if (walkthroughRunning) return;
  walkthroughRunning = true;
  setButtonsBusy(true);
  const btn = document.getElementById("btn-walkthrough");
  if (btn) btn.textContent = "Playing walkthrough…";
  log("Step-by-step walkthrough started (~3 sec per step)…");
  window.showToast?.("Walkthrough started", "Running validation — may take up to a minute for Project Insight", { type: "info", duration: 6000 });
  document.getElementById("demo-results").hidden = true;
  try {
    const data = await window.runGuidedDemo(id, document.getElementById("walkthrough-panel"), (phase, d) => {
      if (phase === "playing") log(`Walkthrough: ${d.passed}/${d.total} checks`);
    });
    renderQuickResults(data);
    window.loadReportGallery?.(document.getElementById("report-gallery"));
  } catch (e) {
    log("Walkthrough failed: " + e.message);
  } finally {
    walkthroughRunning = false;
    setButtonsBusy(false);
    if (btn) btn.textContent = "👁 Watch Step-by-Step Demo";
  }
}

async function runQuickDemo() {
  setButtonsBusy(true);
  log("Quick validation check…");
  try {
    const res = await fetch(`/api/demo-tests/${id}`, { method: "POST", signal: AbortSignal.timeout(60000) });
    const data = await res.json();
    renderQuickResults(data);
    log(`Quick check: ${data.passed}/${data.total} passed`);
    window.loadReportGallery?.(document.getElementById("report-gallery"));
  } catch (e) {
    log("Quick check failed: " + e.message);
  } finally {
    setButtonsBusy(false);
  }
}

function setActionButtonsBusy(busy) {
  document.querySelectorAll("[data-action], .btn-open-live, #github-scan-form button, .upload-label").forEach((b) => {
    b.disabled = busy;
  });
}

async function post(url, label, opts = {}) {
  log(label ? `${label}…` : "Running…");
  setActionButtonsBusy(true);
  try {
    const res = await fetch(url, { method: "POST", ...opts.fetch });
    let data = {};
    try { data = await res.json(); } catch (_) {
      log("✗ Unexpected response");
      return null;
    }
    if (!res.ok) {
      const msg = typeof data.detail === "object" ? data.detail.message : data.detail;
      log("✗ Failed: " + (msg || res.status));
      return data;
    }
    if (data.ok) {
      log("✓ Done");
      if (data.output) log("Saved: " + data.output);
      if (data.preview) log("\n— preview —\n" + data.preview.slice(0, 500));
      if (data.steps) logSteps(data);
      if (data.report_url) {
        log("Opening report viewer…");
        viewReport(data.report_url, data.slug || id);
        window.showToast?.("Report ready", "Saved to Your Reports →", {
          type: "success",
          actions: [
            { id: "v", label: "View", onClick: () => viewReport(data.report_url, data.slug || id) },
          ],
        });
        window.loadReportGallery?.(document.getElementById("report-gallery"));
      }
    } else {
      log("✗ Failed: " + (data.stderr?.slice(-300) || "exit " + data.code));
    }
    return data;
  } catch (e) {
    log("Error: " + e.message);
    return null;
  } finally {
    setActionButtonsBusy(false);
  }
}

async function openReport(href) {
  try {
    const res = await fetch(href);
    if (res.ok) {
      viewReport(href, "Scan Report");
      return;
    }
    const err = await res.json().catch(() => ({}));
    const d = err.detail;
    const msg = (typeof d === "object" && d?.message ? d.message : d) || "No report yet.";
    log(msg + " Run **Map API Routes (B2)** or scan a GitHub repo first.");
  } catch (_) {
    log("Could not load report — open http://127.0.0.1:9010 (dashboard may be stopped).");
  }
}

async function runAction(action) {
  if (action === "inventory") return post(`/api/actions/inventory/${id}`, "Scanning files (B1)");
  if (action === "analyze") return post(`/api/actions/analyze/${id}`, "Mapping API routes (B2)");
  if (action === "run-tests") return post("/api/actions/run-tests", "Running tests (B3)");
  if (action === "demo-fintech") {
    await post("/api/actions/inventory/fintech-demo", "Scanning fintech (B1)");
    return post("/api/actions/analyze/fintech-demo", "Mapping fintech routes (B2)");
  }
}

function logSteps(data) {
  (data?.steps || []).forEach((s) => {
    const mark = s.status === "fail" ? "✗" : "✓";
    log(`${mark} ${s.label}: ${s.detail || ""}`);
  });
  if (data?.summary) log(data.summary);
  if (data?.stderr && !data?.ok) log("Debug: " + data.stderr.slice(-400));
}

const SCAN_STEPS_ZIP = [
  { label: "Receive zip upload" },
  { label: "B1 — file inventory" },
  { label: "B2 — route map + diagram" },
  { label: "Save HTML report" },
];

const SCAN_STEPS_GITHUB = [
  { label: "Download from GitHub" },
  { label: "Receive source" },
  { label: "B1 — file inventory" },
  { label: "B2 — route map + diagram" },
  { label: "Save HTML report" },
];

async function scanGithub(url) {
  setActionButtonsBusy(true);
  log("GitHub scan: " + url);
  try {
    const data = await window.runWithProgressUI(
      "Scanning GitHub repo",
      SCAN_STEPS_GITHUB,
      () => fetch("/api/actions/scan-github", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      }).then(async (res) => {
        const d = await res.json();
        if (!res.ok && !d.steps) {
          const msg = typeof d.detail === "string" ? d.detail : JSON.stringify(d.detail);
          throw new Error(msg || "Request failed");
        }
        return d;
      }),
      (idx, label) => log("… " + label),
    );
    logSteps(data);
    if (data?.ok && data.report_url) {
      viewReport(data.report_url, data.slug);
      window.loadReportGallery?.(document.getElementById("report-gallery"));
    }
  } catch (e) {
    log("Error: " + e.message);
  } finally {
    setActionButtonsBusy(false);
  }
}

async function scanZip(file) {
  if (!file) return;
  document.getElementById("upload-name").textContent = file.name + " (" + (file.size / 1024).toFixed(0) + " KB)";
  setActionButtonsBusy(true);
  log("Zip upload: " + file.name);
  window.showToast?.("Upload received", file.name + " — starting scan…", { type: "info", duration: 5000 });

  const fd = new FormData();
  fd.append("file", file);
  try {
    const data = await window.runWithProgressUI(
      "Scanning " + file.name,
      SCAN_STEPS_ZIP,
      () => fetch("/api/actions/scan-upload", { method: "POST", body: fd }).then(async (res) => {
        const d = await res.json();
        if (!res.ok) throw new Error(typeof d.detail === "string" ? d.detail : "Upload failed");
        return d;
      }),
      (idx, label) => log("… " + label),
    );
    logSteps(data);
    if (data?.ok && data.report_url) {
      viewReport(data.report_url, file.name.replace(/\.zip$/i, ""));
      window.loadReportGallery?.(document.getElementById("report-gallery"));
    }
  } catch (e) {
    log("Error: " + e.message);
  } finally {
    setActionButtonsBusy(false);
  }
}

function initScanExternal() {
  if (id !== "entity-diagrams") return;
  const block = document.getElementById("scan-external-block");
  if (block) block.hidden = false;

  document.getElementById("github-scan-form")?.addEventListener("submit", (e) => {
    e.preventDefault();
    const url = document.getElementById("github-url")?.value?.trim();
    if (url) scanGithub(url);
  });

  document.getElementById("zip-upload")?.addEventListener("change", (e) => {
    scanZip(e.target.files?.[0]);
  });

  const dropZone = document.getElementById("zip-drop-zone");
  if (!dropZone) return;
  ["dragenter", "dragover"].forEach((ev) => {
    dropZone.addEventListener(ev, (e) => {
      e.preventDefault();
      dropZone.classList.add("drag-over");
    });
  });
  ["dragleave", "drop"].forEach((ev) => {
    dropZone.addEventListener(ev, (e) => {
      e.preventDefault();
      dropZone.classList.remove("drag-over");
    });
  });
  dropZone.addEventListener("drop", (e) => {
    const file = e.dataTransfer?.files?.[0];
    if (file?.name?.toLowerCase().endsWith(".zip")) scanZip(file);
    else window.showToast?.("Wrong file", "Please drop a .zip file", { type: "error" });
  });
}

function initGuideChat() {
  const details = document.querySelector(".guide-details");
  const root = document.getElementById("ai-chat-root");
  if (!root) return;
  details?.addEventListener("toggle", () => {
    if (details.open && !projectAIChat) {
      projectAIChat = new ProjectAIChat(root, id);
    }
  });
}

async function init() {
  initTheme();
  window.initReportViewer?.();
  document.getElementById("theme-toggle")?.addEventListener("click", toggleTheme);
  document.getElementById("btn-walkthrough")?.addEventListener("click", runWalkthrough);
  document.getElementById("btn-quick")?.addEventListener("click", runQuickDemo);
  initScanExternal();
  initGuideChat();

  const res = await fetch(`/api/project/${id}`);
  if (!res.ok) {
    document.body.innerHTML = "<p>Project not found. <a href='/'>Go back</a></p>";
    return;
  }
  const { project, guide, open_links, live_ready, has_report, report_url } = await res.json();

  document.documentElement.style.setProperty("--room-accent", project.color || "#818cf8");
  document.getElementById("hero-icon").textContent = project.icon || "◈";
  document.title = project.name + " — " + (guide.theme_label || "");
  document.getElementById("theme-label").textContent = guide.theme_label || "";
  document.getElementById("project-name").textContent = project.name;
  document.getElementById("project-sub").textContent = project.subtitle;
  document.getElementById("status-line").textContent = project.health?.detail || "Ready";
  document.getElementById("summary").textContent = guide.summary || "";

  document.getElementById("flow").innerHTML = (guide.flow || [])
    .map((f) => `<li><strong>Step ${f.step}: ${f.title}</strong><span>${f.detail}</span></li>`)
    .join("");

  document.getElementById("start-hint").textContent = guide.start_hint || (guide.start_cmd ? "Start the live service in Terminal, then use the Open buttons below:" : "");
  const cmd = document.getElementById("start-cmd");
  if (guide.start_cmd) { cmd.hidden = false; cmd.textContent = guide.start_cmd; }

  const openHost = document.getElementById("open-links");
  if (open_links?.length && window.renderOpenButtons) {
    window.renderOpenButtons(openHost, id, open_links, live_ready);
  }

  const LABELS = {
    inventory: "📋 Scan All Files (B1)",
    analyze: "🗺 Map API Routes (B2)",
    "run-tests": "🧪 Run Automated Tests (B3)",
    "demo-fintech": "🏦 Run Full Fintech Scan (B1 + B2)",
  };

  document.getElementById("actions").innerHTML = (guide.links || [])
    .map((link) => {
      const label = LABELS[link.action] || link.label;
      if (link.href) {
        const reportBtn = link.needs_report
          ? `<button type="button" class="btn" data-report="${link.href}"><strong>${label}</strong><small>${link.hint || ""}</small></button>`
          : `<a class="btn" href="${link.href}" target="_blank" rel="noopener"><strong>${label}</strong><small>${link.hint || ""}</small></a>`;
        return reportBtn;
      }
      if (link.open) {
        return `<button type="button" class="btn btn-open-live${live_ready ? "" : " needs-start"}" data-open="${link.open}"><strong>${label}</strong><small>${link.hint || ""}</small></button>`;
      }
      return `<button type="button" class="btn" data-action="${link.action}"><strong>${label}</strong><small>${link.hint || ""}</small></button>`;
    })
    .join("");

  document.querySelectorAll("[data-open]").forEach((btn) => {
    btn.addEventListener("click", () => window.openProjectLink(id, btn.dataset.open));
  });

  const sub = document.querySelector(".sub-heading");
  if (sub && !document.getElementById("actions").children.length) sub.hidden = true;

  document.querySelectorAll("[data-action]").forEach((btn) => {
    btn.addEventListener("click", () => runAction(btn.dataset.action));
  });

  document.querySelectorAll("[data-report]").forEach((btn) => {
    btn.addEventListener("click", () => openReport(btn.dataset.report));
  });

  window.loadReportGallery?.(document.getElementById("report-gallery"));
  if (has_report && report_url) {
    log("Report ready — open from **Your Reports** or run another scan.");
  }

  document.getElementById("agent-cards").innerHTML = (guide.agents_here || [])
    .map((a) => `<div class="agent-card" data-agent-id="${a.id}"><strong>${a.id} — ${a.name}</strong><span>${a.tip}</span></div>`)
    .join("");

  document.querySelectorAll(".agent-card[data-agent-id]").forEach((card) => {
    card.addEventListener("click", () => {
      const details = document.querySelector(".guide-details");
      if (details) details.open = true;
      if (!projectAIChat) projectAIChat = new ProjectAIChat(document.getElementById("ai-chat-root"), id);
      setTimeout(() => {
        projectAIChat.activeAgent = card.dataset.agentId;
        projectAIChat.send(`Tell me about ${card.dataset.agentId}`);
      }, 300);
    });
  });
}

init().catch((e) => {
  const el = document.getElementById("log");
  if (el) el.textContent = "Error: " + e.message;
});
