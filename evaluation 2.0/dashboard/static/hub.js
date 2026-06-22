let PROJECTS = [];
let HEALTH = {};
let SELECTED = null;

function statusBadge(h) {
  if (h.kind === "cli") return ["cli", h.detail || "Scanner ready"];
  if (h.online) return ["ok", `Live · ${h.latency_ms ?? "?"}ms`];
  return ["off", "Service not running"];
}

function renderGuide(project) {
  const body = document.getElementById("guide-body");
  const room = document.getElementById("guide-room");
  if (!project) {
    room.textContent = "Select a project";
    body.innerHTML = "<p class='empty-guide'>Pick a project card. The AI guide will explain what it does and how to use it.</p>";
    return;
  }
  room.textContent = project.guide.theme_label || project.project.subtitle || "Project Guide";
  body.innerHTML = `
    <p class="guide-title">${project.project.name}</p>
    <p class="guide-meta">${project.guide.agent_name || "Agent"} · ${project.guide.agent_role || ""}</p>
    <p class="guide-text">${project.guide.greeting || ""}</p>
    <p class="guide-text">${project.guide.summary || ""}</p>
    <ul class="guide-list">
      ${(project.guide.flow || []).map((f) => `<li><strong>${f.title}:</strong> ${f.detail}</li>`).join("")}
    </ul>
    <button class="btn secondary" id="open-room-btn">Open Full Project Room</button>
  `;
  const openBtn = document.getElementById("open-room-btn");
  if (openBtn) {
    openBtn.addEventListener("click", () => {
      window.location.href = `/room/${project.project.id}`;
    });
  }
}

async function runAction(projectId, action) {
  const log = document.getElementById("capability-log");
  const endpoint = action === "inventory"
    ? `/api/actions/inventory/${projectId}`
    : action === "analyze"
      ? `/api/actions/analyze/${projectId}`
      : action === "run-tests"
        ? "/api/actions/run-tests"
        : null;
  if (!endpoint) return;
  log.textContent = "Running action...";
  try {
    const res = await fetch(endpoint, { method: "POST" });
    const data = await res.json();
    log.textContent = (data.ok ? "✓ " : "✗ ") + (data.output || data.stderr || "Action finished");
    if (data.log_tail) log.textContent += `\n\n${data.log_tail.slice(-1200)}`;
  } catch (e) {
    log.textContent = "Action failed: " + e.message;
  }
}

async function showCapabilities(projectId) {
  const log = document.getElementById("capability-log");
  log.textContent = "Checking capabilities...";
  try {
    const res = await fetch(`/api/capabilities/${projectId}`);
    const data = await res.json();
    const lines = [];
    lines.push(`${data.project.name}`);
    lines.push(`${"-".repeat(data.project.name.length)}`);
    (data.capabilities || []).forEach((c) => {
      const symbol = c.status === "ok" ? "✓" : c.status === "warn" ? "!" : "✗";
      lines.push(`${symbol} ${c.name}: ${typeof c.detail === "string" ? c.detail : JSON.stringify(c.detail)}`);
    });
    lines.push("");
    lines.push("Agent:");
    lines.push(`${data.agent_intro.name} — ${data.agent_intro.role}`);
    lines.push(data.agent_intro.greeting);
    log.textContent = lines.join("\n");
  } catch (e) {
    log.textContent = "Capability check failed: " + e.message;
  }
}

function renderCards() {
  const grid = document.getElementById("portals");
  grid.innerHTML = PROJECTS.map((p) => {
    const h = HEALTH[p.id] || {};
    const [cls, txt] = statusBadge(h);
    return `
      <article class="card" data-id="${p.id}">
        <div class="card-head">
          <span class="icon">${p.icon}</span>
          <div>
            <p class="title">${p.name}</p>
            <p class="sub">${p.subtitle}</p>
          </div>
        </div>
        <span class="badge ${cls}">${txt}</span>
        <div class="card-actions">
          <button class="btn action-open" data-id="${p.id}">Open Room</button>
          <button class="btn action-guide" data-id="${p.id}">AI Guide</button>
          <button class="btn action-check" data-id="${p.id}">Check Capabilities</button>
        </div>
      </article>
    `;
  }).join("");

  document.querySelectorAll(".action-open").forEach((btn) => {
    btn.addEventListener("click", () => { window.location.href = `/room/${btn.dataset.id}`; });
  });
  document.querySelectorAll(".action-guide").forEach((btn) => {
    btn.addEventListener("click", async () => {
      SELECTED = btn.dataset.id;
      const res = await fetch(`/api/project/${SELECTED}`);
      const data = await res.json();
      renderGuide(data);
      document.getElementById("btn-capability").disabled = false;
    });
  });
  document.querySelectorAll(".action-check").forEach((btn) => {
    btn.addEventListener("click", () => {
      SELECTED = btn.dataset.id;
      showCapabilities(SELECTED);
      document.getElementById("btn-capability").disabled = false;
    });
  });
}

async function init() {
  try {
    const [overviewRes, healthRes] = await Promise.all([
      fetch("/api/overview"),
      fetch("/api/projects/health"),
    ]);
    const overview = await overviewRes.json();
    const health = await healthRes.json();
    PROJECTS = overview.projects || [];
    HEALTH = health.health || {};
    document.getElementById("m-complete").textContent = overview.summary.complete;
    document.getElementById("m-total").textContent = overview.summary.total_tasks;
    renderCards();
  } catch (e) {
    document.getElementById("portals").innerHTML = `<p class="loading-msg">Could not load dashboard: ${e.message}</p>`;
  }

  document.getElementById("btn-capability").addEventListener("click", () => {
    if (SELECTED) showCapabilities(SELECTED);
  });
}

init();
