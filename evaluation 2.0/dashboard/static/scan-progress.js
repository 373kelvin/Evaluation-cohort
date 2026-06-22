/** Toasts + scan progress — so uploads never feel "stuck" */
(function () {
  const toasts = [];
  let toastRoot = null;

  function ensureToastRoot() {
    if (toastRoot) return toastRoot;
    toastRoot = document.createElement("div");
    toastRoot.className = "toast-stack";
    toastRoot.setAttribute("aria-live", "polite");
    document.body.appendChild(toastRoot);
    return toastRoot;
  }

  window.showToast = function (title, message, opts = {}) {
    const root = ensureToastRoot();
    const id = "toast-" + Date.now();
    const type = opts.type || "info";
    const el = document.createElement("div");
    el.className = `toast toast-${type}`;
    el.id = id;
    el.innerHTML = `
      <div class="toast-body">
        <strong>${escapeHtml(title)}</strong>
        ${message ? `<p>${escapeHtml(message)}</p>` : ""}
        ${opts.actions ? `<div class="toast-actions">${opts.actions.map((a) =>
          `<button type="button" class="toast-btn" data-action="${a.id}">${escapeHtml(a.label)}</button>`
        ).join("")}</div>` : ""}
      </div>
      <button type="button" class="toast-close" aria-label="Dismiss">×</button>`;

    el.querySelector(".toast-close")?.addEventListener("click", () => dismissToast(el));
    opts.actions?.forEach((a) => {
      el.querySelector(`[data-action="${a.id}"]`)?.addEventListener("click", () => {
        a.onClick?.();
        dismissToast(el);
      });
    });

    root.appendChild(el);
    requestAnimationFrame(() => el.classList.add("show"));
    const ms = opts.duration ?? (opts.actions ? 12000 : 5000);
    const timer = setTimeout(() => dismissToast(el), ms);
    el._timer = timer;
    toasts.push(el);
    return el;
  };

  function dismissToast(el) {
    if (!el) return;
    clearTimeout(el._timer);
    el.classList.remove("show");
    setTimeout(() => el.remove(), 300);
  }

  function escapeHtml(s) {
    const d = document.createElement("div");
    d.textContent = String(s ?? "");
    return d.innerHTML;
  }

  class ScanProgress {
    constructor(container) {
      this.container = container;
      this.steps = [];
      this._start = Date.now();
    }

    show(title, stepDefs) {
      if (!this.container) return;
      this.steps = stepDefs.map((s) => ({ ...s, status: "pending" }));
      this.container.hidden = false;
      this._render(title);
      this.container.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    setStep(index, status, detail) {
      if (!this.steps[index]) return;
      this.steps[index].status = status;
      if (detail) this.steps[index].detail = detail;
      this._render(this._title);
    }

    advance(index, detail) {
      for (let i = 0; i < index; i++) {
        if (this.steps[i].status === "pending" || this.steps[i].status === "active") {
          this.steps[i].status = "pass";
        }
      }
      if (this.steps[index]) {
        this.steps[index].status = "active";
        if (detail) this.steps[index].detail = detail;
      }
      this._render(this._title);
    }

    finish(ok, summary) {
      this.steps.forEach((s) => {
        if (s.status === "active") s.status = ok ? "pass" : "fail";
        if (s.status === "pending") s.status = ok ? "pass" : "skip";
      });
      const elapsed = ((Date.now() - this._start) / 1000).toFixed(1);
      this._render(this._title, summary || (ok ? `Done in ${elapsed}s` : "Failed"));
      this.container?.classList.toggle("scan-failed", !ok);
    }

    applyServerSteps(serverSteps, summary, overallOk) {
      if (!serverSteps?.length) return;
      this.steps = serverSteps.map((s) => ({
        label: s.label,
        detail: s.detail || "",
        status: s.status === "fail" ? "fail" : s.status === "skip" ? "skip" : "pass",
      }));
      const ok = overallOk != null ? !!overallOk : !serverSteps.some((s) => s.status === "fail");
      this.finish(ok, summary);
    }

    failEarly(title, message, failedLabel) {
      this.steps = [{ label: failedLabel || "Download from GitHub", status: "fail", detail: message }];
      this.finish(false, message);
    }

    hide() {
      if (this.container) this.container.hidden = true;
    }

    _render(title, foot) {
      this._title = title;
      if (!this.container) return;
      const icon = { pending: "○", active: "◉", pass: "✓", fail: "✗", skip: "–" };
      this.container.innerHTML = `
        <div class="scan-progress">
          <div class="scan-progress-head">
            <span class="scan-spinner ${this.steps.some((s) => s.status === "active") ? "spin" : ""}"></span>
            <div>
              <p class="scan-progress-title">${escapeHtml(title)}</p>
              <p class="scan-progress-sub">${foot || "Working — see steps below"}</p>
            </div>
          </div>
          <ol class="scan-step-list">
            ${this.steps.map((s) => `
              <li class="scan-step ${s.status}">
                <span class="scan-step-icon">${icon[s.status] || "○"}</span>
                <div>
                  <strong>${escapeHtml(s.label)}</strong>
                  ${s.detail ? `<small>${escapeHtml(s.detail)}</small>` : ""}
                </div>
              </li>`).join("")}
          </ol>
        </div>`;
    }
  }

  window.ScanProgress = ScanProgress;

  /** Fake step timer while waiting for long API call */
  window.runWithProgressUI = async function (title, stepDefs, apiCall, onStep) {
    const panel = document.getElementById("scan-progress-panel");
    const prog = new ScanProgress(panel);
    prog.show(title, stepDefs);
    showToast(title, stepDefs[0]?.label || "Starting…", { type: "info", duration: 4000 });

    let stepIdx = 0;
    prog.advance(0);
    const tick = setInterval(() => {
      if (stepIdx < stepDefs.length - 1) {
        stepIdx++;
        prog.advance(stepIdx, "In progress…");
        onStep?.(stepIdx, stepDefs[stepIdx]?.label);
      }
    }, 3500);

    try {
      const data = await apiCall();
      clearInterval(tick);

      if (data?.steps?.length) {
        prog.applyServerSteps(data.steps, data.summary, data.ok);
      } else if (data?.ok === false) {
        prog.failEarly(title, data.summary || data.stderr || "Scan failed", "Scan failed");
      } else {
        prog.finish(!!data?.ok, data?.summary);
      }

      if (data?.ok) {
        showToast("Report ready", data.report_url
          ? "Your HTML diagram is saved. Open it below or in Your Reports →"
          : "Scan finished successfully.", {
          type: "success",
          duration: 14000,
          actions: data.report_url ? [
            { id: "view", label: "View report", onClick: () => window.showReportViewer?.(data.report_url, data.slug || title) },
            { id: "gallery", label: "Your Reports", onClick: () => document.getElementById("report-gallery")?.scrollIntoView({ behavior: "smooth" }) },
          ] : [],
        });
      } else {
        showToast("Scan failed", (data?.stderr || data?.detail || "Check Activity log for details.").slice(0, 200), { type: "error", duration: 10000 });
      }
      return data;
    } catch (e) {
      clearInterval(tick);
      prog.finish(false, e.message);
      showToast("Error", e.message, { type: "error" });
      throw e;
    }
  };
})();
