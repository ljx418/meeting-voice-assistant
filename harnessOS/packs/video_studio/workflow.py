"""Video studio domain workflow implementation."""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any


class VideoStudioWorkflow:
    """MVP video studio workflow that creates planning and render-lineage artifacts."""

    workflow_id = "video.workflow"
    domain = "video_studio"
    priority = 40

    def should_handle(self, user_input: str, context: Any) -> bool:
        if context.domain == "video_studio":
            return True
        if context.domain and context.domain != "video_studio":
            return False
        lowered = user_input.lower()
        return any(
            keyword in lowered
            for keyword in ("video", "视频", "短剧", "分镜", "脚本", "storyboard", "shot list", "镜头")
        )

    async def run(self, user_input: str, context: Any) -> dict[str, Any]:
        artifact_registry = context.artifact_registry
        if artifact_registry is None:
            raise RuntimeError("Video studio workflow requires an artifact registry")
        brief = _build_video_brief(user_input)
        script = _build_video_script(brief)
        storyboard = _build_video_storyboard(brief)
        shot_list = _build_video_shot_list(brief)
        asset_plan = _build_video_asset_plan(shot_list)
        render_output = _build_video_render_output_manifest(brief, asset_plan)
        output_dir = (
            artifact_registry.root
            / "video_studio"
            / (context.session_id or "session_unknown")
            / (context.turn_id or "turn_unknown")
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        artifacts_to_write = {
            "brief": ("brief.md", _render_brief_markdown(brief)),
            "script": ("script.md", _render_script_markdown(script)),
            "storyboard": ("storyboard.md", _render_storyboard_markdown(storyboard)),
            "shot_list": ("shot_list.json", json.dumps(shot_list, ensure_ascii=False, indent=2) + "\n"),
            "asset_plan": ("asset_plan.json", json.dumps(asset_plan, ensure_ascii=False, indent=2) + "\n"),
            "render_output": ("render_output.json", json.dumps(render_output, ensure_ascii=False, indent=2) + "\n"),
        }
        artifact_records: dict[str, dict[str, Any]] = {}
        previous_artifact_id: str | None = None
        for kind, (filename, content) in artifacts_to_write.items():
            path = output_dir / filename
            path.write_text(content, encoding="utf-8")
            record = artifact_registry.register_file(
                str(path),
                session_id=context.session_id,
                turn_id=context.turn_id,
                domain=self.domain,
                kind=kind,
                metadata={
                    "workflow_id": self.workflow_id,
                    "source_artifact_id": previous_artifact_id,
                    "lineage_step": kind,
                },
            )
            artifact_records[kind] = record
            previous_artifact_id = record["artifact_id"]
        content = (
            "视频工作流规划已完成。\n"
            f"主题：{brief['title']}\n"
            f"产物：brief/script/storyboard/shot_list/asset_plan/render_output\n"
            f"镜头数量：{len(shot_list['shots'])}"
        )
        return {
            "status": "success",
            "content": content,
            "video_studio": {
                "brief": brief,
                "script": script,
                "storyboard": storyboard,
                "shot_list": shot_list,
                "asset_plan": asset_plan,
                "render_output": render_output,
            },
            "artifact_records": artifact_records,
        }


def _build_video_brief(user_input: str) -> dict[str, Any]:
    title = _extract_video_title(user_input)
    return {
        "title": title,
        "objective": "将用户创意转化为可继续制作的短视频生产计划。",
        "audience": "泛内容平台观众",
        "tone": "清晰、有节奏、便于后续分镜制作",
        "source_prompt": user_input.strip(),
        "created_at": datetime.now().isoformat(),
    }


def _build_video_script(brief: dict[str, Any]) -> dict[str, Any]:
    title = brief["title"]
    return {
        "title": title,
        "scenes": [
            {
                "scene": 1,
                "heading": "开场钩子",
                "voiceover": f"如果用一分钟讲清楚{title}，第一秒必须抓住注意力。",
                "visual": "快速展示主题相关的核心画面，建立问题。",
            },
            {
                "scene": 2,
                "heading": "核心展开",
                "voiceover": f"围绕{title}给出三个递进信息点，让观众快速理解价值。",
                "visual": "用连续镜头展示过程、对比和关键细节。",
            },
            {
                "scene": 3,
                "heading": "结尾行动",
                "voiceover": "最后给出明确结论，并留下下一步行动。",
                "visual": "收束到结果画面和简洁字幕。",
            },
        ],
    }


def _build_video_storyboard(brief: dict[str, Any]) -> list[dict[str, Any]]:
    title = brief["title"]
    return [
        {"panel": 1, "duration_seconds": 5, "frame": "近景开场", "description": f"用视觉问题引出{title}。"},
        {"panel": 2, "duration_seconds": 10, "frame": "中景解释", "description": "展示主要信息点和上下文。"},
        {"panel": 3, "duration_seconds": 10, "frame": "细节特写", "description": "强调关键证据、动作或转折。"},
        {"panel": 4, "duration_seconds": 5, "frame": "结果收束", "description": "输出结论和行动提示。"},
    ]


def _build_video_shot_list(brief: dict[str, Any]) -> dict[str, Any]:
    storyboard = _build_video_storyboard(brief)
    return {
        "title": brief["title"],
        "shots": [
            {
                "shot_id": f"shot_{panel['panel']:02d}",
                "duration_seconds": panel["duration_seconds"],
                "camera": panel["frame"],
                "description": panel["description"],
                "asset_requirements": ["background", "caption", "voiceover"],
            }
            for panel in storyboard
        ],
    }


def _build_video_asset_plan(shot_list: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": shot_list["title"],
        "connector_ref": "remote_comfyui",
        "status": "planned",
        "assets": [
            {
                "asset_id": f"asset_{shot['shot_id']}",
                "shot_id": shot["shot_id"],
                "asset_type": "generated_video_clip",
                "prompt": shot["description"],
                "requirements": shot["asset_requirements"],
            }
            for shot in shot_list["shots"]
        ],
    }


def _build_video_render_output_manifest(brief: dict[str, Any], asset_plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": brief["title"],
        "connector_ref": "remote_comfyui",
        "status": "planned_not_rendered",
        "reason": "Remote render execution is deferred to the ComfyUI connector runtime.",
        "expected_outputs": [
            {
                "output_id": f"render_{asset['asset_id']}",
                "asset_id": asset["asset_id"],
                "kind": "video_clip",
                "status": "pending_remote_render",
            }
            for asset in asset_plan["assets"]
        ],
    }


def _render_brief_markdown(brief: dict[str, Any]) -> str:
    return (
        f"# {brief['title']} Brief\n\n"
        f"- Objective: {brief['objective']}\n"
        f"- Audience: {brief['audience']}\n"
        f"- Tone: {brief['tone']}\n\n"
        f"## Source Prompt\n\n{brief['source_prompt']}\n"
    )


def _render_script_markdown(script: dict[str, Any]) -> str:
    lines = [f"# {script['title']} Script", ""]
    for scene in script["scenes"]:
        lines.extend(
            [
                f"## Scene {scene['scene']}: {scene['heading']}",
                "",
                f"Voiceover: {scene['voiceover']}",
                "",
                f"Visual: {scene['visual']}",
                "",
            ]
        )
    return "\n".join(lines)


def _render_storyboard_markdown(storyboard: list[dict[str, Any]]) -> str:
    lines = ["# Storyboard", ""]
    for panel in storyboard:
        lines.extend(
            [
                f"## Panel {panel['panel']} ({panel['duration_seconds']}s)",
                "",
                f"- Frame: {panel['frame']}",
                f"- Description: {panel['description']}",
                "",
            ]
        )
    return "\n".join(lines)


def _extract_video_title(user_input: str) -> str:
    text = user_input.strip()
    for marker in ("主题", "title", "标题"):
        match = re.search(rf"{marker}[:：]\s*([^，。;\n]+)", text, flags=re.IGNORECASE)
        if match:
            return _clean_video_title(match.group(1))
    compact = re.sub(r"\s+", " ", text)
    return _clean_video_title(compact[:40]) or "Untitled Video"


def _clean_video_title(value: str) -> str:
    title = re.split(r"\s+(?:生成|制作|输出|创建|produce|create)", value.strip(), maxsplit=1, flags=re.IGNORECASE)[0]
    return title.strip(" ，。;；") or value.strip(" ，。;；")
