"""Shared V4.0 no-false-green guard helpers."""

from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path


SAFE_FORBIDDEN_CLAIM_CONTEXT_MARKERS = {
    "不能声明",
    "不能产出",
    "禁止",
    "禁止完成声明",
    "Forbidden",
    "forbidden",
    "blocks",
    "被误写",
    "误声明",
    "No False Green",
    "Non-Goals",
    "does not prove",
    "它不证明",
    "does not implement",
    "does not support",
    "does not provide",
    "cannot claim",
    "不是",
    "没有",
    "不代表",
    "不做",
    "不实现",
    "不证明",
    "仍不",
    "不等于",
    "不得声明",
    "不能升级为",
    "过度声明",
    "另行立项",
    "remain false",
    "false",
}

SAFE_FORBIDDEN_COPY_CONTEXT_MARKERS = {
    "禁止",
    "FORBIDDEN",
    "forbidden",
    "claim guard",
    "被误写",
    "误导文案",
    "误声明",
    "No False Green",
    "No forbidden copy",
    "must not show",
    "不得",
    "不显示",
    "不暴露",
    "不出现",
    "不要出现",
    "误导性",
    "不证明",
    "no UI copy says",
    "blocks",
}

API_ROUTE_DECORATOR = re.compile(r"@\w+\.(?:get|post|put|patch|delete)\(([^)]*)\)")


def v4_0_doc_and_frontend_files() -> list[Path]:
    docs = list(Path("docs/design/V4.0").glob("*.md"))
    frontend = [
        path
        for path in Path("apps/workflow-console/src").rglob("*.*")
        if "__tests__" not in path.parts and path.suffix in {".ts", ".tsx"}
    ]
    return [*docs, *frontend]


def assert_phrases_only_in_safe_context(
    *,
    files: Iterable[Path],
    phrases: Iterable[str],
    safe_markers: Iterable[str],
    window_before: int = 520,
    window_after: int = 180,
) -> None:
    marker_set = set(safe_markers)
    for path in files:
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            start = 0
            while True:
                index = text.find(phrase, start)
                if index == -1:
                    break
                context = _safe_context_for_occurrence(
                    text=text,
                    index=index,
                    phrase_length=len(phrase),
                    window_before=window_before,
                    window_after=window_after,
                )
                assert any(marker in context for marker in marker_set), (
                    f"{phrase!r} appears outside explicit forbidden/non-goal context in "
                    f"{path.as_posix()}:{text.count(chr(10), 0, index) + 1}"
                )
                start = index + len(phrase)


def _safe_context_for_occurrence(
    *,
    text: str,
    index: int,
    phrase_length: int,
    window_before: int,
    window_after: int,
) -> str:
    line_start = text.rfind("\n", 0, index) + 1
    line_end = text.find("\n", index)
    if line_end == -1:
        line_end = len(text)

    block_start = max(0, text.rfind("\n\n", 0, index) + 2)
    block_end = text.find("\n\n", index)
    if block_end == -1:
        block_end = len(text)

    bounded_start = max(block_start, index - window_before)
    bounded_end = min(block_end, index + phrase_length + window_after)
    preamble = _markdown_block_preamble(text, block_start, index)
    return "\n".join(
        (
            text[line_start:line_end],
            preamble,
            text[bounded_start:bounded_end],
        )
    )


def _markdown_block_preamble(text: str, block_start: int, index: int) -> str:
    block_prefix = text[block_start:index].lstrip()
    for line in reversed(text[:block_start].splitlines()):
        stripped = line.strip()
        if stripped and (
            block_prefix.startswith("```")
            or stripped.startswith("#")
            or stripped.endswith((":", "："))
        ):
            return stripped
    return ""


def api_source_files() -> list[Path]:
    return [
        path
        for path in Path("apps/api").rglob("*.py")
        if "__pycache__" not in path.parts
    ]


def workflow_console_source_files() -> list[Path]:
    return [
        path
        for path in Path("apps/workflow-console/src").rglob("*.*")
        if "__tests__" not in path.parts and path.suffix in {".ts", ".tsx"}
    ]


def _fragment_pattern(fragment: str) -> re.Pattern[str]:
    # Match forbidden path segments without treating allowed plural neighbors
    # such as /runs as a forbidden /run route.
    return re.compile(rf"(?<![A-Za-z0-9_]){re.escape(fragment)}(?=$|[\"'`/?#&])")


def assert_no_forbidden_route_fragments(fragments: Iterable[str]) -> None:
    compiled = {fragment: _fragment_pattern(fragment.rstrip("*")) for fragment in fragments}
    for path in api_source_files():
        text = path.read_text(encoding="utf-8")
        route_literals = "\n".join(API_ROUTE_DECORATOR.findall(text))
        for fragment, pattern in compiled.items():
            assert not pattern.search(route_literals), (
                f"Forbidden API route fragment {fragment!r} appears in route decorator {path.as_posix()}"
            )
            assert not pattern.search(text), (
                f"Forbidden API route fragment {fragment!r} appears in {path.as_posix()}"
            )
    for path in workflow_console_source_files():
        text = path.read_text(encoding="utf-8")
        for fragment, pattern in compiled.items():
            assert not pattern.search(text), (
                f"Forbidden frontend route fragment {fragment!r} appears in {path.as_posix()}"
            )
