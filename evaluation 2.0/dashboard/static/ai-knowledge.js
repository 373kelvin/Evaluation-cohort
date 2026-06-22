/** Project guide — answers + live service status */
window.AI_START_CMD = {
  "entity-diagrams": null,
  "fastapi-tx": "cd fastapi_transactions && uvicorn app.main:app --port 8000",
  "fraud-score": "cd fraud-score-system/service && uvicorn app.main:app --port 8001  # also start Node worker + Rust for full pipeline",
  "fintech-demo": "cd sample-projects/fintech-platform && PYTHONPATH=. uvicorn app.main:app --port 8002",
};

window.AI_KNOWLEDGE = {
  "entity-diagrams": {
    master: { name: "Archie", role: "Repository Inventory Agent" },
    subs: [
      { id: "B1", name: "Repo Inventory Agent", tip: "Finds models, services, configs — run B1 Scan button" },
      { id: "B2", name: "API Endpoint Agent", tip: "Maps routes to source files — run B2 Map button" },
    ],
    demo: "Paste a **GitHub URL** or **upload .zip** — scanner reads routes + entities. Django, FastAPI, Express, Flask supported. Report shows **Scanner coverage** so you know what was detected.",
    how: "1. GitHub / zip / folder\n2. Static scan (B1 inventory + B2 analyze.py)\n3. HTML report: routes, tables, ER diagram, gaps if any\n\nDeep work (30 min): run B1/B2 agents in Cursor with prompts from agents/",
    agents: "**B1** + **B2** — real Python scanner, not chat AI. Reads source files. Cursor agents use the same tools for the 30-minute eval tasks.",
    score: "No fraud scoring on this project — it is a code scanner only.",
    live: "CLI scanner — ready to use. B1/B2 buttons run the analyzer directly.",
  },
  "fastapi-tx": {
    master: { name: "Tessa", role: "Transactions Service Agent" },
    subs: [
      { id: "B4", name: "FastAPI Greenfield Agent", tip: "Built POST/GET /transactions and GET /balance" },
      { id: "B3", name: "Test Discovery Agent", tip: "8 pytest tests — Run All Tests button" },
    ],
    demo: "The walkthrough checks /health, posts sample transactions, validates error handling, and recalculates balance. When the service is running, it uses the live API.",
    how: "POST /transactions (credit/debit) → GET /balance sums everything. Bad amounts return HTTP 422.",
    agents: "**B4** built the service. **B3** runs tests. Ask \"is it running?\" for live status.",
    score: "No fraud scoring — this is a ledger app.",
    live_online: "Service is **ONLINE**. Click **Open Web App** or **Open API Docs** on the project page.",
    live_offline: "Service is **OFFLINE**. Use the start command on the project page, then click the Open buttons.",
  },
  "fraud-score": {
    master: { name: "Sam", role: "Fraud Pipeline Orchestrator" },
    subs: [
      { id: "A3", name: "Polyglot System Agent", tip: "Python service + Node worker + Rust CLI" },
      { id: "B3", name: "Test Discovery Agent", tip: "Python + integration tests" },
    ],
    demo: "The walkthrough submits test transactions and scores them 0–100 using the same rules as the Rust engine: large amount (+40), odd hour (+20), risky country (+30).",
    how: "Python stores txn as pending → Node worker polls → Rust scores → score saved. Full pipeline needs all three services running.",
    agents: "**A3** designed the polyglot stack. **B3** runs tests.",
    score: "Score 0–100 from deterministic rules: >₹10k (+40), hour 0–4 (+20), country not IN/US/GB (+30).",
    live_online: "Python service is **ONLINE**. Click **Open API Docs** to post a test transaction. Full scoring also needs Node worker + Rust.",
    live_offline: "Python service is **OFFLINE**. Start it from the project page, then use the Open buttons.",
  },
  "fintech-demo": {
    master: { name: "Fin", role: "Fintech Demo Guide" },
    subs: [
      { id: "B1", name: "Repo Inventory Agent", tip: "Scans this demo — ~27 artifacts" },
      { id: "B2", name: "API Endpoint Agent", tip: "Maps ~12 routes" },
    ],
    demo: "The walkthrough validates the fintech platform structure — inventory scan, route mapping, and API health checks.",
    how: "Best demo for B1/B2 scanning. Optional live API — click **Open API Docs** when online.",
    agents: "**B1** + **B2** on this project. Ask \"is it running?\" before using Open buttons.",
    score: "Fraud alerts exist in the demo schema; scoring lives in the Fraud Score project.",
    live_online: "Fintech API is **ONLINE** — click **Open API Docs** on the project page.",
    live_offline: "Fintech API is **OFFLINE** — start it from the project page, then click Open API Docs.",
  },
};

function _statusBlock(projectId, health) {
  const k = window.AI_KNOWLEDGE[projectId];
  if (!k) return "";
  const h = health?.[projectId];
  if (!h) return "";
  if (projectId === "entity-diagrams" || h.kind === "cli") return k.live || "";
  if (h.online) return k.live_online || "Service is ONLINE.";
  return k.live_offline || "Service is OFFLINE — start it to run live checks.";
}

