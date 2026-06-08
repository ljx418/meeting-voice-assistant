from pathlib import Path


DOC_ROOT = Path("docs/V2.x")

PHASE_REPORTS = [
    DOC_ROOT / "V2_16_PHASE_76_ACCEPTANCE_AUDIT_REPORT.md",
    DOC_ROOT / "V2_16_PHASE_77_ACCEPTANCE_AUDIT_REPORT.md",
    DOC_ROOT / "V2_16_PHASE_78_ACCEPTANCE_AUDIT_REPORT.md",
    DOC_ROOT / "V2_16_PHASE_79_ACCEPTANCE_AUDIT_REPORT.md",
    DOC_ROOT / "V2_16_PHASE_80_ACCEPTANCE_AUDIT_REPORT.md",
    DOC_ROOT / "V2_16_PHASE_81_ACCEPTANCE_AUDIT_REPORT.md",
]

FOCUSED_TESTS = [
    Path("backend/tests/test_v2_16_provider_registry.py"),
    Path("backend/tests/test_v2_16_semantic_orchestrator.py"),
    Path("backend/tests/test_v2_16_runtime_profiles.py"),
    Path("backend/tests/test_v2_16_workbench_v2.py"),
    Path("backend/tests/test_v2_16_large_project_advisor.py"),
    Path("backend/tests/test_v2_16_patch_sandbox.py"),
]


def test_v216_phase_acceptance_reports_have_no_open_fatal_or_major_findings():
    for report in PHASE_REPORTS:
        assert report.exists(), report
        text = report.read_text(encoding="utf-8")
        assert "结论：Phase" in text
        assert "Fatal findings：0" in text
        assert "Major findings：0" in text


def test_v216_focused_test_files_exist():
    for path in FOCUSED_TESTS:
        assert path.exists(), path


def test_v216_coverage_matrix_has_no_phase_76_81_pending_rows():
    matrix = (DOC_ROOT / "V2_16_FULL_COVERAGE_MATRIX.md").read_text(encoding="utf-8")
    for phase in range(76, 82):
        phase_rows = [line for line in matrix.splitlines() if f"| {phase} |" in line]
        assert phase_rows, phase
        for row in phase_rows:
            assert "pending" not in row.lower(), row
            assert "accepted" in row or "out_of_scope" in row, row


def test_v216_non_goals_remain_out_of_scope():
    matrix = (DOC_ROOT / "V2_16_FULL_COVERAGE_MATRIX.md").read_text(encoding="utf-8")
    for marker in ["任意命令执行", "自主源码修改", "full call graph / data flow / type inference", "自主 git 操作"]:
        rows = [line for line in matrix.splitlines() if marker in line]
        assert rows, marker
        assert all("out_of_scope" in row for row in rows)
