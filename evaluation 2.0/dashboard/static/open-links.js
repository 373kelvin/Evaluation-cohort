/** Open live apps/docs — one click, no localhost URLs shown in UI */
window.openProjectLink = async function (projectId, target, href) {
  if (href) {
    window.open(href, "_blank", "noopener");
    return { ok: true };
  }
  try {
    const res = await fetch(`/api/open-url/${projectId}/${target}`);
    const data = await res.json().catch(() => ({}));
    if (res.ok && data.url) {
      window.open(data.url, "_blank", "noopener");
      return { ok: true };
    }
    const d = data.detail;
    const msg = (typeof d === "object" && d?.message ? d.message : d) || "Service is not running.";
    const cmd = typeof d === "object" ? d.start_cmd : "";
    alert(msg + (cmd ? "\n\nStart it with:\n" + cmd : ""));
    return { ok: false, message: msg };
  } catch (e) {
    alert(
      "Could not reach the dashboard.\n\n" +
        "Open http://127.0.0.1:9010 in your browser (not an HTML file from Finder).\n" +
        "If blank, run: bash \"evaluation 2.0/scripts/start_dashboard.sh\" restart"
    );
    return { ok: false };
  }
};

window.renderOpenButtons = function (container, projectId, links, liveReady) {
  if (!container || !links?.length) return;
  const wrap = document.createElement("div");
  wrap.className = "open-links-row";
  links.forEach((link) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn btn-open-live" + (liveReady || link.href ? "" : " needs-start");
    btn.innerHTML = `<strong>${link.label}</strong><small>${link.hint || (liveReady ? "Opens in new tab" : "Start service first")}</small>`;
    btn.addEventListener("click", () => {
      if (link.href) {
        window.open(link.href, link.href.startsWith("http") ? "_blank" : "_self", "noopener");
      } else {
        window.openProjectLink(projectId, link.target);
      }
    });
    wrap.appendChild(btn);
  });
  container.appendChild(wrap);
};
