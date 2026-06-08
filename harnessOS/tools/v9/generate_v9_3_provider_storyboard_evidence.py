from __future__ import annotations

import base64
import hashlib
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from uuid import uuid4

from core.workflows.v9_3_multi_agent_orchestration_runtime import (
    V93OrchestrationConfig,
    run_v9_3_multi_agent_orchestration,
)
from tools.v9.common import V9_ROOT, utc_now, write_json


OUT_DIR = V9_ROOT / "evidence" / "v9-3-orchestration-runtime"
IMAGE_DIR = OUT_DIR / "storyboard-images"
PROVIDER_EVIDENCE = OUT_DIR / "storyboard-provider-evidence.json"
SUMMARY_PATH = V9_ROOT / "v9_3_runtime_acceptance_closure.md"


def main() -> int:
    provider = _load_provider_config()
    if not provider["api_key"]:
        evidence = _blocked_evidence(f"{provider['provider']}_key_missing")
        write_json(PROVIDER_EVIDENCE, evidence)
        print(json.dumps({"status": "BLOCKED", "reason": evidence["blocked_reason"], "output": str(PROVIDER_EVIDENCE)}, ensure_ascii=False, indent=2))
        return 1

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    prompt_refs = [f"artifact-ref://v9-3/video/storyboard-prompt-{index}" for index in range(1, 5)]
    invocation_id = f"provider-invocation-v9-3-{uuid4().hex[:12]}"
    images: list[bytes] = []
    response_shapes: list[dict[str, Any]] = []
    for index in range(1, 5):
        request = _build_provider_request(provider, index)
        response = _call_provider(provider, request)
        response_shapes.append(_response_shape(response))
        images.extend(_extract_image_payloads(response)[:1])
    if len(images) < 4:
        evidence = _blocked_evidence(_blocked_reason_from_shapes(response_shapes))
        evidence["provider_invocation_ref"] = f"provider-invocation-ref://v9-3/video/{invocation_id}"
        evidence["response_shapes"] = response_shapes
        write_json(PROVIDER_EVIDENCE, evidence)
        print(json.dumps({"status": "BLOCKED", "reason": evidence["blocked_reason"], "output": str(PROVIDER_EVIDENCE)}, ensure_ascii=False, indent=2))
        return 1

    artifacts = []
    for index, image_bytes in enumerate(images[:4], start=1):
        image_path = IMAGE_DIR / f"storyboard-shot-{index}.{provider['image_extension']}"
        image_path.write_bytes(image_bytes)
        artifacts.append(
            {
                "artifact_ref": f"artifact-ref://v9-3/video/storyboard-image-{index}",
                "path": str(image_path.relative_to(V9_ROOT)),
                "sha256": hashlib.sha256(image_bytes).hexdigest(),
                "byte_size": len(image_bytes),
                "content_type": provider["content_type"],
                "prompt_ref": prompt_refs[index - 1],
            }
        )

    provider_evidence = {
        "schema_version": "v9_3.provider_storyboard_evidence.v1",
        "status": "PASS",
        "scenario_id": "US-V9-08",
        "evidence_scope": "real_provider_backed_runtime_fixture",
        "runtime_backed": True,
        "provider_ref": provider["provider_ref"],
        "provider_model_ref": f"provider-model-ref://{provider['provider']}/{provider['model']}",
        "provider_config_source": provider["provider_config_source"],
        "provider_invocation_ref": f"provider-invocation-ref://v9-3/video/{invocation_id}",
        "prompt_refs": prompt_refs,
        "storyboard_image_artifacts": artifacts,
        "prompt_material_stored": False,
        "provider_request_body_stored": False,
        "provider_response_body_stored": False,
        "credential_material_stored": False,
        "base64_stored": False,
        "created_at": utc_now(),
    }
    write_json(PROVIDER_EVIDENCE, provider_evidence)

    payload = run_v9_3_multi_agent_orchestration(
        V93OrchestrationConfig(
            evidence_dir=OUT_DIR,
            provider_image_generation_available=True,
            storyboard_image_artifact_refs=tuple(item["artifact_ref"] for item in artifacts),
            provider_model_ref=provider_evidence["provider_model_ref"],
            provider_invocation_ref=provider_evidence["provider_invocation_ref"],
        )
    )
    write_json(PROVIDER_EVIDENCE, provider_evidence)
    SUMMARY_PATH.write_text((OUT_DIR / "result-summary.md").read_text(encoding="utf-8"), encoding="utf-8")
    print(json.dumps({"status": payload["acceptance"]["status"], "output": str(OUT_DIR / "index.html"), "provider_evidence": str(PROVIDER_EVIDENCE)}, ensure_ascii=False, indent=2))
    return 0 if payload["acceptance"]["status"] == "PASS" else 1


