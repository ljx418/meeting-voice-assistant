"""HTML renderer for the V2.18 Platform Console."""

from __future__ import annotations

import html
from typing import Any


def render_platform_console_html(payload: dict[str, Any]) -> str:
    title = "Project Intelligence Console"
    panels = payload.get("panels", [])
    cards = "\n".join(_panel_card(panel) for panel in panels)
    next_actions = "\n".join(
        f"<li><code>{html.escape(str(action))}</code></li>"
        for action in payload.get("next_actions", [])
    )
    warnings = "\n".join(
        f"<li>{html.escape(str(warning))}</li>"
        for warning in payload.get("warnings", [])
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <style>
    :root {{ color-scheme: light; --bg:#f7f8fa; --ink:#172033; --muted:#5c667a; --line:#d9dee8; --ok:#146c43; --warn:#9a6700; --bad:#b42318; --card:#fff; }}
    body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif; color:var(--ink); background:var(--bg); }}
    header {{ padding:28px 32px 18px; background:#172033; color:#fff; }}
    header p {{ margin:8px 0 0; color:#d6dce8; max-width:960px; }}
    main {{ padding:24px 32px 40px; max-width:1280px; margin:0 auto; }}
    .summary {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; margin-bottom:18px; }}
    .metric,.panel {{ background:var(--card); border:1px solid var(--line); border-radius:8px; padding:14px; }}
    .metric b {{ display:block; font-size:24px; margin-bottom:4px; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:14px; }}
    .panel h2 {{ margin:0 0 8px; font-size:18px; }}
    .status {{ display:inline-block; border-radius:999px; padding:2px 8px; font-size:12px; border:1px solid var(--line); }}
    .ready {{ color:var(--ok); }} .needs_build,.partial {{ color:var(--warn); }} .blocked,.missing {{ color:var(--bad); }}
    ul {{ margin:8px 0 0; padding-left:20px; }} li {{ margin:4px 0; }}
    code {{ background:#eef1f6; border-radius:4px; padding:1px 4px; }}
    .section {{ margin-top:18px; background:#fff; border:1px solid var(--line); border-radius:8px; padding:14px; }}
  </style>
</head>
<body>
  <header>
    <h1>{title}</h1>
    <p>面向人类和 Agent 的统一产品控制台：只汇总已落盘的项目智能资产，缺失能力会明确标记为待构建或阻塞，不伪造就绪状态。</p>
  </header>
  <main>
    {_summary(payload)}
    <div class="grid">{cards}</div>
    <section class="section"><h2>下一步动作</h2><ul>{next_actions or "<li>当前没有推荐动作。</li>"}</ul></section>
    <section class="section"><h2>风险与待确认</h2><ul>{warnings or "<li>未发现额外风险。</li>"}</ul></section>
  </main>
</body>
</html>"""


def _summary(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    items = [
        ("就绪面板", summary.get("ready_panel_count", 0)),
        ("待构建面板", summary.get("needs_build_panel_count", 0)),
        ("阻塞面板", summary.get("blocked_panel_count", 0)),
        ("资产引用", len(payload.get("artifact_refs", []))),
    ]
    cards = "".join(
        f"<div class=\"metric\"><b>{html.escape(str(value))}</b><span>{html.escape(label)}</span></div>"
        for label, value in items
    )
    return f"<section class=\"summary\">{cards}</section>"


def _panel_card(panel: dict[str, Any]) -> str:
    status = html.escape(str(panel.get("status", "unknown")))
    title = html.escape(str(panel.get("title") or panel.get("panel_id") or "Panel"))
    description = html.escape(str(panel.get("description") or ""))
    metrics = panel.get("metrics") or {}
    metric_items = "".join(
        f"<li>{html.escape(str(key))}: <b>{html.escape(str(value))}</b></li>"
        for key, value in metrics.items()
    )
    evidence = "".join(
        f"<li><code>{html.escape(str(ref.get('artifact_ref') or ref))}</code></li>"
        for ref in panel.get("artifact_refs", [])
    )
    blockers = "".join(
        f"<li>{html.escape(str(item.get('reason') or item))}</li>"
        for item in panel.get("needs_review", [])
    )
    return f"""<article class="panel">
  <h2>{title} <span class="status {status}">{status}</span></h2>
  <p>{description}</p>
  <h3>指标</h3><ul>{metric_items or "<li>暂无指标</li>"}</ul>
  <h3>资产</h3><ul>{evidence or "<li>未找到已落盘资产</li>"}</ul>
  <h3>待处理</h3><ul>{blockers or "<li>无</li>"}</ul>
</article>"""
