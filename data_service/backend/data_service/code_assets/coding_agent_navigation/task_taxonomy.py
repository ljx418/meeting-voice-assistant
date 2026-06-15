"""Deterministic task taxonomy for V2.31 navigation."""

from __future__ import annotations

import re


TASK_KEYWORDS: dict[str, set[str]] = {
    "mcp_tool": {"mcp", "tool", "工具", "registry", "dispatcher"},
    "api": {"api", "http", "route", "router", "endpoint", "接口"},
    "cli": {"cli", "command", "命令", "argparse"},
    "workflow": {"workflow", "dispatch", "orchestration", "工作流", "编排"},
    "provider": {"provider", "adapter", "health", "ocr", "tts", "供应商", "适配器"},
    "snapshot": {"snapshot", "codebase", "repo", "manifest", "fingerprint", "快照", "仓库"},
    "governance": {"quality", "governance", "feedback", "rule", "review", "治理", "质量", "规则"},
    "descriptor": {"descriptor", "registry", "agent", "station", "manifest", "描述", "注册"},
    "entrypoint": {"entrypoint", "main", "console", "tui", "launch", "入口", "控制台"},
    "bugfix": {"bug", "fix", "error", "修复", "报错", "失败"},
    "test": {"test", "pytest", "验收", "测试"},
    "docs": {"doc", "docs", "readme", "文档", "prd"},
    "architecture_review": {"architecture", "架构", "intent", "diagram", "drawio", "governance", "审计"},
}


def classify_task(task: str) -> tuple[str, list[str]]:
    terms = task_terms(task)
    scores: dict[str, int] = {}
    for task_type, keywords in TASK_KEYWORDS.items():
        scores[task_type] = sum(1 for term in terms if term in keywords)
    best_type, best_score = max(scores.items(), key=lambda item: (item[1], item[0]))
    if best_score <= 0:
        return "unknown", terms
    return best_type, terms


def task_terms(task: str) -> list[str]:
    raw = re.split(r"[^A-Za-z0-9_\u4e00-\u9fff]+", str(task or "").lower())
    terms = [item for item in raw if item]
    expanded = set(terms)
    for term in list(terms):
        if "_" in term:
            expanded.update(part for part in term.split("_") if part)
        if "-" in term:
            expanded.update(part for part in term.split("-") if part)
    return sorted(expanded)
