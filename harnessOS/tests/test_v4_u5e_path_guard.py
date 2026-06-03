import pytest

from core.workflows.v4_u5e_local_document_workflow import V4U5EWorkflowError, resolve_allowed_folder


@pytest.mark.parametrize("path", ["/", "~", ".", "..", "../技术分享", "Desktop/../secret"])
def test_path_guard_rejects_root_disk_and_parent_escape(path):
    with pytest.raises(V4U5EWorkflowError) as exc:
        resolve_allowed_folder(path)

    assert exc.value.code == "PATH_FORBIDDEN"


def test_path_guard_rejects_unapproved_folder():
    with pytest.raises(V4U5EWorkflowError) as exc:
        resolve_allowed_folder("Desktop")

    assert exc.value.code == "PATH_FORBIDDEN"


def test_path_guard_allows_desktop_tech_share_or_fixture():
    resolved, fixture_source = resolve_allowed_folder("tests/fixtures/desktop/技术分享")

    assert resolved.exists()
    assert fixture_source is True
