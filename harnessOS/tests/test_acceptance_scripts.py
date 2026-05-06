from __future__ import annotations

from pathlib import Path


def test_meeting_lineage_acceptance_script_exists_and_targets_meeting_only():
    script = Path("scripts/e2e_meeting_validation.sh")

    assert script.exists()
    assert script.stat().st_mode & 0o111

    content = script.read_text(encoding="utf-8")
    assert "artifact.lineage" in content
    assert '"domain": "meeting"' in content
    assert "EXPECTED_KINDS = [\"transcript\", \"analysis\", \"result\", \"minutes\"]" in content
    assert "ComfyUI" not in content
    assert "remote_comfyui" not in content
