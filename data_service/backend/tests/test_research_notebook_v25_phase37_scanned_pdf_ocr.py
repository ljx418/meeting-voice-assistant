import base64
import os
import subprocess
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.research_notebook.providers.ocr_tesseract import pdf_embedded_text_probe
from test_target_http_source_preview import _assert_no_internal_paths, _create_workspace


PROVIDER_ENV = [
    "OCR_PROVIDER",
    "OCR_API_KEY",
    "OCR_ENDPOINT",
    "OCR_SIMULATE_ERROR",
    "TTS_PROVIDER",
    "TTS_API_KEY",
    "TTS_ENDPOINT",
    "TTS_SIMULATE_ERROR",
    "PPTX_PROVIDER",
    "PPTX_SIMULATE_ERROR",
    "PPTX_EXPORTER_ENABLED",
]


def _setup_client(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    for name in PROVIDER_ENV:
        monkeypatch.delenv(name, raising=False)
    return TestClient(app)


def _image_only_scanned_pdf_fixture(tmp_path: Path, text: str) -> bytes:
    png_path = tmp_path / "phase37-scanned-source.png"
    jpg_path = tmp_path / "phase37-scanned-source.jpg"
    pdf_path = tmp_path / "phase37-scanned-source.pdf"
    subprocess.run(
        [
            "pango-view",
            "--no-display",
            "--font=Sans Bold 44",
            "--dpi=180",
            "--background=white",
            "--foreground=black",
            "--margin=60",
            "--output",
            str(png_path),
            "--text",
            text,
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    )
    subprocess.run(
        ["sips", "-s", "format", "jpeg", str(png_path), "--out", str(jpg_path)],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    )
    jpeg = jpg_path.read_bytes()
    width, height = _jpeg_size(jpeg)
    _write_image_pdf(pdf_path, jpeg=jpeg, width=width, height=height)
    probe = pdf_embedded_text_probe(pdf_path)
    assert probe["available"] is True
    assert probe["has_embedded_text"] is False
    assert probe["text_length"] == 0
    return pdf_path.read_bytes()


def _jpeg_size(jpeg: bytes) -> tuple[int, int]:
    index = 2
    while index < len(jpeg):
        if jpeg[index] != 0xFF:
            index += 1
            continue
        marker = jpeg[index + 1]
        index += 2
        if marker in {0xD8, 0xD9}:
            continue
        length = int.from_bytes(jpeg[index : index + 2], "big")
        if marker in {0xC0, 0xC1, 0xC2, 0xC3}:
            height = int.from_bytes(jpeg[index + 3 : index + 5], "big")
            width = int.from_bytes(jpeg[index + 5 : index + 7], "big")
            return width, height
        index += length
    raise AssertionError("JPEG dimensions were not found")


def _write_image_pdf(path: Path, *, jpeg: bytes, width: int, height: int) -> None:
    content = f"q {width} 0 0 {height} 0 0 cm /Im0 Do Q\n".encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width} {height}] /Resources << /XObject << /Im0 4 0 R >> >> /Contents 5 0 R >>".encode(
            "ascii"
        ),
        f"<< /Type /XObject /Subtype /Image /Width {width} /Height {height} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length {len(jpeg)} >>\nstream\n".encode(
            "ascii"
        )
        + jpeg
        + b"\nendstream",
        f"<< /Length {len(content)} >>\nstream\n".encode("ascii") + content + b"endstream",
    ]
    data = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, body in enumerate(objects, start=1):
        offsets.append(len(data))
        data.extend(f"{number} 0 obj\n".encode("ascii"))
        data.extend(body)
        data.extend(b"\nendobj\n")
    xref_offset = len(data)
    data.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    data.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        data.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    data.extend(f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii"))
    path.write_bytes(bytes(data))


def _import_pdf_source(client: TestClient, workspace_id: str, pdf_bytes: bytes) -> str:
    response = client.post(
        f"/api/workspaces/{workspace_id}/sources",
        json={
            "files": [
                {
                    "title": "Phase 37 scanned PDF",
                    "file_name": "phase37-scanned.pdf",
                    "content_base64": base64.b64encode(pdf_bytes).decode("ascii"),
                    "content_type": "application/pdf",
                    "source_type": "pdf",
                }
            ]
        },
    )
    assert response.status_code == 200
    payload = response.json()
    _assert_no_internal_paths(payload)
    return payload["data"]["sources"][0]["source_id"]


def test_phase37_real_scanned_pdf_ocr_e2e_persists_and_reads_back(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    monkeypatch.setenv("OCR_PROVIDER", "tesseract")
    workspace_id = _create_workspace(client, "RN V25 Phase37 Scanned PDF")
    pdf_bytes = _image_only_scanned_pdf_fixture(tmp_path, "PHASE THIRTY SEVEN SCANNED PDF OCR")
    source_id = _import_pdf_source(client, workspace_id, pdf_bytes)

    response = client.post(f"/api/workspaces/{workspace_id}/sources/{source_id}/ocr")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    artifact = payload["data"]["artifact"]
    assert artifact["artifact_type"] == "ocr"
    assert artifact["status"] == "ready"
    assert artifact["artifact_available"] is True
    assert artifact["pages"]
    first_block = artifact["pages"][0]["blocks"][0]
    recognized = first_block["text"].upper()
    assert "PHASE" in recognized
    assert "OCR" in recognized
    assert first_block["confidence"] > 0
    assert first_block["locator"]["page"] == 1
    assert first_block["evidence_refs"][0]["locator"].startswith(f"source://{source_id}#page=1&block=0")
    metadata = artifact["generation_metadata"]
    assert metadata["rasterizer"] == "pdftoppm"
    assert metadata["embedded_text_probe"]["available"] is True
    assert metadata["embedded_text_probe"]["has_embedded_text"] is False
    assert metadata["embedded_text_probe"]["text_length"] == 0
    assert metadata["evidence_ref_count"] >= 1
    _assert_no_internal_paths(payload)

    artifact_id = artifact["artifact_id"]
    readback = client.get(f"/api/workspaces/{workspace_id}/artifacts/{artifact_id}")
    assert readback.status_code == 200
    readback_artifact = readback.json()["data"]["artifact"]
    assert readback_artifact["artifact_id"] == artifact_id
    assert readback_artifact["generation_metadata"]["embedded_text_probe"]["has_embedded_text"] is False
    _assert_no_internal_paths(readback.json())

    status = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/ocr/status")
    assert status.status_code == 200
    assert status.json()["data"]["status"] == "ready"
    assert status.json()["data"]["artifact_id"] == artifact_id

    workspace_root = Path(os.environ["DATA_SERVICE_WORKSPACE_ROOT"]) / workspace_id
    stored = workspace_root / "research_notebook" / "artifacts" / f"{artifact_id}.json"
    assert stored.exists()
    stored_text = stored.read_text(encoding="utf-8")
    assert "PHASE" in stored_text.upper()
    assert "/Users/" not in str(readback.json())
