"""Interactive AI chat — master project agent + sub-agents with project knowledge."""
from __future__ import annotations

import random
import re
from typing import Any

from project_guides import PROJECT_GUIDES

# Extra knowledge per project for richer answers
EXTRA_KNOWLEDGE: dict[str, dict[str, Any]] = {
    "entity-diagrams": {
        "master_title": "Master Archivist",
        "demo_explain": (
            "The walkthrough runs the live scanner: inventory (B1), route mapping (B2), "
            "and HTML report generation on the fintech demo folder."
        ),
        "faqs": {
            "b1": "B1 scans every file and lists classes, configs, models, and utilities. Output goes to outputs/b1-artifact-inventory/.",
            "b2": "B2 finds every @app.get / @app.post route and builds a clickable HTML diagram.",
            "scan": "Point inventory.py or analyze.py at any folder — no server needed.",
        },
    },
    "fastapi-tx": {
        "master_title": "Master Ledger AI",
        "demo_explain": (
            "The walkthrough validates the ledger API: health check, credit transaction, "
            "invalid amount rejection, and balance recalculation. Uses the live API when the service is running."
        ),
        "faqs": {
            "balance": "GET /balance adds all credits minus all debits automatically.",
            "validation": "Pydantic rejects negative amounts with HTTP 422 before anything is saved.",
            "b4": "B4 agent built this greenfield FastAPI service from scratch in about an hour.",
        },
    },
    "fraud-score": {
        "master_title": "Master Security AI",
        "demo_explain": (
            "The walkthrough submits test transactions and scores them 0–100 using the Rust engine rules: "
            "large amount (+40), odd hour (+20), risky country (+30). Score cards show LOW / MEDIUM / HIGH risk."
        ),
        "faqs": {
            "score": "Score 0–100: 0–39 LOW (green), 40–69 MEDIUM (amber), 70+ HIGH (red).",
            "pipeline": "Python ingests → Node worker polls → Rust engine scores → score saved back.",
            "rust": "Rust reads JSON from stdin, applies rules, writes JSON score to stdout.",
            "a3": "A3 Polyglot Agent designed Python + Node + Rust to each do one job well.",
        },
    },
    "fintech-demo": {
        "master_title": "Master Demo AI",
        "demo_explain": (
            "The walkthrough validates the fintech platform: folder scan, B1 inventory, "
            "B2 route mapping, API health, and fraud alert endpoints."
        ),
        "faqs": {
            "demo": "Best project to show scanning — richest codebase in the repo.",
            "tables": "5 database tables: accounts, payments, alerts, users, audit_log.",
        },
    },
}

SUB_AGENT_VOICES = {
    "B1": "I scan folders and list every important file, class, and config.",
    "B2": "I map every API route to its source file and line number.",
    "B3": "I find test files, run pytest, and report pass/fail.",
    "B4": "I build FastAPI services from scratch with validation and tests.",
    "A3": "I wire Python, Node, and Rust into one working pipeline.",
}


def _pick(texts: list[str]) -> str:
    return random.choice(texts)


def _match_topic(msg: str) -> str:
    m = msg.lower()
    if any(w in m for w in ("demo test", "demo tests", "what does demo", "run demo")):
        return "demo"
    if any(w in m for w in ("score", "fraud", "risk", "rust", "pipeline")):
        return "fraud" if "fraud-score" in m else "score"
    if any(w in m for w in ("b1", "inventory", "scan", "artifact")):
        return "b1"
    if any(w in m for w in ("b2", "endpoint", "route", "map", "diagram")):
        return "b2"
    if any(w in m for w in ("b3", "test", "pytest")):
        return "b3"
    if any(w in m for w in ("b4", "fastapi", "transaction", "balance", "ledger")):
        return "b4"
    if any(w in m for w in ("a3", "polyglot", "node", "worker")):
        return "a3"
    if any(w in m for w in ("hello", "hi", "hey", "help", "start")):
        return "greet"
    if any(w in m for w in ("how", "work", "flow", "explain")):
        return "how"
    return "general"


