"""V4.0-D quality panel read-only tests."""

from __future__ import annotations

from pathlib import Path

APP_ROOT = Path("apps/workflow-console")


def test_quality_panel_source_does_not_call_quality_write_routes() -> None:
    source = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in (APP_ROOT / "src").rglob("*.ts*")
        if "__tests__" not in path.parts
    )
    assert "quality.evaluation.create" not in source
    assert "quality.evaluation.attach" not in source
    assert "/quality/create" not in source
    assert "/quality/attach" not in source


from tests.test_v4_0_operation_panels_bff_routes import test_operation_panel_bff_routes_return_redacted_dtos  # noqa: E402,F401
