"""Render a Project into a single self-contained interactive HTML file."""
import html
import json


def _esc(s):
    return html.escape(str(s), quote=True)


def _mermaid_er(project):
    if not project.tables:
        return "erDiagram\n  EMPTY {\n    string none\n  }"
    lines = ["erDiagram"]
    for r in project.relationships:
        conn = "||..o{" if r.inferred else "||--o{"
        lines.append(f'    {r.parent.upper()} {conn} {r.child.upper()} : "{_mm(r.key)}"')
    for t in project.tables:
        lines.append(f"    {t.name.upper()} {{")
        for c in t.columns[:14]:
            typ = (c.type or "string").split("(")[0]
            key = "PK" if c.pk else ("FK" if c.fk_to else "")
            note = c.notes.replace('"', "")
            comment = f' "{note}"' if note else ""
            lines.append(f"        {typ} {c.name} {key}{comment}".rstrip())
        lines.append("    }")
    return "\n".join(lines)


def _mm(s):
    return str(s).replace('"', "").replace(":", " ")[:40] or "rel"


def _graph(project):
    palette = {"auth": "#7c5cff", "student": "#5a8dee", "admin": "#f0a33c", "general": "#36c692"}
    nodes = [{"id": t.name, "label": t.name + ("\n(inferred)" if t.inferred else ""),
              "shape": "box", "color": "#5a8dee" if not t.inferred else "#7c5cff"}
             for t in project.tables]
    edges = [{"from": r.parent, "to": r.child, "label": r.key,
              "dashes": bool(r.inferred),
              "color": "#f0a33c" if r.inferred else "#9a9aac"}
             for r in project.relationships]
    return json.dumps(nodes), json.dumps(edges)


ROLE_CLASS = {"auth": "r-auth", "student": "r-student", "admin": "r-admin", "general": "r-gen"}


def render(project):
    nodes_js, edges_js = _graph(project)
    er = _mermaid_er(project)

    # features grouped
    groups = {}
    for f in project.features:
        groups.setdefault(f.role, []).append(f)
    feat_html = ""
    for role in ("auth", "student", "admin", "general"):
        if role not in groups:
            continue
        feat_html += f"<h3>{role.title()} <small style='color:var(--muted)'>({len(groups[role])})</small></h3>"
        for f in groups[role]:
            rc = ROLE_CLASS.get(f.role, "r-gen")
            feat_html += (f"<div class='feat'><div class='h'><span>{_esc(f.name)}</span>"
                          f"<span class='role {rc}'>{f.role}</span></div>"
                          f"<div class='f'>{_esc(f.detail)} — <code>{_esc(f.source)}</code></div></div>")

    # entity tables
    ent_html = ""
    for t in project.tables:
        pill = "<span class='pill'>inferred</span>" if t.inferred else ""
        rows = ""
        for c in t.columns:
            cons = []
            if c.pk: cons.append("PK")
            if c.fk_to: cons.append("FK→" + _esc(c.fk_to))
            if c.notes: cons.append(_esc(c.notes))
            rows += f"<tr><td>{_esc(c.name)}</td><td>{_esc(c.type or '?')}</td><td>{', '.join(cons)}</td></tr>"
        ent_html += (f"<h3>{_esc(t.name)} {pill}</h3>"
                     f"<table><tr><th>Column</th><th>Type</th><th>Constraints</th></tr>{rows}</table>"
                     f"<small style='color:var(--muted)'>source: <code>{_esc(t.source)}</code></small>")

    rel_rows = ""
    for r in project.relationships:
        kind = "inferred" if r.inferred else "declared FK"
        rel_rows += (f"<tr><td>{_esc(r.parent)} → {_esc(r.child)}</td><td>{_esc(r.key)}</td>"
                     f"<td>{kind}</td><td><code>{_esc(r.source)}</code></td></tr>")

    comp_rows = "".join(
        f"<tr><td><code>{_esc(n)}</code></td><td>{_esc(role)}</td><td>{cnt}</td></tr>"
        for n, role, cnt in project.components) or "<tr><td colspan=3 class='muted'>—</td></tr>"
    if project.exec_map:
        exec_section = ("<section id='exec-s'><h2>Execution / data flow</h2>"
                        "<p class='muted'>Most write-heavy endpoint: <code>" + _esc(project.exec_title) +
                        "</code></p><div class='mermaid'>" + project.exec_map + "</div></section>")
    else:
        exec_section = ""
    findings = "".join(f"<li>{_esc(x)}</li>" for x in project.findings) or "<li>No notable issues flagged.</li>"
    coverage_html = "".join(f"<li>{_esc(x)}</li>" for x in project.scan_coverage)
    cov_section = (
        f"<div class='callout c-tip'><b>Scanner coverage</b><ul>{coverage_html}</ul>"
        f"<small class='muted'>Static analysis — reads source files, not an LLM.</small></div>"
        if coverage_html else ""
    )
    runs = "".join(f"<div class='callout c-tip'><code>{_esc(c)}</code></div>" for c in project.how_to_run) or "<p class='muted'>Run command could not be determined from the code.</p>"
    entries = ", ".join(f"<code>{_esc(e)}</code>" for e in project.entry_points) or "<span class='muted'>—</span>"

    return TEMPLATE.format(
        name=_esc(project.name),
        verdict=_esc(project.verdict),
        langs=_esc(", ".join(project.languages) or "—"),
        fws=_esc(", ".join(project.frameworks) or "—"),
        data_layer=_esc(project.data_layer or "—"),
        db=_esc(project.db_name or "—"),
        n_tables=len(project.tables), n_feats=len(project.features), n_files=project.file_count,
        runs=runs, entries=entries,
        feat_html=feat_html or "<p class='muted'>No endpoints detected.</p>",
        ent_html=ent_html or "<p class='muted'>No tables found.</p>",
        rel_rows=rel_rows or "<tr><td colspan=4 class='muted'>No relationships found.</td></tr>",
        findings=findings, er=er, nodes_js=nodes_js, edges_js=edges_js,
        arch=project.architecture or 'flowchart LR\n  A[No components detected]',
        comp_rows=comp_rows, exec_section=exec_section,
        inferred_banner=("<div class='callout c-warn'><b>⚠ Schema inferred from queries</b> — no DDL file was found; tables/columns/relationships were reconstructed from SQL in the code.</div>" if project.tables and not project.has_ddl else ""),
        coverage_banner=cov_section,
    )