def chat(project_id: str, message: str, agent: str = "master") -> dict:
    guide = PROJECT_GUIDES.get(project_id, {})
    extra = EXTRA_KNOWLEDGE.get(project_id, {})
    if not guide:
        return {"reply": "I don't know that project.", "agent": "System", "role": "error"}

    msg = (message or "").strip()
    topic = _match_topic(msg)

    # Sub-agent mode
    if agent != "master":
        sub = next((a for a in guide.get("agents_here", []) if a["id"] == agent), None)
        if sub:
            voice = SUB_AGENT_VOICES.get(agent, sub.get("tip", ""))
            if topic == "demo":
                reply = f"I'm {sub['name']}. {voice} Demo Tests include checks for my task ({agent})."
            elif topic in ("b1", "b2", "b3", "b4", "a3") and agent.upper().startswith(topic.upper()[:2]):
                reply = f"{sub['tip']} Click the buttons on the dashboard to run my task live."
            else:
                reply = f"Hi — I'm the {sub['name']}. {sub['tip']} Ask me about {agent} or switch to Master AI for the full picture."
            return {
                "reply": reply,
                "agent": sub["name"],
                "role": agent,
                "agent_id": agent,
            }

    # Master agent
    master_name = guide.get("agent_name", "Master AI")
    master_title = extra.get("master_title", guide.get("agent_role", "Project Guide"))
    subs = guide.get("agents_here", [])

    if topic == "greet" or not msg:
        sub_list = ", ".join(f"**{a['id']}** ({a['name']})" for a in subs)
        reply = _pick([
            f"Hello! I'm **{master_name}**, your {master_title}. I know everything about this project. "
            f"My team: {sub_list}. Ask me anything — or click **Run Demo Tests** to see it in action.",
            f"Hi there — **{master_name}** here. I'll guide you through this project step by step. "
            f"Try: \"how does it work?\", \"what does demo test do?\", or pick a sub-agent below.",
        ])
    elif topic == "demo":
        reply = extra.get("demo_explain", "The walkthrough runs automated validation checks for this project.")
        reply += f"\n\n**Tip:** Click ▶ Demo Tests on the project card — results appear right here in the chat and in the panel below."
    elif topic == "how":
        steps = "\n".join(f"{f['step']}. **{f['title']}** — {f['detail']}" for f in guide.get("flow", []))
        reply = f"Here's how **{guide.get('theme_label', project_id)}** works:\n\n{steps}"
    elif topic in extra.get("faqs", {}):
        reply = extra["faqs"][topic]
    elif topic == "score" and project_id == "fraud-score":
        reply = extra["faqs"].get("score", "") + "\n\n" + extra["faqs"].get("pipeline", "")
    elif re.search(r"\b(B[1-4]|A[1-6])\b", msg.upper()):
        aid = re.search(r"\b(B[1-4]|A[1-6])\b", msg.upper()).group(1)
        sub = next((a for a in subs if a["id"] == aid), None)
        if sub:
            reply = f"**{aid} — {sub['name']}**: {sub['tip']}\n\nSwitch to the {aid} tab below to talk to that agent directly."
        else:
            reply = f"{aid} is not assigned to this project. My team here: {', '.join(a['id'] for a in subs)}."
    else:
        reply = _pick([
            f"{guide.get('summary', '')}\n\nAsk me about **demo tests**, **how it works**, or a task like B1/B2/A3.",
            f"I'm {master_name}. {guide.get('greeting', '')}\n\nWhat would you like to explore?",
        ])

    return {
        "reply": reply,
        "agent": master_name,
        "role": master_title,
        "agent_id": "master",
        "sub_agents": [{"id": a["id"], "name": a["name"], "tip": a["tip"]} for a in subs],
    }


def narrate_demo_start(project_id: str) -> dict:
    extra = EXTRA_KNOWLEDGE.get(project_id, {})
    result = chat(project_id, "what does demo test do", "master")
    result["reply"] = f"▶ **Running demo tests now…**\n\n{extra.get('demo_explain', result['reply'])}"
    return result


def narrate_demo_results(project_id: str, demo_data: dict) -> dict:
    guide = PROJECT_GUIDES.get(project_id, {})
    name = guide.get("agent_name", "Agent")
    passed = demo_data.get("passed", 0)
    total = demo_data.get("total", 0)
    lines = [f"✅ **Demo complete** — {passed}/{total} checks passed.\n"]
    for s in demo_data.get("steps", [])[:5]:
        icon = "✓" if s.get("status") == "pass" else "✗"
        lines.append(f"{icon} **{s.get('name')}**: {s.get('detail')}")
        if s.get("score") is not None:
            lines.append(f"   → Fraud score: **{s['score']}/100** ({s.get('risk', '?')})")
    lines.append(f"\n{demo_data.get('tip', '')}")
    return {
        "reply": "\n".join(lines),
        "agent": name,
        "role": guide.get("agent_role", ""),
        "agent_id": "master",
        "narration": True,
    }