function _isProjectQuestion(msg) {
  if (!msg) return true;
  if (/weather|football|bitcoin|president|news|joke|recipe|movie|song|capital of|who won/i.test(msg)) return false;
  return /demo|test|score|fraud|b1|b2|b3|b4|a3|scan|agent|work|flow|how|balance|ledger|pipeline|rust|endpoint|inventory|run|start|live|offline|status|help|hello|hi|hey|open|link|docs|url|running|which|who|explain|show|see|try|button|port|8000|8001|8002|project|guide|ai|ledger|transaction|fintech|insight|scanner|map|pytest|fastapi|uvicorn|node|worker|rust|polyglot|artifact|report|diagram|balance|credit|debit|alert|table|route|api|service|cli|online|offline|walkthrough|help with/i.test(msg);
}

window.answerChat = function (projectId, message, agentId, health) {
  const k = window.AI_KNOWLEDGE[projectId];
  if (!k) return { reply: "Unknown project.", agent: "System", role: "" };

  const msg = (message || "").trim();
  const lower = msg.toLowerCase();
  const status = _statusBlock(projectId, health);

  if (agentId !== "master") {
    const sub = k.subs.find((s) => s.id === agentId);
    if (!sub) return { reply: "Unknown agent.", agent: "System", role: "" };
    if (msg && !_isProjectQuestion(msg)) {
      return {
        reply: `I'm **${sub.name}** — I specialize in **${agentId}** tasks on this project.`,
        agent: sub.name, role: agentId, agent_id: agentId,
      };
    }
    return {
      reply: `I'm **${sub.name}** (${agentId}). ${sub.tip}\n\n${status}`,
      agent: sub.name, role: agentId, agent_id: agentId,
    };
  }

  if (msg && !_isProjectQuestion(msg)) {
    return {
      reply: "I focus on **this project only**. Try: \"Is it running?\", \"What does the walkthrough do?\", or \"How does it work?\"",
      agent: k.master.name, role: k.master.role, agent_id: "master",
      sub_agents: k.subs.map((s) => ({ id: s.id, name: s.name, tip: s.tip })),
    };
  }

  if (/running|online|offline|live|status|working|up|down|reachable|open|link|docs|url|try it/.test(lower)) {
    const extra = /open|link|docs|url|try|see/.test(lower) && status.includes("OFFLINE")
      ? "\n\nStart the service from the project page, then use the **Open** buttons."
      : "";
    return {
      reply: (status || "Checking status… refresh and ask again.") + extra,
      agent: k.master.name, role: k.master.role, agent_id: "master",
      sub_agents: k.subs.map((s) => ({ id: s.id, name: s.name, tip: s.tip })),
    };
  }

  let reply;
  if (!msg || /^(hi|hello|hey|help|start)$/.test(lower)) {
    reply = `I'm **${k.master.name}**, your guide for this project.\n\n${status}\n\nAsk: "What does the walkthrough do?", "Is it running?", or "How does it work?"`;
  } else if (/demo|walkthrough/.test(lower)) {
    reply = k.demo + "\n\n" + status;
  } else if (/score|fraud|risk|rust|pipeline/.test(lower)) {
    reply = k.score + (projectId === "fraud-score" ? "\n\n" + k.how : "");
  } else if (/how|work|flow/.test(lower) && !/score/.test(lower)) {
    reply = k.how + "\n\n" + status;
  } else if (/agent|team|which|who/.test(lower)) {
    reply = k.agents;
  } else if (/b1|inventory|artifact/.test(lower)) {
    reply = k.subs.find((s) => s.id === "B1")?.tip || k.agents;
  } else if (/b2|endpoint|route|map/.test(lower)) {
    reply = k.subs.find((s) => s.id === "B2")?.tip || k.agents;
  } else if (/b3|pytest/.test(lower)) {
    reply = k.subs.find((s) => s.id === "B3")?.tip || "B3 is not on this project.";
  } else if (/b4|balance|ledger/.test(lower)) {
    reply = k.subs.find((s) => s.id === "B4")?.tip || "B4 is not on this project.";
  } else if (/a3|polyglot|node|worker/.test(lower)) {
    reply = k.subs.find((s) => s.id === "A3")?.tip || "A3 is not on this project.";
  } else if (/help with|what can you/.test(lower)) {
    reply = `I guide evaluators through **${projectId.replace(/-/g, " ")}**: walkthroughs, scans, tests, and live service status.\n\n${status}`;
  } else {
    reply = `I focus on **this project**. ${status}\n\nTry: "Is it running?", "What does the walkthrough do?", or "How does it work?"`;
  }

  return {
    reply,
    agent: k.master.name,
    role: k.master.role,
    agent_id: "master",
    sub_agents: k.subs.map((s) => ({ id: s.id, name: s.name, tip: s.tip })),
  };
};