def _load_provider_config() -> dict[str, str]:
    env = dict(os.environ)
    for file_name in (".env.local", ".env"):
        path = Path(file_name)
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line or line.lstrip().startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    requested = (env.get("V9_STORYBOARD_IMAGE_PROVIDER") or "").strip().lower()
    if not requested:
        requested = "openai" if (env.get("OPENAI_API_KEY") or "").strip() else "minimax"
    if requested in {"openai", "openai-compatible", "compatible"}:
        return {
            "provider": "openai-compatible",
            "api_key": (env.get("OPENAI_API_KEY") or "").strip(),
            "base_url": (env.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/"),
            "model": (env.get("OPENAI_IMAGE_MODEL") or "gpt-image-1").strip(),
            "provider_ref": "provider-ref://openai-compatible/image-generation",
            "provider_config_source": "dotenv://openai-compatible-image-provider",
            "content_type": "image/png",
            "image_extension": "png",
        }
    base = env.get("MINIMAX_IMAGE_BASE_URL") or env.get("MINIMAX_BASE_URL") or "https://api.minimax.io/v1"
    return {
        "provider": "minimax",
        "api_key": (env.get("MINIMAX_API_KEY") or "").strip(),
        "base_url": base.rstrip("/"),
        "model": (env.get("MINIMAX_IMAGE_MODEL") or "image-01").strip(),
        "provider_ref": "provider-ref://minimax/image-generation",
        "provider_config_source": "dotenv://minimax-image-provider",
        "content_type": "image/jpeg",
        "image_extension": "jpg",
    }


def _storyboard_prompt(index: int) -> str:
    scene = {
        1: "wide establishing shot of the small AI studio and multiple specialist agents at workstations",
        2: "debate scene where philosopher, engineer, historian, and ethicist agents discuss the brief",
        3: "coding workflow scene with diff proposal, sandboxed tests, and evidence review on screens",
        4: "human producer approval scene with final evidence chain and storyboard wall",
    }[index]
    return (
        f"Create storyboard shot {index} of 4 for a 60-second cinematic short video: {scene}. "
        "Use consistent visual style across all shots, no text overlays, clear shot composition, "
        "professional concept art, balanced lighting, and a modern AI workflow studio setting."
    )


def _build_provider_request(provider: dict[str, str], index: int) -> dict[str, Any]:
    if provider["provider"] == "openai-compatible":
        return {
            "model": provider["model"],
            "prompt": _storyboard_prompt(index),
            "n": 1,
            "size": "1024x1024",
        }
    return {
        "model": provider["model"],
        "prompt": _storyboard_prompt(index),
        "response_format": "base64",
        "n": 1,
        "prompt_optimizer": True,
    }


def _call_provider(provider: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
    if provider["provider"] == "openai-compatible":
        return _call_openai_compatible(provider["api_key"], provider["base_url"], payload)
    return _call_minimax(provider["api_key"], provider["base_url"], payload)


def _call_openai_compatible(api_key: str, base_url: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        f"{base_url}/images/generations",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")[:500]
        raise RuntimeError(f"OpenAI-compatible image generation failed with HTTP {exc.code}: {body}") from exc


def _call_minimax(api_key: str, base_url: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        f"{base_url}/image_generation",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")[:500]
        raise RuntimeError(f"MiniMax image generation failed with HTTP {exc.code}: {body}") from exc


def _extract_image_payloads(response: dict[str, Any]) -> list[bytes]:
    data = response.get("data")
    if isinstance(data, dict):
        value = data.get("image_base64")
        if isinstance(value, list):
            return [base64.b64decode(item) for item in value if isinstance(item, str) and item.strip()]
        if isinstance(value, str) and value.strip():
            return [base64.b64decode(value)]
        urls = _coerce_url_list(data.get("image_urls") or data.get("image_url") or data.get("url"))
        if urls:
            return [_download_image(url) for url in urls]
        images = data.get("images")
        if isinstance(images, list):
            return _extract_from_list(images)
    if isinstance(data, list):
        return _extract_from_list(data)
    return []


def _blocked_reason_from_shapes(shapes: list[dict[str, Any]]) -> str:
    if shapes and all(shape.get("base_resp_status_msg") == "credential_rejected" for shape in shapes):
        return "provider_credential_rejected"
    return "provider_returned_less_than_four_images"


def _extract_from_list(items: list[Any]) -> list[bytes]:
    images: list[bytes] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        value = item.get("image_base64") or item.get("b64_json")
        if isinstance(value, str) and value.strip():
            images.append(base64.b64decode(value))
            continue
        urls = _coerce_url_list(item.get("image_url") or item.get("url") or item.get("image_urls"))
        images.extend(_download_image(url) for url in urls)
    return images


def _coerce_url_list(value: Any) -> list[str]:
    if isinstance(value, str) and value.startswith(("http://", "https://")):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item.startswith(("http://", "https://"))]
    return []


def _download_image(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=120) as response:
        return response.read()


def _blocked_evidence(reason: str) -> dict[str, Any]:
    return {
        "schema_version": "v9_3.provider_storyboard_evidence.v1",
        "status": "BLOCKED",
        "scenario_id": "US-V9-08",
        "evidence_scope": "blocked_provider_unavailable",
        "runtime_backed": False,
        "blocked_reason": reason,
        "prompt_material_stored": False,
        "provider_request_body_stored": False,
        "provider_response_body_stored": False,
        "credential_material_stored": False,
        "base64_stored": False,
        "created_at": utc_now(),
    }


def _response_shape(response: dict[str, Any]) -> dict[str, Any]:
    data = response.get("data")
    shape: dict[str, Any] = {
        "top_level_keys": sorted(str(key) for key in response.keys()),
        "base_resp_status_code": None,
        "base_resp_status_msg": None,
    }
    base_resp = response.get("base_resp")
    if isinstance(base_resp, dict):
        shape["base_resp_status_code"] = base_resp.get("status_code")
        status_msg = str(base_resp.get("status_msg") or "")
        shape["base_resp_status_msg"] = "credential_rejected" if "key" in status_msg.lower() else status_msg[:80]
    if isinstance(data, dict):
        shape["data_keys"] = sorted(str(key) for key in data.keys())
        shape["data_types"] = {str(key): type(value).__name__ for key, value in data.items()}
    elif isinstance(data, list):
        shape["data_type"] = "list"
        shape["data_len"] = len(data)
        if data and isinstance(data[0], dict):
            shape["first_data_keys"] = sorted(str(key) for key in data[0].keys())
    else:
        shape["data_type"] = type(data).__name__
    return shape


if __name__ == "__main__":
    raise SystemExit(main())
