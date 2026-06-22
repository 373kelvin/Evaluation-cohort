/** Guided step-by-step demo — like someone manually clicking (2–3 sec per step) */
(function () {
  const STEP_MS = 2800;

  function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = String(s ?? "");
    return d.innerHTML;
  }

  function humanIntro(step) {
    const map = {
      "Open scanner CLI": "👆 Opening the scanner tool (like double-clicking an app)…",
      "Walk project tree (B1)": "👆 Clicking **Scan All Files** — walking every folder…",
      "Detect API routes (B2)": "👆 Clicking **Map API Routes** — searching for @app.get / @app.post…",
      "Generate insight report": "👆 Building the HTML report you can open in a browser…",
      "Validate diagram export": "👁 Checking the diagram has nodes you can zoom and click…",
      "Health check": "👆 Opening the service health page — is it alive?",
      "Add credit transaction": "👆 Typing a credit amount and clicking **Submit**…",
      "Reject invalid amount": "👆 Trying a bad negative amount — should see an error…",
      "Recalculate balance": "👁 Reading the balance on screen — does the math match?",
      "Simulate list transactions": "👁 Opening the transactions list…",
      "Preview list transactions": "👁 Opening the transactions list…",
      "Pipeline health": "👆 Checking if the Python fraud service is running…",
      "Explain AI scoring rules": "👁 Reading the score rules on screen — large amount, odd hour, risky country…",
      "Load demo platform": "👆 Opening the fintech demo folder…",
      "Inventory scan (B1)": "👆 Running file inventory — counting artifacts and tables…",
      "Endpoint map (B2)": "👆 Mapping every API route in the project…",
      "API health": "👆 Clicking the live API link — checking if it responds…",
      "Fraud alert endpoint": "👁 Opening fraud alerts — checking what an operator would see…",
    };
    for (const [key, val] of Object.entries(map)) {
      if (step.name?.startsWith(key) || step.name?.includes(key)) return val;
    }
    if (step.name?.startsWith("Score transaction")) {
      return "👆 Submitting a test transaction and waiting for the fraud score…";
    }
    return `👆 **${step.name}** — ${step.action || "running check"}…`;
  }

  class GuidedWalkthrough {
    constructor(container) {
      this.container = container;
      this._abort = false;
    }

    stop() {
      this._abort = true;
    }

    _renderShell(title) {
      this.container.hidden = false;
      this.container.innerHTML = `
        <div class="walkthrough">
          <div class="wt-head">
            <span class="wt-hand">👆</span>
            <div>
              <p class="wt-title">${esc(title || "Guided walkthrough")}</p>
              <p class="wt-sub">Watch each step — like a person clicking through the project</p>
            </div>
          </div>
          <div class="wt-progress-wrap"><div class="wt-progress" id="wt-progress"></div></div>
          <p class="wt-step-label" id="wt-step-label">Starting…</p>
          <div class="wt-stage" id="wt-stage"></div>
          <ul class="wt-log" id="wt-log"></ul>
        </div>`;
      this.progressEl = this.container.querySelector("#wt-progress");
      this.stageEl = this.container.querySelector("#wt-stage");
      this.logEl = this.container.querySelector("#wt-log");
      this.labelEl = this.container.querySelector("#wt-step-label");
    }

    async play(data, projectId) {
      this._abort = false;
      this.projectId = projectId;
      const steps = data.steps || [];
      this._renderShell(`${data.project} — step-by-step`);

      for (let i = 0; i < steps.length; i++) {
        if (this._abort) break;
        const step = steps[i];
        const pct = Math.round(((i + 1) / steps.length) * 100);
        if (this.progressEl) this.progressEl.style.width = pct + "%";
        if (this.labelEl) this.labelEl.textContent = `Step ${i + 1} of ${steps.length}`;

        const intro = humanIntro(step);
        this.stageEl.innerHTML = `
          <div class="wt-current ${step.status}">
            <p class="wt-action">${intro.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")}</p>
            <p class="wt-detail">${esc(step.detail)}</p>
            ${step.capability ? `<p class="wt-cap">${esc(step.capability)}</p>` : ""}
            ${step.score != null ? `<p class="wt-score">Score: <strong>${step.score}/100</strong> (${esc(step.risk)})</p>` : ""}
            ${step.open_href && step.status === "pass" ? `<button type="button" class="btn btn-open-live wt-open-btn" data-open-href="${esc(step.open_href)}">Open report →</button>` : step.open_target && step.status === "pass" ? `<button type="button" class="btn btn-open-live wt-open-btn" data-open-target="${esc(step.open_target)}">Open now →</button>` : ""}
            <span class="wt-status ${step.status}">${step.status === "pass" ? "✓ Confirmed" : "✗ Failed"}</span>
          </div>`;

        const openHrefBtn = this.stageEl.querySelector("[data-open-href]");
        if (openHrefBtn) {
          openHrefBtn.addEventListener("click", () => {
            if (window.showReportViewer) window.showReportViewer(openHrefBtn.dataset.openHref, step.name);
            else window.open(openHrefBtn.dataset.openHref, "_blank", "noopener");
          });
        }
        const openBtn = this.stageEl.querySelector("[data-open-target]");
        if (openBtn && window.openProjectLink) {
          openBtn.addEventListener("click", () => window.openProjectLink(this.projectId, openBtn.dataset.openTarget));
        }

        const li = document.createElement("li");
        li.className = step.status;
        li.innerHTML = `<span>${step.status === "pass" ? "✓" : "✗"}</span> ${esc(step.name)}`;
        this.logEl.appendChild(li);
        this.logEl.scrollTop = this.logEl.scrollHeight;

        await sleep(STEP_MS);
      }

      if (!this._abort) {
        this.stageEl.innerHTML = `
          <div class="wt-done">
            <p class="wt-done-title">✅ Walkthrough complete</p>
            <p>${esc(data.summary || "")}</p>
            <p class="wt-done-tip">${esc(data.tip || "")}</p>
          </div>`;
        if (this.labelEl) this.labelEl.textContent = `Done — ${data.passed}/${data.total} checks passed`;
      }
    }
  }

  window.GuidedWalkthrough = GuidedWalkthrough;
  window.runGuidedDemo = async function (projectId, container, onFetch) {
    const wt = new GuidedWalkthrough(container);
    if (onFetch) onFetch("fetching");
    const res = await fetch(`/api/demo-tests/${projectId}`, {
      method: "POST",
      signal: AbortSignal.timeout(20000),
    });
    const data = await res.json();
    if (onFetch) onFetch("playing", data);
    await wt.play(data, projectId);
    return data;
  };
})();
