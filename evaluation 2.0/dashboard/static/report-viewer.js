/** Inline report viewer — proper HTML insight reports without leaving the page */
window.showReportViewer = function (url, title) {
  const panel = document.getElementById("report-panel");
  const frame = document.getElementById("report-frame");
  const label = document.getElementById("report-title");
  if (!panel || !frame) {
    window.open(url, "_blank", "noopener");
    return;
  }
  if (label) label.textContent = title || "Insight Report";
  frame.src = url;
  panel.hidden = false;
  panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
};

window.hideReportViewer = function () {
  const panel = document.getElementById("report-panel");
  const frame = document.getElementById("report-frame");
  if (panel) panel.hidden = true;
  if (frame) frame.src = "about:blank";
};

window.initReportViewer = function () {
  document.getElementById("report-close")?.addEventListener("click", window.hideReportViewer);
  document.getElementById("report-newtab")?.addEventListener("click", () => {
    const src = document.getElementById("report-frame")?.src;
    if (src && src !== "about:blank") window.open(src, "_blank", "noopener");
  });
  document.getElementById("report-fullscreen")?.addEventListener("click", () => {
    const panel = document.getElementById("report-panel");
    panel?.classList.toggle("report-fullscreen");
    document.getElementById("report-fullscreen").textContent =
      panel?.classList.contains("report-fullscreen") ? "Exit fullscreen" : "Fullscreen";
  });
};

window.loadReportGallery = async function (container, onSelect) {
  if (!container) return;
  try {
    const res = await fetch("/api/reports");
    const data = await res.json();
    const reports = data.reports || [];
    if (!reports.length) {
      container.innerHTML = `<p class="muted">No reports yet — run a scan or walkthrough to generate one.</p>`;
      return;
    }
    container.innerHTML = reports.slice(0, 8).map((r) => `
      <button type="button" class="report-chip" data-url="${r.url}" data-name="${r.name}">
        <strong>${r.name}</strong>
        <small>${r.size_kb} KB</small>
      </button>`).join("");
    container.querySelectorAll(".report-chip").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (onSelect) onSelect(btn.dataset.url, btn.dataset.name);
        else window.showReportViewer(btn.dataset.url, btn.dataset.name);
      });
    });
  } catch (_) {
    container.innerHTML = `<p class="muted">Could not load report list.</p>`;
  }
};
