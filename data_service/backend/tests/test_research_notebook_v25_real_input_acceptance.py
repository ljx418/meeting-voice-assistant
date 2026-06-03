import base64
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from test_target_http_source_preview import _assert_no_internal_paths, _create_workspace


REAL_RESEARCH_NOTEBOOK_DOC_ROOT = Path("/Users/Zhuanz/Desktop/workspace/research-notebook/docs/backend")
REAL_RESEARCH_NOTEBOOK_DOCS = [
    "V2_BACKEND_SERVICE_PRD.md",
    "V2_BACKEND_API_MATRIX.md",
    "V2_TARGET_ARCHITECTURE.md",
]


def test_v25_real_research_notebook_backend_docs_drive_artifact_e2e(tmp_path, monkeypatch):
    missing = [name for name in REAL_RESEARCH_NOTEBOOK_DOCS if not (REAL_RESEARCH_NOTEBOOK_DOC_ROOT / name).exists()]
    if missing:
        pytest.skip(f"real ResearchNotebook backend docs are not available: {missing}")

    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    for name in ["OCR_PROVIDER", "OCR_API_KEY", "OCR_ENDPOINT", "TTS_PROVIDER", "TTS_API_KEY", "TTS_ENDPOINT", "PPTX_PROVIDER"]:
        monkeypatch.delenv(name, raising=False)

    client = TestClient(app)
    workspace_id = _create_workspace(client, "RN V25 Real Docs Acceptance")
    files = []
    for name in REAL_RESEARCH_NOTEBOOK_DOCS:
        path = REAL_RESEARCH_NOTEBOOK_DOC_ROOT / name
        files.append(
            {
                "title": path.stem,
                "file_name": path.name,
                "content_base64": base64.b64encode(path.read_bytes()).decode("ascii"),
                "content_type": "text/markdown",
                "source_type": "markdown",
                "metadata": {
                    "source_type": "markdown",
                    "acceptance_fixture": "research_notebook_v2_backend_docs",
                    "real_input_file": path.name,
                },
            }
        )

    import_response = client.post(f"/api/workspaces/{workspace_id}/sources", json={"files": files})
    assert import_response.status_code == 200
    import_payload = import_response.json()
    source_ids = [source["source_id"] for source in import_payload["data"]["sources"]]
    assert len(source_ids) == len(REAL_RESEARCH_NOTEBOOK_DOCS)
    _assert_no_internal_paths(import_payload)

    slides_response = client.post(
        f"/api/workspaces/{workspace_id}/artifacts/slides",
        json={"source_ids": source_ids, "topic": "ResearchNotebook V2 Backend", "slide_count": 5},
    )
    assert slides_response.status_code == 200
    slides = slides_response.json()["data"]["artifact"]
    assert slides["artifact_available"] is True
    assert len(slides["slides"]) == 5
    assert all(slide["evidence_refs"] for slide in slides["slides"])
    assert any("ResearchNotebook V2.x" in ref["snippet"] for ref in slides["evidence_refs"])

    mindmap_response = client.post(
        f"/api/workspaces/{workspace_id}/artifacts/mindmap",
        json={"source_ids": source_ids, "topic": "ResearchNotebook V2 Backend"},
    )
    assert mindmap_response.status_code == 200
    mindmap = mindmap_response.json()["data"]["artifact"]
    assert mindmap["root_node"]["children"]
    assert mindmap["evidence_refs"]

    compare_response = client.post(f"/api/workspaces/{workspace_id}/artifacts/compare", json={"source_ids": source_ids})
    assert compare_response.status_code == 200
    compare = compare_response.json()["data"]["artifact"]
    assert compare["result"]["source_pairs"][0]["similarities"][0]["evidence_refs"]
    assert compare["result"]["source_pairs"][0]["differences"][0]["evidence_a"]
    assert compare["result"]["source_pairs"][0]["differences"][0]["evidence_b"]

    artifact_files = sorted(root.rglob("research_notebook/artifacts/*.json"))
    assert len(artifact_files) >= 3
    listing = client.get(f"/api/workspaces/{workspace_id}/artifacts")
    assert listing.status_code == 200
    assert listing.json()["data"]["count"] >= 3

    _assert_no_internal_paths(slides_response.json())
    _assert_no_internal_paths(mindmap_response.json())
    _assert_no_internal_paths(compare_response.json())
