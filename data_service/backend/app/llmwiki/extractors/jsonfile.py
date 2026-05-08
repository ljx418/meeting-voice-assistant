"""JSON 文件抽取器"""
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import LLMWikiConfig
from ..models import NormalizedSection, SectionKind, generate_id
from .base import BaseExtractor, ExtractionResult
from . import register_extractor


@register_extractor
class JsonExtractor(BaseExtractor):
    """通用 JSON 文件抽取器"""

    VERSION = "1.0"

    @staticmethod
    def supports(file_path: str) -> bool:
        return Path(file_path).suffix.lower() == ".json"

    def extract(self, file_path: str) -> ExtractionResult:
        """抽取 JSON 文件内容"""
        try:
            path = Path(file_path)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            sections = self._parse_json(data, path.stem)
            return ExtractionResult(sections=sections, status="success")
        except json.JSONDecodeError as e:
            return ExtractionResult(sections=[], status="error", error=f"Invalid JSON: {e}")
        except Exception as e:
            return ExtractionResult(sections=[], status="error", error=str(e))

    def _parse_json(self, data: Any, key_hint: str = "root") -> List[NormalizedSection]:
        """递归解析 JSON 数据"""
        sections = []

        if isinstance(data, dict):
            sections.extend(self._parse_dict(data, key_hint))
        elif isinstance(data, list):
            sections.extend(self._parse_list(data, key_hint))

        return sections

    def _parse_dict(self, data: Dict, parent_key: str = "") -> List[NormalizedSection]:
        """解析字典类型的 JSON"""
        sections = []

        for key, value in data.items():
            key_str = str(key)

            if isinstance(value, str):
                # 叶子节点字符串
                sections.append(NormalizedSection(
                    section_id=generate_id(),
                    source_id="",
                    kind=SectionKind.PARAGRAPH.value,
                    title=key_str,
                    text=value,
                    locator={
                        "kind": "json_path",
                        "path": f"{parent_key}.{key_str}" if parent_key else key_str
                    },
                    order_index=len(sections)
                ))
            elif isinstance(value, (int, float, bool)):
                # 叶子节点原始类型
                sections.append(NormalizedSection(
                    section_id=generate_id(),
                    source_id="",
                    kind=SectionKind.PARAGRAPH.value,
                    title=key_str,
                    text=str(value),
                    locator={
                        "kind": "json_path",
                        "path": f"{parent_key}.{key_str}" if parent_key else key_str
                    },
                    order_index=len(sections)
                ))
            elif isinstance(value, dict):
                # 嵌套对象
                sections.extend(self._parse_dict(value, f"{parent_key}.{key_str}" if parent_key else key_str))
            elif isinstance(value, list):
                # 数组
                sections.extend(self._parse_list(value, f"{parent_key}.{key_str}" if parent_key else key_str))

        return sections

    def _parse_list(self, data: List, parent_key: str = "") -> List[NormalizedSection]:
        """解析数组类型的 JSON"""
        sections = []

        for i, item in enumerate(data):
            if isinstance(item, str):
                sections.append(NormalizedSection(
                    section_id=generate_id(),
                    source_id="",
                    kind=SectionKind.PARAGRAPH.value,
                    text=item,
                    locator={
                        "kind": "json_path",
                        "path": f"{parent_key}[{i}]"
                    },
                    order_index=len(sections)
                ))
            elif isinstance(item, dict):
                sections.extend(self._parse_dict(item, f"{parent_key}[{i}]"))
            else:
                sections.append(NormalizedSection(
                    section_id=generate_id(),
                    source_id="",
                    kind=SectionKind.PARAGRAPH.value,
                    text=str(item),
                    locator={
                        "kind": "json_path",
                        "path": f"{parent_key}[{i}]"
                    },
                    order_index=len(sections)
                ))

        return sections