TEMPLATE = r"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} — Project Insight</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script src="https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js"></script>
<style>
:root{{--bg:#16161c;--panel:#20202a;--panel2:#282834;--text:#e8e8f0;--muted:#9a9aac;--accent:#a98bff;--border:#33333f;--info:#4aa3ff;--tip:#36c692;--warn:#f0a33c;--danger:#ff6b6b}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.6 -apple-system,Segoe UI,Roboto,Arial,sans-serif;display:flex}}
a{{color:var(--accent);text-decoration:none}} .muted{{color:var(--muted)}}
nav{{position:sticky;top:0;height:100vh;width:210px;flex:0 0 210px;background:var(--panel);border-right:1px solid var(--border);padding:18px 12px;overflow:auto}}
nav .brand{{font-weight:700}} nav .tag{{color:var(--muted);font-size:11px;margin-bottom:12px}}
nav a{{display:block;padding:6px 10px;border-radius:8px;color:var(--text);font-size:13.5px}} nav a:hover{{background:var(--panel2)}}
main{{flex:1;max-width:960px;margin:0 auto;padding:28px 38px 120px}} h1{{font-size:28px;margin:0 0 4px}}
.sub{{color:var(--muted);margin-bottom:18px}}
.stats{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:18px}}
.stat{{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:10px 16px;min-width:90px}}
.stat b{{font-size:22px;display:block}} .stat span{{color:var(--muted);font-size:12px}}
section{{background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:20px 24px;margin:0 0 18px}}
section h2{{margin-top:0;font-size:20px}} h3{{font-size:15px;color:var(--accent);margin:18px 0 8px}}
table{{width:100%;border-collapse:collapse;margin:8px 0;font-size:13.5px}} th,td{{text-align:left;padding:7px 10px;border-bottom:1px solid var(--border);vertical-align:top}} th{{color:var(--muted)}}
code{{background:#101015;padding:2px 6px;border-radius:6px;font:12.5px ui-monospace,Consolas,monospace;color:#d8c7ff}}
.callout{{border-left:4px solid var(--info);background:#1c2632;border-radius:8px;padding:10px 14px;margin:10px 0}}
.c-tip{{border-color:var(--tip);background:#172a24}} .c-warn{{border-color:var(--warn);background:#2c2518}} .c-danger{{border-color:var(--danger);background:#2c1d1d}}
.pill{{font-size:11px;padding:2px 8px;border-radius:20px;background:#2c2518;color:var(--warn);border:1px solid var(--warn)}}
#graph{{height:440px;background:#101015;border:1px solid var(--border);border-radius:10px}}
.mermaid{{background:#101015;border-radius:10px;padding:16px;text-align:center}}
.feat{{border:1px solid var(--border);border-radius:10px;padding:10px 13px;margin:7px 0;background:var(--panel2)}}
.feat .h{{font-weight:600;display:flex;justify-content:space-between;gap:8px}} .feat .f{{font-size:12px;color:var(--muted)}}
.role{{font-size:10px;padding:2px 8px;border-radius:20px;text-transform:uppercase}}
.r-student{{background:#16314a;color:#8cc6ff}} .r-admin{{background:#3a2e16;color:#f3c684}} .r-auth{{background:#2a2148;color:#c5b3ff}} .r-gen{{background:#16314a;color:#9fdcc6}}
footer{{color:var(--muted);font-size:12px;text-align:center;padding:22px}}
</style></head><body>
<nav><div class="brand">🔍 Insight</div><div class="tag">{name}</div>
<a href="#ov">Overview</a><a href="#arch-s">Architecture</a><a href="#comp-s">Components</a><a href="#feat">Features</a><a href="#exec-s">Flow</a><a href="#graph-s">Graph</a><a href="#er-s">ER Diagram</a><a href="#ent">Entities</a><a href="#rel">Relationships</a><a href="#find">Findings</a></nav>
<main>
<h1>{name}</h1><div class="sub">{verdict}</div>
<div class="stats"><div class="stat"><b>{n_tables}</b><span>tables</span></div><div class="stat"><b>{n_feats}</b><span>features</span></div><div class="stat"><b>{n_files}</b><span>source files</span></div></div>
{inferred_banner}
{coverage_banner}
<section id="ov"><h2>Overview</h2>
<div class="callout"><b>Stack</b><br>Languages: {langs}<br>Frameworks: {fws}<br>Data layer: {data_layer}<br>Database: {db}</div>
<h3>How to run</h3>{runs}
<h3>Entry points</h3><p>{entries}</p></section>
<section id="arch-s"><h2>System architecture</h2><p class="muted">Components found in the code and how they connect.</p><div class="mermaid">{arch}</div></section>
<section id="comp-s"><h2>Components / modules</h2><table><tr><th>Area</th><th>Role</th><th>Files</th></tr>{comp_rows}</table></section>
<section id="feat"><h2>Features</h2>{feat_html}</section>
{exec_section}
<section id="graph-s"><h2>Interactive data-model graph</h2><p class="muted">Drag nodes, scroll to zoom. Dashed edges are inferred (not declared foreign keys).</p><div id="graph"></div></section>
<section id="er-s"><h2>ER diagram</h2><div class="mermaid">{er}</div></section>
<section id="ent"><h2>Entities</h2>{ent_html}</section>
<section id="rel"><h2>Relationships</h2><table><tr><th>Parent → Child</th><th>Key</th><th>Type</th><th>Source</th></tr>{rel_rows}</table></section>
<section id="find"><h2>Findings &amp; notes</h2><ul>{findings}</ul></section>
<footer>Generated by Project Insight · static analysis, no AI</footer>
</main>
<script>
mermaid.initialize({{startOnLoad:true,theme:'dark',securityLevel:'loose',themeVariables:{{primaryColor:'#282834',primaryTextColor:'#e8e8f0',lineColor:'#a98bff',fontSize:'13px'}}}});
var nodes=new vis.DataSet({nodes_js});var edges=new vis.DataSet({edges_js});
new vis.Network(document.getElementById('graph'),{{nodes:nodes,edges:edges}},{{nodes:{{font:{{color:'#fff',size:14}},borderWidth:0,margin:12,shapeProperties:{{borderRadius:8}}}},edges:{{arrows:'to',smooth:{{type:'dynamic'}},font:{{size:12,background:'#101015',color:'#c9c9d6'}}}},physics:{{barnesHut:{{springLength:170,gravitationalConstant:-9000}},stabilization:{{iterations:200}}}},interaction:{{hover:true}}}});
</script></body></html>"""
