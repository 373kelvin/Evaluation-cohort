/** Interactive project guide chat */
(function () {
  function esc(s) {
    if (!s) return "";
    const d = document.createElement("div");
    d.textContent = String(s);
    return d.innerHTML;
  }

  function mdLite(text) {
    if (!text) return "<em>No response.</em>";
    return esc(text)
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br>");
  }

  class ProjectAIChat {
    constructor(root, projectId) {
      this.root = root;
      this.projectId = projectId;
      this.activeAgent = "master";
      this.health = {};
      this._render();
      this._loadIntro();
    }

    _render() {
      this.root.innerHTML = `
        <div class="ai-chat">
          <div class="ai-chat-tabs" id="ai-tabs">
            <button type="button" class="ai-tab active" data-agent="master">Master Guide</button>
          </div>
          <div class="ai-messages" id="ai-messages"></div>
          <div class="ai-typing" id="ai-typing" hidden><span></span><span></span><span></span></div>
          <form class="ai-input-row" id="ai-form">
            <input type="text" id="ai-input" placeholder="Ask about this project…" autocomplete="off" />
            <button type="submit" class="btn btn-primary btn-sm">Ask</button>
          </form>
          <div class="ai-quick" id="ai-quick"></div>
        </div>`;
      this.messagesEl = this.root.querySelector("#ai-messages");
      this.typingEl = this.root.querySelector("#ai-typing");
      this.tabsEl = this.root.querySelector("#ai-tabs");
      this.quickEl = this.root.querySelector("#ai-quick");

      this.root.querySelector("#ai-form").addEventListener("submit", (e) => {
        e.preventDefault();
        const input = this.root.querySelector("#ai-input");
        const text = input.value.trim();
        if (text) this.send(text);
        input.value = "";
      });
    }

    async _fetchHealth() {
      try {
        const res = await fetch("/api/projects/health", { signal: AbortSignal.timeout(4000) });
        if (res.ok) {
          const data = await res.json();
          this.health = data.health || {};
        }
      } catch (_) {}
    }

    _setQuick(prompts) {
      this.quickEl.innerHTML = "";
      prompts.forEach((p) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "ai-chip";
        btn.textContent = p;
        btn.addEventListener("click", () => this.send(p));
        this.quickEl.appendChild(btn);
      });
    }

    _setTabs(subs) {
      this.tabsEl.innerHTML = `<button type="button" class="ai-tab active" data-agent="master">Master Guide</button>` +
        (subs || []).map((a) =>
          `<button type="button" class="ai-tab" data-agent="${a.id}" title="${esc(a.tip)}">${a.id}</button>`
        ).join("");
      this.tabsEl.querySelectorAll(".ai-tab").forEach((tab) => {
        tab.addEventListener("click", () => {
          this.activeAgent = tab.dataset.agent;
          this.tabsEl.querySelectorAll(".ai-tab").forEach((t) => t.classList.toggle("active", t === tab));
          this.addMessage("system", `Switched to **${tab.textContent}** specialist.`);
        });
      });
    }

    addMessage(kind, text, meta = {}) {
      const div = document.createElement("div");
      div.className = `ai-msg ai-msg-${kind}`;
      if (kind === "user") {
        div.innerHTML = `<div class="ai-bubble user">${mdLite(text)}</div>`;
      } else if (kind === "system") {
        div.innerHTML = `<div class="ai-bubble system">${mdLite(text)}</div>`;
      } else {
        const who = meta.agent || "Guide";
        div.innerHTML = `
          <div class="ai-avatar">${esc(who.charAt(0))}</div>
          <div class="ai-bubble bot">
            <span class="ai-who">${esc(who)}${meta.role ? " · " + esc(meta.role) : ""}</span>
            <div class="ai-text">${mdLite(text)}</div>
          </div>`;
      }
      this.messagesEl.appendChild(div);
      this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
    }

    async _getReply(message) {
      await this._fetchHealth();
      try {
        const res = await fetch(`/api/chat/${this.projectId}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message, agent: this.activeAgent }),
          signal: AbortSignal.timeout(5000),
        });
        if (res.ok) {
          const data = await res.json();
          if (data.reply) return data;
        }
      } catch (_) {}
      return window.answerChat(this.projectId, message, this.activeAgent, this.health);
    }

    async _typeReply(data) {
      if (!data?.reply) {
        data = window.answerChat(this.projectId, "", "master", this.health);
      }
      this.typingEl.hidden = false;
      await new Promise((r) => setTimeout(r, 300 + Math.random() * 300));
      this.typingEl.hidden = true;
      this.addMessage("bot", data.reply, data);
      if (data.sub_agents) this._setTabs(data.sub_agents);
    }

    async send(message) {
      this.addMessage("user", message);
      const data = await this._getReply(message);
      await this._typeReply(data);
    }

    async _loadIntro() {
      await this._fetchHealth();
      const data = window.answerChat(this.projectId, "", "master", this.health);
      await this._typeReply(data);
      const prompts = ["Is it running?", "What does the walkthrough do?", "How does it work?", "What can you help with?"];
      if (this.projectId === "fraud-score") prompts[2] = "Explain the scoring";
      if (this.projectId === "entity-diagrams") prompts[2] = "What is B1 vs B2?";
      this._setQuick(prompts);
    }

    async narrateDemoStart() {
      await this._fetchHealth();
      this.addMessage("system", "▶ Running step-by-step validation…");
      const data = window.answerChat(this.projectId, "demo test", "master", this.health);
      await this._typeReply(data);
    }

    async narrateDemoResults(demoData) {
      const k = window.AI_KNOWLEDGE[this.projectId];
      const name = k?.master?.name || "Guide";
      const lines = [`Walkthrough complete: **${demoData.passed}/${demoData.total}** checks passed.\n`];
      (demoData.steps || []).slice(0, 5).forEach((s) => {
        lines.push(`${s.status === "pass" ? "✓" : "✗"} **${s.name}**: ${s.detail}`);
        if (s.score != null) lines.push(`   → Score: **${s.score}/100** (${s.risk})`);
      });
      if (demoData.tip) lines.push(`\n${demoData.tip}`);
      await this._typeReply({ reply: lines.join("\n"), agent: name, role: k?.master?.role || "" });
    }
  }

  window.ProjectAIChat = ProjectAIChat;
})();