@register_extractor
class ChatJsonExtractor(BaseExtractor):
    """聊天记录 JSON 抽取器"""

    VERSION = "1.0"

    # 支持的聊天记录格式
    CHAT_FORMATS = [
        {"type": "array", "role_key": "role", "content_key": "content"},
        {"type": "object", "messages_key": "messages"},
        {"type": "object", "mapping_key": "mapping"},
        {"type": "object", "conversation_key": "conversation"},
        {"type": "object", "items_key": "items"},
        {"type": "object", "turns_key": "turns"},
    ]

    @staticmethod
    def supports(file_path: str) -> bool:
        return Path(file_path).suffix.lower() == ".json"

    def extract(self, file_path: str) -> ExtractionResult:
        """抽取聊天记录 JSON"""
        try:
            path = Path(file_path)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            # 检测格式
            format_info = self._detect_format(data)
            if not format_info:
                # 回退到通用 JSON 抽取器
                return JsonExtractor().extract(file_path)

            # 提取 messages
            messages = self._extract_messages(data, format_info)
            sections = self._create_turn_sections(messages, path.stem)

            return ExtractionResult(sections=sections, status="success")
        except Exception as e:
            return ExtractionResult(sections=[], status="error", error=str(e))

    @classmethod
    def load_conversation_payload(cls, file_path: str) -> Optional[Dict[str, Any]]:
        """Load one chat-like JSON file into conversation metadata + messages."""
        path = Path(file_path)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        extractor = cls()
        format_info = extractor._detect_format(data)
        if not format_info:
            return None

        messages = extractor._extract_messages(data, format_info)
        if not messages:
            return None

        if isinstance(data, dict):
            conversation_id = str(data.get("id") or data.get("conversation_id") or path.stem)
            created_at = str(data.get("inserted_at") or data.get("created_at") or "")
            updated_at = str(data.get("updated_at") or "")
        else:
            conversation_id = path.stem
            created_at = ""
            updated_at = ""

        normalized_messages = []
        for message in messages:
            normalized_messages.append(
                {
                    "role": str(message.get("role") or "unknown").lower(),
                    "content": extractor._clean_turn_text(str(message.get("content") or "")),
                    "timestamp": message.get("timestamp"),
                }
            )
        normalized_messages = [message for message in normalized_messages if message["content"]]
        if not normalized_messages:
            return None
        raw_title = str(data.get("title") or "") if isinstance(data, dict) else ""
        title = cls._human_title(raw_title, normalized_messages, path.stem, conversation_id)

        return {
            "conversation_id": conversation_id,
            "title": title,
            "created_at": created_at or None,
            "updated_at": updated_at or None,
            "messages": normalized_messages,
            "origin": "json",
        }

    @classmethod
    def preprocess_json_for_ingest(cls, file_path: str, output_root: Optional[str] = None) -> List[str]:
        """Rewrite only unreadable chat JSON structures into readable docs."""
        path = Path(file_path)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        extractor = cls()
        if not extractor._needs_readable_rewrite(data):
            return [file_path]

        base_dir = Path(output_root).resolve() if output_root else (LLMWikiConfig.resolve_workspace_path(path.parent) / "intermediate")
        out_dir = base_dir / "llmwiki_docs" / path.stem
        out_dir.mkdir(parents=True, exist_ok=True)
        written: List[str] = []
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            conv_id = str(item.get("id") or generate_id())
            messages = extractor._extract_from_mapping(item.get("mapping", {}))
            title = cls._human_title(str(item.get("title") or ""), messages, path.stem, conv_id)
            safe_title = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", title).strip("_")[:80] or conv_id
            out_path = out_dir / f"{conv_id}_{safe_title}.md"
            markdown = extractor._conversation_to_markdown(
                conversation_id=conv_id,
                title=title,
                inserted_at=str(item.get("inserted_at", "")),
                updated_at=str(item.get("updated_at", "")),
                messages=messages,
            )
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(markdown)
            written.append(str(out_path))
        return written or [file_path]

    def _needs_readable_rewrite(self, data: Any) -> bool:
        """Return True only for machine-shaped chat exports that are hard to read directly."""
        if isinstance(data, list) and data and isinstance(data[0], dict):
            return "mapping" in data[0]
        if isinstance(data, dict):
            if "mapping" in data and isinstance(data["mapping"], dict):
                return True
            # Simple turns/messages/items JSON is already readable enough for direct extraction.
            for key in ("turns", "messages", "items"):
                value = data.get(key)
                if isinstance(value, list) and value:
                    return False
        return False

    def _detect_format(self, data: Any) -> Optional[dict]:
        """检测聊天记录格式"""
        if isinstance(data, list):
            if len(data) > 0 and isinstance(data[0], dict):
                if "role" in data[0] and "content" in data[0]:
                    return {"type": "array", "messages": data}
                if "mapping" in data[0] and isinstance(data[0]["mapping"], dict):
                    return {"type": "list", "messages": self._extract_from_conversation_list(data)}
        elif isinstance(data, dict):
            # 检查各种可能的格式
            if "messages" in data and isinstance(data["messages"], list):
                return {"type": "object", "messages": data["messages"]}
            if "mapping" in data and isinstance(data["mapping"], dict):
                return {"type": "object", "messages": self._extract_from_mapping(data["mapping"])}
            if "conversation" in data and isinstance(data["conversation"], dict):
                return {"type": "object", "messages": self._extract_from_conversation(data["conversation"])}
            if "items" in data and isinstance(data["items"], list):
                return {"type": "object", "messages": self._extract_from_items(data["items"])}
            if "turns" in data and isinstance(data["turns"], list):
                return {"type": "object", "messages": self._extract_from_turns(data["turns"])}

        return None

    def _extract_from_mapping(self, mapping: dict) -> list:
        """从 mapping 格式提取消息"""
        messages = []
        ordered_nodes = sorted(
            mapping.values(),
            key=lambda node: (self._message_timestamp(node), str(node.get("id", ""))) if isinstance(node, dict) else ("", ""),
        )
        for node in ordered_nodes:
            if isinstance(node, dict):
                message = node.get("message", {})
                if message and isinstance(message, dict):
                    role = self._normalize_role(message)
                    content = self._extract_message_content(message)
                    if content:
                        messages.append({"role": role, "content": content})
        return messages

    def _extract_from_conversation_list(self, conversations: list) -> list:
        """从会话数组中提取串联消息。"""
        messages = []
        for item in conversations:
            if not isinstance(item, dict):
                continue
            extracted = self._extract_from_mapping(item.get("mapping", {}))
            title = item.get("title")
            if title and extracted:
                extracted[0]["conversation_title"] = title
            messages.extend(extracted)
        return messages

    def _extract_from_conversation(self, conv: dict) -> list:
        """从 conversation 格式提取消息"""
        messages = []
        if isinstance(conv, dict):
            for key in ["messages", "turns", "items"]:
                if key in conv and isinstance(conv[key], list):
                    messages.extend(conv[key])
        return messages

    def _extract_from_items(self, items: list) -> list:
        """从 items 格式提取消息"""
        messages = []
        for item in items:
            if isinstance(item, dict):
                role = item.get("role", item.get("author", ""))
                content = item.get("content", item.get("text", ""))
                if isinstance(content, list):
                    content = "\n".join(str(part) for part in content if part)
                if content:
                    messages.append({"role": role, "content": content})
        return messages

    def _extract_from_turns(self, turns: list) -> list:
        """从 turns 格式提取消息"""
        messages = []
        for turn in turns:
            if isinstance(turn, dict):
                role = turn.get("role", turn.get("speaker", ""))
                content = turn.get("content", turn.get("text", ""))
                if isinstance(content, list):
                    content = "\n".join(str(part) for part in content if part)
                if content:
                    messages.append({"role": role, "content": content})
        return messages

    def _extract_messages(self, data: Any, format_info: dict) -> list:
        """提取消息列表"""
        return format_info.get("messages", [])

    def _normalize_role(self, message: dict) -> str:
        role = message.get("role", "")
        if isinstance(role, dict):
            role = role.get("type") or role.get("name") or ""
        if not role:
            fragments = message.get("fragments", [])
            if isinstance(fragments, list) and fragments:
                fragment_type = str(fragments[0].get("type", "")).upper()
                if fragment_type == "REQUEST":
                    return "user"
                if fragment_type == "RESPONSE":
                    return "assistant"
        role = str(role or "unknown").lower()
        return {"human": "user"}.get(role, role)

    def _extract_message_content(self, message: dict) -> str:
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
        if isinstance(content, list):
            parts = [str(part).strip() for part in content if str(part).strip()]
            if parts:
                return "\n".join(parts)
        fragments = message.get("fragments", [])
        if isinstance(fragments, list):
            parts = []
            for fragment in fragments:
                if not isinstance(fragment, dict):
                    continue
                text = str(fragment.get("content", "")).strip()
                if text:
                    parts.append(text)
            if parts:
                return "\n\n".join(parts)
        return ""

    def _message_timestamp(self, node: dict) -> str:
        message = node.get("message") if isinstance(node, dict) else {}
        if not isinstance(message, dict):
            return ""
        return str(message.get("inserted_at", ""))

    @staticmethod
    def _clean_turn_text(text: str) -> str:
        return re.sub(r"\n{3,}", "\n\n", text).strip()

    @classmethod
    def _human_title(cls, raw_title: str, messages: List[dict], fallback_stem: str, conversation_id: str) -> str:
        cleaned = cls._clean_title(raw_title)
        if cls._is_meaningful_title(cleaned):
            return cleaned
        for message in messages:
            if str(message.get("role", "")).lower() != "user":
                continue
            candidate = cls._title_from_text(str(message.get("content") or ""))
            if candidate:
                return candidate
        cleaned = cls._clean_title(fallback_stem)
        if cls._is_meaningful_title(cleaned):
            return cleaned
        return cls._clean_title(conversation_id) or "Untitled Conversation"

    @staticmethod
    def _clean_title(title: str) -> str:
        title = (title or "").strip()
        title = re.sub(r"^[0-9a-f]{8}-[0-9a-f-]{27}[_\-\s]*", "", title, flags=re.IGNORECASE)
        title = re.sub(r"^[0-9a-f]{8,64}[_\-\s]*", "", title, flags=re.IGNORECASE)
        title = re.sub(r"^(source|conversation)\s*[:：]\s*", "", title, flags=re.IGNORECASE)
        title = re.sub(r"\bconversation[_\-\s]*id\b", "", title, flags=re.IGNORECASE)
        title = re.sub(r"\bsource[_\-\s]*id\b", "", title, flags=re.IGNORECASE)
        title = re.sub(r"^tmp[_\-\s]+", "", title, flags=re.IGNORECASE)
        title = re.sub(r"[_]+", " ", title)
        title = re.sub(r"[_\-]+", " ", title)
        title = re.sub(r"\s+", " ", title).strip(" -_:.：")
        return title[:120]

    @classmethod
    def _is_meaningful_title(cls, title: str) -> bool:
        cleaned = cls._clean_title(title)
        if not cleaned:
            return False
        lowered = cleaned.lower()
        if lowered in {"untitled", "untitled source", "untitled conversation", "source", "conversation", "conversation id"}:
            return False
        if re.search(r"(?i)\bconversation\b", cleaned):
            return False
        if re.fullmatch(r"[0-9a-f]{8,}", lowered):
            return False
        return len(re.sub(r"\s+", "", cleaned)) >= 3

    @classmethod
    def _title_from_text(cls, text: str) -> str:
        text = cls._clean_turn_text(text)
        if not text:
            return ""
        first = next((line.strip() for line in text.splitlines() if line.strip()), "")
        first = re.sub(r"^\[(user|assistant|system|unknown)\]\s*:\s*", "", first, flags=re.IGNORECASE)
        first = re.sub(r"^(请帮我|帮我|请问|想知道|求问|我想|能否|可否|请)\s*", "", first)
        first = first.strip(" -_#*？?。.:：")
        if not first:
            return ""
        sentence = re.split(r"[。！？!?]\s*|\n", first, maxsplit=1)[0].strip()
        candidate = sentence or first
        candidate = re.sub(r"\s+", " ", candidate).strip()
        if len(candidate) > 80:
            candidate = candidate[:80].rstrip()
        return cls._clean_title(candidate)

    def _conversation_to_markdown(
        self,
        *,
        conversation_id: str,
        title: str,
        inserted_at: str,
        updated_at: str,
        messages: List[dict],
    ) -> str:
        body: List[str] = [
            f"# {title or conversation_id}",
            "",
        ]
        overview = self._conversation_overview(messages)
        body.extend(["", "## Question", "", overview["question"] or "N/A"])
        body.extend(["", "## Core Conclusion", "", overview["conclusion"] or "N/A"])
        if overview["steps"]:
            body.extend(["", "## Actionable Steps", ""])
            for idx, step in enumerate(overview["steps"], start=1):
                body.append(f"{idx}. {step}")
        if overview["keywords"]:
            body.extend(["", "## Key Topics", "", ", ".join(overview["keywords"])])
        if inserted_at or updated_at:
            body.extend(["", "## Source Context", ""])
            body.append(f"- Conversation ID: {conversation_id}")
            if inserted_at:
                body.append(f"- Created At: {inserted_at}")
            if updated_at:
                body.append(f"- Updated At: {updated_at}")
        body.extend(["", "## Conversation", ""])

        for idx, message in enumerate(messages, start=1):
            role = str(message.get("role", "unknown")).lower()
            role_title = {"user": "User", "assistant": "Assistant", "system": "System"}.get(role, role.title())
            content = self._clean_turn_text(message.get("content", ""))
            if not content:
                continue
            body.append(f"### Turn {idx} · {role_title}")
            body.append("")
            body.append(content)
            body.append("")

        return "\n".join(body).strip() + "\n"

    def _conversation_overview(self, messages: List[dict]) -> dict:
        user_messages = [self._clean_turn_text(m.get("content", "")) for m in messages if str(m.get("role", "")).lower() == "user"]
        assistant_messages = [self._clean_turn_text(m.get("content", "")) for m in messages if str(m.get("role", "")).lower() == "assistant"]
        question = user_messages[0] if user_messages else ""
        conclusion = self._extract_conclusion_from_messages(assistant_messages[:3])
        steps = self._extract_steps_from_text(assistant_messages[:3])
        keywords = self._extract_keywords_from_messages(messages)
        return {
            "question": question[:400],
            "conclusion": conclusion[:600],
            "steps": steps[:5],
            "keywords": keywords[:8],
        }

    def _extract_steps_from_text(self, texts: List[str]) -> List[str]:
        steps: List[str] = []
        for text in texts:
            for line in text.splitlines():
                stripped = line.strip()
                cleaned = self._clean_summary_line(stripped)
                if cleaned and self._looks_like_step(cleaned):
                    if cleaned not in steps:
                        steps.append(cleaned[:240])
        return steps

    def _extract_conclusion_from_messages(self, texts: List[str]) -> str:
        for text in texts:
            for segment in re.split(r"(?<=[。！？.!?])\s+|\n+", text):
                cleaned = self._clean_summary_line(segment)
                if not cleaned or self._looks_like_step(cleaned):
                    continue
                if "?" in cleaned or "？" in cleaned:
                    continue
                return cleaned
        return texts[0][:600] if texts else ""

    def _extract_keywords_from_messages(self, messages: List[dict]) -> List[str]:
        text = " ".join(self._clean_turn_text(m.get("content", "")) for m in messages[:8])
        tokens = re.findall(r"[A-Za-z][A-Za-z0-9._-]{2,}|[\u4e00-\u9fff]{2,12}", text)
        seen = []
        for token in tokens:
            lower = token.lower()
            if lower in {"assistant", "user", "request", "response", "步骤", "问题", "结论", "然后", "最后"}:
                continue
            if re.fullmatch(r"\d+", token):
                continue
            if token not in seen:
                seen.append(token)
        return seen[:8]

    def _create_turn_sections(self, messages: list, source_name: str) -> List[NormalizedSection]:
        """创建 turn sections"""
        sections = []
        conversation_title = None

        for i, msg in enumerate(messages):
            role = msg.get("role", "unknown")
            content = self._clean_turn_text(msg.get("content", ""))

            # 尝试从第一条消息提取标题
            if i == 0 and role == "user" and len(content) < 100:
                conversation_title = content[:50]
            if not conversation_title and msg.get("conversation_title"):
                conversation_title = str(msg["conversation_title"])[:80]

            # 跳过空内容
            if not content:
                continue

            sections.append(NormalizedSection(
                section_id=generate_id(),
                source_id="",
                kind=SectionKind.TURN.value,
                title=f"Turn {i + 1}",
                text=f"[{role}]: {content}",
                locator={
                    "kind": "turn",
                    "conversation_id": source_name,
                    "turn": i + 1,
                    "role": role
                },
                order_index=i,
                meta_json={"role": role, "source_title": conversation_title}
            ))

        return sections

    def _clean_summary_line(self, text: str) -> str:
        cleaned = re.sub(r"^(\d+\.|[-*]|#+\s*)\s*", "", text or "").strip()
        cleaned = re.sub(r"^\[(user|assistant|system|unknown)\]\s*:\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" -:")
        if re.search(r"(?i)\b(conversation id|created at|updated at|metadata)\b", cleaned):
            return ""
        return cleaned

    def _looks_like_step(self, text: str) -> bool:
        return bool(re.match(r"(?i)(step\s*\d+|先|然后|接着|最后|安装|配置|运行|执行|打开|设置|检查|确认|创建|启动|重启)", text or ""))
