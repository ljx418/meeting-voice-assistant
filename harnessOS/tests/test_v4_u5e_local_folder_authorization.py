import pytest

from core.workflows.v4_u5e_local_document_workflow import (
    V4U5EWorkflowError,
    authorize_local_folder,
)


def test_local_folder_authorization_requires_user_confirmation():
    with pytest.raises(V4U5EWorkflowError) as exc:
        authorize_local_folder("Desktop/技术分享", user_confirmed=False, source="mission_console")

    assert exc.value.code == "AUTH_REQUIRED"


def test_local_folder_authorization_accepts_fixture_alias():
    authorization = authorize_local_folder(
        "Desktop/技术分享",
        user_confirmed=True,
        source="mission_console",
    )

    assert authorization.user_confirmed is True
    assert authorization.source == "mission_console"
    assert authorization.resolved_path.exists()
    assert authorization.to_dict()["redaction_status"] == "redacted"
