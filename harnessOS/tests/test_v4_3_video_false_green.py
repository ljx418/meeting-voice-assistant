"""V4.3 false-green and boundary tests."""

from __future__ import annotations

from pathlib import Path


FORBIDDEN_CLAIMS = [
    "complete Workflow Studio ready",
    "complete AgentTalkWindow ready",
    "Agent executor ready",
    "controlled executor ready",
    "autonomous workflow editing ready",
    "production-ready external app support",
    "full multi-Agent orchestration ready",
]

FORBIDDEN_COPY = ["自动应用", "自动发布", "Agent 已执行", "Agent 已发布"]

V43_PATHS = [
    Path("docs/design/V4.3"),
    Path("tests/test_v4_3_video_workflow_spec.py"),
    Path("tests/test_v4_3_video_runtime_runner.py"),
    Path("tests/test_v4_3_video_rerun_stale.py"),
    Path("tests/test_v4_3_video_evidence_package.py"),
    Path("scripts/v4_3_serial_video_evidence.py"),
    Path("apps/api/routers/bff_v43.py"),
    Path("core/workflows/v4_3_serial_video.py"),
]


def _iter_text() -> str:
    chunks: list[str] = []
    for path in V43_PATHS:
        if path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and child.suffix in {".md", ".json", ".txt", ".html", ".py", ".drawio", ".yaml"}:
                    chunks.append(child.read_text(encoding="utf-8"))
        elif path.exists():
            chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def test_v43_does_not_claim_forbidden_completion() -> None:
    text = _iter_text()
    for claim in FORBIDDEN_CLAIMS:
        unsafe_lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip() == claim or line.strip().startswith(f"Status: {claim}")
        ]
        assert unsafe_lines == []


def test_v43_does_not_use_forbidden_ui_copy() -> None:
    text = _iter_text()
    for copy in FORBIDDEN_COPY:
        unsafe_lines = [line.strip() for line in text.splitlines() if line.strip() == copy]
        assert unsafe_lines == []


def test_v43_boundaries_are_explicit() -> None:
    text = _iter_text()

    assert "dev/local" in text
    assert "deterministic" in text or "确定性" in text
    assert "Agent executor" in text
    assert "user_confirmed" in text
