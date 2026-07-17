"""
report_generator.py — HTML, JSON, and Markdown report generation for RCA Analyzer
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from config import REPORTS_DIR

if TYPE_CHECKING:
    from rca_engine import ProjectAnalysis


# ── Severity colour mapping ──────────────────────────────────────────────────────
SEVERITY_COLORS = {
    "Low": "#22c55e",
    "Medium": "#f59e0b",
    "High": "#f97316",
    "Critical": "#ef4444",
}

SEVERITY_BG = {
    "Low": "#f0fdf4",
    "Medium": "#fffbeb",
    "High": "#fff7ed",
    "Critical": "#fef2f2",
}


def _badge(text: str, color: str, bg: str) -> str:
    return (
        f'<span style="background:{bg};color:{color};border:1px solid {color};'
        f'border-radius:4px;padding:2px 8px;font-size:12px;font-weight:600;">'
        f"{text}</span>"
    )


def _sev_badge(severity: str) -> str:
    c = SEVERITY_COLORS.get(severity, "#6b7280")
    b = SEVERITY_BG.get(severity, "#f9fafb")
    return _badge(severity, c, b)


def _escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def generate_html_report(project: "ProjectAnalysis") -> str:
    """Generate a full standalone HTML report and save it to the reports folder."""
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    file_ts = now.strftime("%Y%m%d_%H%M%S")
    report_name = f"RCA_Report_{file_ts}.html"
    report_path = REPORTS_DIR / report_name

    # ── File result cards ────────────────────────────────────────────────────────
    cards_html = ""
    for r in project.file_results:
        if r.error:
            cards_html += f"""
            <div class="card error-card">
              <div class="card-header">
                <span class="file-name">📄 {_escape(r.file_path)}</span>
                <span class="lang-badge">{_escape(r.language)}</span>
                {_badge("ERROR", "#ef4444", "#fef2f2")}
              </div>
              <p style="color:#ef4444">{_escape(r.error)}</p>
            </div>"""
            continue

        causes_html = "".join(
            f'<li>🔴 {_escape(c)}</li>' for c in r.root_causes
        )
        recs_html = "".join(
            f'<li>✅ {_escape(rec)}</li>' for rec in r.recommendations
        )

        snippets_html = ""
        for s in r.code_snippets:
            line_info = f"Line {s.get('line')}" if s.get("line") else "Unknown line"
            snippets_html += f"""
            <div class="snippet-block">
              <div class="snippet-meta">
                <strong>{_escape(line_info)}</strong> — {_escape(s.get('issue', ''))}
              </div>
              <pre class="code-block">{_escape(s.get('snippet', ''))}</pre>
              <div class="fix-suggestion">💡 Fix: {_escape(s.get('fix', ''))}</div>
            </div>"""

        metrics = r.metrics or {}
        metrics_html = "".join(
            f'<div class="metric-item"><span class="metric-label">{_escape(k.replace("_", " ").title())}</span>'
            f'<span class="metric-value">{_escape(str(v))}</span></div>'
            for k, v in metrics.items()
        )

        cards_html += f"""
        <div class="card">
          <div class="card-header">
            <span class="file-name">📄 {_escape(r.file_path)}</span>
            <span class="lang-badge">{_escape(r.language)}</span>
            {_sev_badge(r.severity)}
            <span style="color:#6b7280;font-size:12px">Confidence: {_escape(r.confidence)}</span>
          </div>

          <p class="summary-text">{_escape(r.summary)}</p>

          <div class="two-col">
            <div>
              <h4>🔍 Root Causes</h4>
              <ul class="issue-list">{causes_html}</ul>
            </div>
            <div>
              <h4>💡 Recommendations</h4>
              <ul class="rec-list">{recs_html}</ul>
            </div>
          </div>

          {f'<div class="metrics-row">{metrics_html}</div>' if metrics_html else ""}
          {f'<div class="snippets-section"><h4>🔎 Code Snippets</h4>{snippets_html}</div>' if snippets_html else ""}
        </div>"""

    # ── Top issues ───────────────────────────────────────────────────────────────
    top_issues_html = "".join(
        f"<li>{_escape(i)}</li>" for i in project.top_issues
    )

    # ── Severity distribution ────────────────────────────────────────────────────
    sev_dist: dict = {}
    for r in project.file_results:
        sev_dist[r.severity] = sev_dist.get(r.severity, 0) + 1

    sev_bars = ""
    total_files = max(project.total_files, 1)
    for sev, count in sorted(sev_dist.items(), key=lambda x: ["Low", "Medium", "High", "Critical"].index(x[0]) if x[0] in ["Low", "Medium", "High", "Critical"] else 99):
        pct = round(count / total_files * 100)
        color = SEVERITY_COLORS.get(sev, "#6b7280")
        sev_bars += f"""
        <div class="sev-bar-row">
          <span class="sev-label">{sev}</span>
          <div class="sev-bar-bg">
            <div class="sev-bar-fill" style="width:{pct}%;background:{color}"></div>
          </div>
          <span class="sev-count">{count}</span>
        </div>"""

    overall_color = SEVERITY_COLORS.get(project.overall_severity, "#6b7280")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RCA Analyzer Report — {_escape(timestamp)}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system,"Segoe UI",system-ui,sans-serif; background:#0f172a; color:#e2e8f0; font-size:14px; line-height:1.6; }}
  a {{ color:#60a5fa; }}
  .page-wrap {{ max-width:1000px; margin:0 auto; padding:32px 16px; }}

  /* Header */
  .report-header {{ background:linear-gradient(135deg,#1e3a5f 0%,#1e1b4b 100%); border-radius:12px; padding:32px; margin-bottom:28px; border:1px solid #334155; }}
  .report-title {{ font-size:28px; font-weight:700; color:#f1f5f9; }}
  .report-subtitle {{ color:#94a3b8; margin-top:6px; font-size:14px; }}
  .header-meta {{ display:flex; gap:24px; margin-top:20px; flex-wrap:wrap; }}
  .meta-chip {{ background:#0f172a55; border:1px solid #334155; border-radius:6px; padding:8px 14px; }}
  .meta-chip .label {{ font-size:11px; color:#64748b; text-transform:uppercase; letter-spacing:.05em; }}
  .meta-chip .value {{ font-size:14px; font-weight:600; color:#e2e8f0; margin-top:2px; }}

  /* Summary panel */
  .summary-panel {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-bottom:28px; }}
  .panel {{ background:#1e293b; border:1px solid #334155; border-radius:10px; padding:20px; }}
  .panel h3 {{ font-size:13px; font-weight:600; color:#94a3b8; text-transform:uppercase; letter-spacing:.05em; margin-bottom:12px; }}
  .overall-sev {{ font-size:32px; font-weight:800; color:{overall_color}; }}
  .top-issues-list {{ list-style:none; }}
  .top-issues-list li {{ padding:4px 0; color:#cbd5e1; font-size:13px; border-bottom:1px solid #1e293b; }}
  .top-issues-list li::before {{ content:"⚠️ "; }}

  /* Severity bars */
  .sev-bar-row {{ display:flex; align-items:center; gap:12px; margin-bottom:8px; }}
  .sev-label {{ width:70px; font-size:12px; color:#94a3b8; }}
  .sev-bar-bg {{ flex:1; background:#0f172a; border-radius:4px; height:8px; overflow:hidden; }}
  .sev-bar-fill {{ height:100%; border-radius:4px; transition:width .4s; }}
  .sev-count {{ width:24px; font-size:12px; color:#64748b; text-align:right; }}

  /* Section */
  .section-title {{ font-size:18px; font-weight:700; color:#f1f5f9; margin-bottom:16px; margin-top:32px; padding-bottom:8px; border-bottom:1px solid #334155; }}

  /* File card */
  .card {{ background:#1e293b; border:1px solid #334155; border-radius:10px; padding:20px; margin-bottom:16px; }}
  .error-card {{ border-color:#7f1d1d; background:#1c0a0a; }}
  .card-header {{ display:flex; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:12px; }}
  .file-name {{ font-weight:600; color:#93c5fd; font-size:14px; }}
  .lang-badge {{ background:#1e3a5f; color:#60a5fa; border:1px solid #1d4ed8; border-radius:4px; padding:2px 8px; font-size:11px; font-weight:600; }}
  .summary-text {{ color:#94a3b8; font-size:13px; margin-bottom:14px; line-height:1.7; }}
  .two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-bottom:16px; }}
  .two-col h4 {{ font-size:13px; color:#e2e8f0; margin-bottom:8px; }}
  .issue-list, .rec-list {{ list-style:none; }}
  .issue-list li, .rec-list li {{ font-size:12px; color:#cbd5e1; padding:3px 0; border-bottom:1px dashed #1e3a5f; }}

  /* Metrics */
  .metrics-row {{ display:flex; flex-wrap:wrap; gap:10px; margin-bottom:14px; }}
  .metric-item {{ background:#0f172a; border:1px solid #334155; border-radius:6px; padding:8px 14px; }}
  .metric-label {{ font-size:11px; color:#64748b; display:block; }}
  .metric-value {{ font-size:13px; font-weight:600; color:#e2e8f0; }}

  /* Snippets */
  .snippets-section h4 {{ font-size:13px; color:#e2e8f0; margin-bottom:10px; }}
  .snippet-block {{ background:#0f172a; border-left:3px solid #3b82f6; border-radius:4px; padding:12px; margin-bottom:10px; }}
  .snippet-meta {{ font-size:12px; color:#94a3b8; margin-bottom:6px; }}
  .code-block {{ font-family:"Cascadia Code","Fira Code",monospace; font-size:12px; color:#86efac; overflow-x:auto; white-space:pre; }}
  .fix-suggestion {{ font-size:12px; color:#fbbf24; margin-top:8px; }}

  /* Footer */
  .footer {{ text-align:center; color:#475569; font-size:11px; margin-top:40px; padding-top:16px; border-top:1px solid #1e293b; }}

  @media(max-width:600px) {{
    .summary-panel, .two-col {{ grid-template-columns:1fr; }}
    .header-meta {{ flex-direction:column; }}
  }}
</style>
</head>
<body>
<div class="page-wrap">

  <!-- Header -->
  <div class="report-header">
    <div class="report-title">🔍 Root Cause Analysis Report</div>
    <div class="report-subtitle">{_escape(project.mode)}</div>
    <div class="header-meta">
      <div class="meta-chip">
        <div class="label">Generated</div>
        <div class="value">{_escape(timestamp)}</div>
      </div>
      <div class="meta-chip">
        <div class="label">AI Provider</div>
        <div class="value">{_escape(project.provider)} / {_escape(project.model)}</div>
      </div>
      <div class="meta-chip">
        <div class="label">Files Analysed</div>
        <div class="value">{project.analysed_files} / {project.total_files}</div>
      </div>
      <div class="meta-chip">
        <div class="label">Overall Severity</div>
        <div class="value" style="color:{overall_color}">{_escape(project.overall_severity)}</div>
      </div>
    </div>
  </div>

  <!-- Summary -->
  <div class="summary-panel">
    <div class="panel">
      <h3>Project Summary</h3>
      <div class="overall-sev">{_escape(project.overall_severity)}</div>
      <p style="color:#94a3b8;margin-top:10px;font-size:13px">{_escape(project.project_summary)}</p>
    </div>
    <div class="panel">
      <h3>Top Issues</h3>
      <ul class="top-issues-list">{top_issues_html}</ul>
    </div>
  </div>

  <!-- Severity distribution -->
  <div class="panel" style="margin-bottom:28px">
    <h3>Severity Distribution</h3>
    <div style="margin-top:12px">{sev_bars}</div>
  </div>

  <!-- Per-file results -->
  <div class="section-title">📁 Per-File Analysis</div>
  {cards_html}

  <div class="footer">Generated by RCA Analyzer · {_escape(timestamp)}</div>
</div>
</body>
</html>"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)

    return str(report_path)


def generate_json_report(project: "ProjectAnalysis") -> str:
    """Serialise the project analysis to a JSON file."""
    now = datetime.now()
    file_ts = now.strftime("%Y%m%d_%H%M%S")
    report_path = REPORTS_DIR / f"RCA_Report_{file_ts}.json"

    data = {
        "generated_at": now.isoformat(),
        "mode": project.mode,
        "provider": project.provider,
        "model": project.model,
        "overall_severity": project.overall_severity,
        "project_summary": project.project_summary,
        "top_issues": project.top_issues,
        "total_files": project.total_files,
        "analysed_files": project.analysed_files,
        "file_results": [
            {
                "path": r.file_path,
                "language": r.language,
                "severity": r.severity,
                "confidence": r.confidence,
                "summary": r.summary,
                "root_causes": r.root_causes,
                "recommendations": r.recommendations,
                "code_snippets": r.code_snippets,
                "metrics": r.metrics,
                "error": r.error,
            }
            for r in project.file_results
        ],
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return str(report_path)


def generate_markdown_report(project: "ProjectAnalysis") -> str:
    """Generate a Markdown report."""
    now = datetime.now()
    file_ts = now.strftime("%Y%m%d_%H%M%S")
    report_path = REPORTS_DIR / f"RCA_Report_{file_ts}.md"

    lines = [
        f"# 🔍 Root Cause Analysis Report\n",
        f"**Mode:** {project.mode}  ",
        f"**Generated:** {now.strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"**Provider:** {project.provider} / {project.model}  ",
        f"**Overall Severity:** {project.overall_severity}  ",
        f"**Files:** {project.analysed_files}/{project.total_files}\n",
        f"## Project Summary\n",
        f"{project.project_summary}\n",
    ]

    if project.top_issues:
        lines.append("## Top Issues\n")
        for issue in project.top_issues:
            lines.append(f"- ⚠️ {issue}")
        lines.append("")

    lines.append("## Per-File Results\n")
    for r in project.file_results:
        lines.append(f"### 📄 {r.file_path} `[{r.language}]` — **{r.severity}**\n")
        if r.error:
            lines.append(f"> ❌ Error: {r.error}\n")
            continue
        lines.append(f"{r.summary}\n")
        if r.root_causes:
            lines.append("**Root Causes:**")
            for c in r.root_causes:
                lines.append(f"- 🔴 {c}")
            lines.append("")
        if r.recommendations:
            lines.append("**Recommendations:**")
            for rec in r.recommendations:
                lines.append(f"- ✅ {rec}")
            lines.append("")

    content = "\n".join(lines)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)

    return str(report_path)


def generate_report(project: "ProjectAnalysis", fmt: str = "HTML") -> str:
    """Dispatch to the correct report generator based on format."""
    fmt = fmt.upper()
    if fmt == "HTML":
        return generate_html_report(project)
    elif fmt == "JSON":
        return generate_json_report(project)
    elif fmt in ("MARKDOWN", "MD"):
        return generate_markdown_report(project)
    else:
        return generate_html_report(project)
