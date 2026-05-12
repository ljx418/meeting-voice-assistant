"""LLMWiki 核心引擎"""
import hashlib
import json
import logging
import re
import shutil
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .compiler import WikiCompiler, classify, normalize_title
from .compiler.page_builder import build_conversation_note
from .config import LLMWikiConfig
from .extractors import get_extractor
from .extractors.jsonfile import ChatJsonExtractor
from .models import (
    Authority,
    Conversation,
    IngestRun,
    IngestStatus,
    Passage,
    SourceRecord,
    SourceType,
    Turn,
    generate_id,
)
from .normalize import normalize_sections
from .search.fts import FTS5Search
from .storage import Storage

logger = logging.getLogger(__name__)


class WikiEngine:
    """LLMWiki 核心引擎

    封装 4 个核心动作:
    - ingest: 导入文件或目录
    - search: 搜索 wiki
    - read_page: 读取页面
    - rebuild: 重建索引
    """

    def __init__(self, config: Optional[LLMWikiConfig] = None):
        """初始化 WikiEngine

        Args:
            config: LLMWiki 配置
        """
        self.config = config or LLMWikiConfig()
        self.config.ensure_directories()
        self.storage = Storage(self.config)
        self.storage.init_db()
        self.fts = FTS5Search(self.config.db_path)
        self.compiler = WikiCompiler(self.config)

    def ingest(self, paths: Union[List[str], str]) -> Dict[str, Any]:
        """导入文件或目录

        流程: 文件检测 -> 抽取器选择 -> extract() -> normalize() -> passage -> page build -> storage

        Args:
            paths: 文件路径或目录路径列表

        Returns:
            {
                success: int,    # 成功导入的文件数
                failed: int,      # 失败的文件数
                pages: list[str], # 创建的页面 slug 列表
                errors: list     # 错误信息列表
            }
        """
        if isinstance(paths, str):
            paths = [paths]

        run_started_at = datetime.utcnow()

        # 收集所有文件
        file_paths: List[Path] = []
        for p in paths:
            path = Path(p)
            if path.is_dir():
                for ext in self._supported_extensions():
                    file_paths.extend(path.rglob(f"*{ext}"))
                # 也扫描无扩展名的文本文件
                for fp in path.rglob("*"):
                    if fp.is_file() and "." not in fp.name:
                        file_paths.append(fp)
            elif path.is_file():
                if path.suffix.lower() == ".json":
                    expanded_paths = ChatJsonExtractor.preprocess_json_for_ingest(
                        str(path),
                        output_root=str(self.config.readable_docs_dir),
                    )
                    file_paths.extend(Path(expanded) for expanded in expanded_paths)
                else:
                    file_paths.append(path)

        # 去重
        file_paths = list(set(file_paths))

        success = 0
        failed = 0
        skipped = 0
        page_slugs: List[str] = []
        source_ids: List[str] = []
        errors: List[Dict[str, Any]] = []
        total_passages = 0

        for file_path in file_paths:
            try:
                ingest_result = self._ingest_single_file(file_path)
                if ingest_result:
                    page_slugs.extend(ingest_result["page_slugs"])
                    source_ids.append(ingest_result["source_id"])
                    total_passages += ingest_result.get("passage_count", 0)
                    if ingest_result.get("skipped"):
                        skipped += 1
                    else:
                        success += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                errors.append({
                    "file": str(file_path),
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                })
                logger.error(f"Failed to ingest {file_path}: {e}")

        # 所有文件导入完成后，解析 [[wiki link]] 到实际页面 slug
        if page_slugs:
            resolved = self._resolve_all_wiki_links(page_slugs)
            logger.info(f"Resolved {resolved} wiki links across {len(page_slugs)} pages")

        if self.config.compile_on_ingest and source_ids:
            topic_results = self._compile_topics_for_sources(source_ids)
            page_slugs.extend([page.slug for page in topic_results])

        self.storage.insert_ingest_run(
            self._build_ingest_run(
                source_ids=source_ids,
                started_at=run_started_at,
                success=success,
                failed=failed,
                skipped=skipped,
                page_count=len(page_slugs),
                passage_count=total_passages,
                errors=errors,
            )
        )

        self._write_summary(
            action="ingest",
            paths=paths,
            success=success,
            failed=failed,
            skipped=skipped,
            page_slugs=page_slugs,
            source_ids=source_ids,
        )

        return {
            "success": success,
            "failed": failed,
            "skipped": skipped,
            "pages": page_slugs,
            "sources": source_ids,
            "errors": errors,
        }

    def _resolve_all_wiki_links(self, page_slugs: List[str]) -> int:
        """批量解析 [[wiki link]] 到实际 page slug

        在所有页面导入完成后调用，将正文中的 [[link]] 映射为真实 slug。
        匹配策略（按优先级）：
        1. 精确匹配 page title（去掉 "Source: " 前缀）
        2. link text 是某个 slug 的子串（或反之）
        3. link text 中任意词（按 -/_ 分割）匹配到 title 或 slug
        """
        import re
        all_pages = self.storage.list_pages(limit=1000)

        # 为每个页面建立多个索引键
        # key -> slug
        slug_map: Dict[str, str] = {}
        for p in all_pages:
            title = p.title.lower()
            for prefix in ("source: ", "conversation: "):
                title = title.removeprefix(prefix)
            slug_map[title] = p.slug
            slug_map[p.slug.lower()] = p.slug
            # 也索引 slug 中去掉 "source-" 前缀和 hash 后缀的部分
            core = p.slug.lower()
            for prefix in ("source-", "conversation-"):
                core = core.removeprefix(prefix)
            # 去掉末尾 -xxxxxxxx (8位hash)
            core = re.sub(r'-[a-f0-9]{8}$', '', core)
            if core:
                slug_map[core] = p.slug

        def find_match(link: str) -> Optional[str]:
            key = link.lower().strip()
            # 1. 精确匹配
            if key in slug_map:
                return slug_map[key]
            # 2. 子串匹配
            for k, v in slug_map.items():
                if key in k or k in key:
                    slug_map[key] = v  # 缓存
                    return v
            # 3. 分词匹配（按 - / _ 分割）
            tokens = re.split(r'[-/_]', key)
            for token in tokens:
                if len(token) < 3:
                    continue
                for k, v in slug_map.items():
                    if token in k:
                        slug_map[key] = v
                        return v
            return None

        resolved_count = 0
        for page in all_pages:
            if page.slug not in page_slugs:
                continue
            raw_links = re.findall(
                r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', page.body_md or ""
            )
            resolved: List[str] = []
            for link_text in raw_links:
                target = find_match(link_text)
                if target:
                    resolved.append(target)
            page.link_slugs = list(set(resolved))
            self.storage.insert_page(page)  # 更新 links 表
            resolved_count += len(resolved)
        return resolved_count

    def _ingest_single_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """导入单个文件

        Args:
            file_path: 文件路径

        Returns:
            创建的页面 slug，失败返回 None
        """
        file_path = file_path.resolve()

        # 检查是否支持
        extractor = get_extractor(str(file_path))
        if extractor is None:
            logger.warning(f"No extractor for {file_path}, skipping")
            return None

        # 生成 source_id
        source_id = self._generate_source_id(file_path)
        file_sha = self._compute_sha256(file_path)

        # 检查是否已存在
        existing = self.storage.get_source(source_id)
        if existing is not None:
            if self._should_recompile_existing(existing, file_sha):
                logger.info(f"Source {source_id} already exists, recompiling")
                self._delete_source_bundle(source_id)
            else:
                logger.info(f"Source {source_id} already exists, skipping")
                return {
                    "source_id": source_id,
                    "page_slugs": [page.slug for page in self.storage.get_pages_by_source(source_id)],
                    "skipped": True,
                }

        # 复制文件到 vault（如果配置了）
        stored_path = None
        if self.config.copy_raw_files:
            stored_path = self._copy_to_vault(file_path, source_id)

        # 提取文件
        result = extractor.extract(str(file_path))
        if result.status != "success" or not result.sections:
            logger.warning(f"Extraction failed for {file_path}: {result.error}")
            return None

        # 设置 source_id 和 section_id
        for section in result.sections:
            section.source_id = source_id

        # 规范化 sections -> passages
        passages = normalize_sections(
            result.sections,
            max_chars=self.config.max_passage_chars,
            overlap_chars=self.config.overlap_chars,
        )
        conversation_bundle = self._extract_conversation_bundle(file_path)

        # 创建 source record
        content_hash = self._compute_content_hash(result.sections, passages)
        derived_title = self._derive_source_title(file_path, result.sections)
        source = SourceRecord(
            source_id=source_id,
            source_type=SourceType.CHAT_JSON if conversation_bundle else self._detect_source_type(file_path),
            authority=self._determine_authority(file_path, conversation_bundle),
            original_path=str(file_path),
            stored_path=str(stored_path) if stored_path else None,
            sha256=file_sha,
            title=derived_title,
            mime=self._detect_mime(file_path),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            extractor_name=extractor.__class__.__name__,
            extractor_version=extractor.get_version(),
            status=IngestStatus.SUCCESS.value,
            content_hash=content_hash,
            compile_status="pending" if self.config.compile_on_ingest else "disabled",
            meta_json={
                "file_size": file_path.stat().st_size if file_path.exists() else 0,
            },
        )

        # 存储
        self.storage.insert_source(source)
        self._update_raw_manifest(source)
        for passage in passages:
            passage.source_id = source_id
            self.storage.insert_passage(passage)
        self._write_normalized_artifacts(source, result.sections, passages)
        source_page = self._compile_source_page(source, result.sections, passages)
        page_slugs = [source_page.slug]
        if conversation_bundle:
            conversation_page = self._persist_conversation_bundle(source, conversation_bundle)
            if conversation_page:
                page_slugs.append(conversation_page.slug)

        return {
            "source_id": source_id,
            "page_slugs": page_slugs,
            "passage_count": len(passages),
            "skipped": False,
        }

    def search(
        self,
        query: str,
        top_k: int = 8,
        scope: str = "hybrid",
    ) -> Dict[str, Any]:
        """搜索 wiki

        Args:
            query: 搜索查询
            top_k: 返回结果数量
            scope: 搜索范围 "pages" | "passages" | "hybrid"

        Returns:
            {
                pages: [...],      # 页面级别命中
                passages: [...],   # 段落级别命中
                citations: [...],  # 引用列表
                related_pages: [...] # 相关页面
            }
        """
        if scope == "pages":
            results = self.fts.search_pages(query, limit=top_k)
            return {
                "pages": [_result_to_dict(r) for r in results],
                "passages": [],
                "citations": [],
                "related_pages": [],
            }
        elif scope == "passages":
            results = self.fts.search_passages(query, limit=top_k)
            return {
                "pages": [],
                "passages": [_result_to_dict(r) for r in results],
                "citations": [],
                "related_pages": [],
            }
        else:  # hybrid
            response = self.fts.search_hybrid(query, page_limit=top_k, passage_limit=top_k * 2)
            return {
                "pages": [_result_to_dict(r) for r in response.pages],
                "passages": [_result_to_dict(r) for r in response.passages],
                "citations": self._build_citations([_result_to_dict(r) for r in response.passages]),
                "related_pages": [r.result_id for r in response.pages[:5]],
            }

    def read_page(self, slug: str) -> Dict[str, Any]:
        """读取页面

        Args:
            slug: 页面 slug

        Returns:
            {
                page: WikiPage,       # 页面数据
                sources: [...],       # 来源列表
                citations: [...],     # 引用列表
                backlinks: [...]      # 反向链接 [{slug, title}, ...]
            }
        """
        page = self.storage.get_page(slug)
        if page is None:
            return {"page": None, "sources": [], "citations": [], "backlinks": []}

        # 获取来源
        sources = []
        for source_id in page.source_ids:
            source = self.storage.get_source(source_id)
            if source:
                sources.append(_source_to_dict(source))

        # 构建 citations（优先真实来源，再补内部链接）
        citations = self._build_page_citations(page, sources)

        # 获取反向链接
        backlinks = self.storage.get_backlinks(slug)

        page_dict = _page_to_dict(page)
        if page.markdown_path:
            markdown_path = Path(page.markdown_path)
            if markdown_path.exists():
                page_dict["body_md"] = markdown_path.read_text(encoding="utf-8")

        return {
            "page": page_dict,
            "sources": sources,
            "citations": citations,
            "backlinks": backlinks,
        }

    def rebuild(
        self,
        source_id: Optional[str] = None,
        page_slug: Optional[str] = None,
        all: bool = False,
    ) -> Dict[str, Any]:
        """重建索引

        Args:
            source_id: 只重建某文件的页面
            page_slug: 只重建某页面
            all: 重建所有

        Returns:
            { rebuilt: int, errors: list }
        """
        errors: List[Dict[str, Any]] = []
        rebuilt = 0

        if all:
            # 重建所有 FTS 索引 - 直接通过 Storage 连接操作
            self._rebuild_fts_indexes()
            compiled_sources = [source.source_id for source in self.storage.list_sources(limit=1000)]
            rebuilt += len(self._compile_topics_for_sources(compiled_sources)) + 1

        elif source_id:
            # 只重建某 source 的页面
            source = self.storage.get_source(source_id)
            if source is None:
                errors.append({"source_id": source_id, "error": "Source not found"})
            else:
                try:
                    # 删除旧数据
                    self._delete_source_data(source_id)
                    # 重新导入
                    if source.original_path:
                        path = Path(source.original_path)
                        if path.exists():
                            self._ingest_single_file(path)
                            rebuilt += 1
                        else:
                            errors.append({
                                "source_id": source_id,
                                "error": f"File not found: {source.original_path}"
                            })
                except Exception as e:
                    errors.append({
                        "source_id": source_id,
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    })

        elif page_slug:
            # 只重建某页面
            page = self.storage.get_page(page_slug)
            if page is None:
                errors.append({"page_slug": page_slug, "error": "Page not found"})
            else:
                try:
                    # 删除并重建
                    self._delete_page_data(page_slug)
                    for sid in page.source_ids:
                        self._delete_source_data(sid)
                        source = self.storage.get_source(sid)
                        if source and source.original_path:
                            path = Path(source.original_path)
                            if path.exists():
                                self._ingest_single_file(path)
                                rebuilt += 1
                except Exception as e:
                    errors.append({
                        "page_slug": page_slug,
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    })

        self._write_summary(
            action="rebuild",
            paths=[source_id or page_slug or "all"] if (source_id or page_slug or all) else [],
            success=rebuilt,
            failed=len(errors),
            skipped=0,
            page_slugs=[],
            source_ids=[source_id] if source_id else [],
        )
        return {"rebuilt": rebuilt, "errors": errors}

    def _compile_source_page(self, source: SourceRecord, sections, passages: List[Passage]):
        compile_result = self.compiler.compile_source_page(source, sections, passages)
        page = compile_result.page
        page.content_hash = source.content_hash
        page.markdown_path = str(self.compiler.write_markdown_page(page))

        from .compiler.linker import LinkBuilder
        linker = LinkBuilder()
        page.link_slugs = list(set(page.link_slugs + linker.extract_wiki_links(page.body_md)))

        self.storage.insert_page(page)
        self.storage.update_source_compile_state(
            source.source_id,
            compile_status="success" if compile_result.used_llm else page.compile_status,
            compiled_at=page.compiled_at or datetime.utcnow(),
            compiled_by_model=page.compiled_by_model,
            compile_error=compile_result.error,
            content_hash=source.content_hash,
            stale_reason=None,
        )
        return page

    def _compile_topics_for_sources(self, source_ids: List[str]) -> List[Any]:
        sources = [self.storage.get_source(source_id) for source_id in source_ids]
        sources = [source for source in sources if source is not None]
        passages_by_source = {
            source.source_id: self.storage.get_passages_by_source(source.source_id)
            for source in sources
        }
        results = self.compiler.compile_topic_pages(sources, passages_by_source)
        pages = []
        for result in results:
            page = result.page
            page.content_hash = self._compute_text_hash(page.body_md)
            page.markdown_path = str(self.compiler.write_markdown_page(page))
            self.storage.insert_page(page)
            pages.append(page)
        return pages

    def _persist_conversation_bundle(self, source: SourceRecord, bundle: Dict[str, Any]) -> Optional[Any]:
        messages = bundle.get("messages") or []
        if not messages:
            return None
        conversation = Conversation(
            conversation_id=str(bundle.get("conversation_id") or source.source_id),
            source_id=source.source_id,
            title=bundle.get("title") or source.title,
            participants=self._participants_from_messages(messages),
            created_at=self._parse_timestamp(bundle.get("created_at")),
            updated_at=self._parse_timestamp(bundle.get("updated_at")) or datetime.utcnow(),
            meta_json={
                "origin": bundle.get("origin"),
                "message_count": len(messages),
            },
        )
        turns = [
            Turn(
                conversation_id=conversation.conversation_id,
                role=str(message.get("role") or "unknown").lower(),
                content_text=str(message.get("content") or "").strip(),
                timestamp=self._parse_timestamp(message.get("timestamp")),
                order_index=index,
                meta_json={"source_title": source.title},
            )
            for index, message in enumerate(messages)
            if str(message.get("content") or "").strip()
        ]
        self.storage.insert_conversation(conversation)
        self.storage.insert_turns(turns)
        page = self._compile_conversation_page(conversation, turns, source)
        return page

    def _compile_conversation_page(self, conversation: Conversation, turns: List[Turn], source: SourceRecord):
        summary = next((turn.content_text for turn in turns if turn.role == "assistant" and turn.content_text), "")[:240]
        key_turns = turns[: min(len(turns), 6)]
        page = build_conversation_note(
            conversation=conversation,
            turns=turns,
            summary=summary or source.title or "",
            key_turns=key_turns,
            related_topics=[],
        )
        page.source_ids = [source.source_id]
        page.content_hash = source.content_hash
        page.compiled_at = datetime.utcnow()
        page.compile_status = "derived"
        page.markdown_path = str(self.compiler.write_markdown_page(page))
        self.storage.insert_page(page)
        return page

    def _extract_conversation_bundle(self, file_path: Path) -> Optional[Dict[str, Any]]:
        if file_path.suffix.lower() == ".json":
            return ChatJsonExtractor.load_conversation_payload(str(file_path))
        if self._is_readable_conversation_doc(file_path):
            return self._parse_conversation_markdown(file_path)
        return None

    def _is_readable_conversation_doc(self, file_path: Path) -> bool:
        resolved = file_path.resolve()
        if resolved.suffix.lower() not in {".md", ".markdown"}:
            return False
        try:
            resolved.relative_to(self.config.readable_docs_dir.resolve())
            return True
        except ValueError:
            pass
        return "llmwiki_docs" in str(resolved)

    def _parse_conversation_markdown(self, file_path: Path) -> Optional[Dict[str, Any]]:
        text = file_path.read_text(encoding="utf-8")
        title_match = re.search(r"(?m)^#\s+(.+)$", text)
        conversation_id_match = re.search(r"(?m)^- Conversation ID:\s*(.+)$", text)
        created_match = re.search(r"(?m)^- Created At:\s*(.+)$", text)
        updated_match = re.search(r"(?m)^- Updated At:\s*(.+)$", text)
        turn_matches = list(
            re.finditer(
                r"(?ms)^###\s+Turn\s+(\d+)\s+·\s+([^\n]+)\n+(.*?)(?=^###\s+Turn\s+\d+\s+·|\Z)",
                text,
            )
        )
        messages: List[Dict[str, Any]] = []
        for match in turn_matches:
            role = match.group(2).strip().lower()
            role = {"user": "user", "assistant": "assistant", "system": "system"}.get(role, role)
            content = match.group(3).strip()
            if content:
                messages.append({"role": role, "content": content})
        if not messages:
            return None
        return {
            "conversation_id": conversation_id_match.group(1).strip() if conversation_id_match else file_path.stem,
            "title": title_match.group(1).strip() if title_match else file_path.stem,
            "created_at": created_match.group(1).strip() if created_match else None,
            "updated_at": updated_match.group(1).strip() if updated_match else None,
            "messages": messages,
            "origin": "readable_markdown",
        }

    def _determine_authority(self, file_path: Path, conversation_bundle: Optional[Dict[str, Any]]) -> str:
        if conversation_bundle or self._is_readable_conversation_doc(file_path):
            return Authority.SECONDARY_CHAT.value
        return Authority.PRIMARY_DOC.value

    def _participants_from_messages(self, messages: List[Dict[str, Any]]) -> List[str]:
        participants: List[str] = []
        for message in messages:
            role = str(message.get("role") or "").lower()
            if role and role not in participants:
                participants.append(role)
        return participants

    def _parse_timestamp(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None

    def _build_ingest_run(
        self,
        *,
        source_ids: List[str],
        started_at: datetime,
        success: int,
        failed: int,
        skipped: int,
        page_count: int,
        passage_count: int,
        errors: List[Dict[str, Any]],
    ) -> IngestRun:
        status = IngestStatus.SUCCESS.value if failed == 0 else IngestStatus.FAILED.value
        return IngestRun(
            source_ids=source_ids,
            status=status,
            started_at=started_at,
            completed_at=datetime.utcnow(),
            total_files=success + failed + skipped,
            success_files=success,
            failed_files=failed,
            skipped_files=skipped,
            new_pages=page_count,
            updated_pages=page_count,
            errors=errors,
        )

    def _write_normalized_artifacts(self, source: SourceRecord, sections, passages: List[Passage]) -> Path:
        artifact_path = self.config.normalized_output_dir / f"{source.source_id}.json"
        payload = {
            "source": {
                "source_id": source.source_id,
                "title": source.title,
                "authority": source.authority,
                "source_type": source.source_type.value if hasattr(source.source_type, "value") else source.source_type,
                "original_path": source.original_path,
                "stored_path": source.stored_path,
                "sha256": source.sha256,
                "content_hash": source.content_hash,
                "extractor_name": source.extractor_name,
                "extractor_version": source.extractor_version,
            },
            "sections": [
                {
                    "section_id": section.section_id,
                    "kind": section.kind,
                    "title": section.title,
                    "text": section.text,
                    "locator": section.locator,
                    "order_index": section.order_index,
                }
                for section in sections
            ],
            "passages": [
                {
                    "passage_id": passage.passage_id,
                    "section_id": passage.section_id,
                    "text": passage.text,
                    "locator": passage.locator,
                    "order_index": passage.order_index,
                    "token_count_est": passage.token_count_est,
                }
                for passage in passages
            ],
            "generated_at": datetime.utcnow().isoformat(),
        }
        artifact_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return artifact_path

    def _update_raw_manifest(self, source: SourceRecord) -> Path:
        manifest_path = self.config.workspace_path / "row_manifest.json"
        manifest: Dict[str, Any] = {"sources": []}
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError, TypeError, ValueError):
                manifest = {"sources": []}
        entries = manifest.setdefault("sources", [])
        entry = {
            "source_id": source.source_id,
            "title": source.title,
            "authority": source.authority,
            "original_path": source.original_path,
            "stored_path": source.stored_path,
            "sha256": source.sha256,
            "content_hash": source.content_hash,
            "updated_at": datetime.utcnow().isoformat(),
        }
        updated = False
        for idx, current in enumerate(entries):
            if current.get("source_id") == source.source_id or current.get("original_path") == source.original_path:
                entries[idx] = entry
                updated = True
                break
        if not updated:
            entries.append(entry)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return manifest_path

    def _write_summary(
        self,
        action: str,
        paths: List[str],
        success: int,
        failed: int,
        skipped: int,
        page_slugs: List[str],
        source_ids: List[str],
    ) -> None:
        pages = self.storage.list_pages(limit=2000)
        sources = [self.storage.get_source(source_id) for source_id in source_ids]
        sources = [source for source in sources if source is not None]
        compile_counts: Dict[str, int] = {}
        for page in pages:
            compile_counts[page.compile_status] = compile_counts.get(page.compile_status, 0) + 1

        topic_pages = [
            page for page in pages
            if (page.kind.value if hasattr(page.kind, "value") else page.kind) == "topic"
        ]
        source_pages = [
            page for page in pages
            if (page.kind.value if hasattr(page.kind, "value") else page.kind) == "source_note"
        ]
        latest_sources = [source.title or source.original_path or source.source_id for source in sources[:10]]
        top_topics = [page.title for page in topic_pages[:10]]

        body = [
            "# LLMWiki Summary",
            "",
            "## Layers",
            "",
            f"- row: external raw sources, treated as immutable inputs with hash-tracked snapshots under `{self.config.vault_path}`",
            f"- llmwiki: workspace artifacts under `{self.config.workspace_path}`",
            f"- summary: this file at `{self.config.summary_path}`",
            "",
            "## Current Status",
            "",
            f"- Last action: `{action}`",
            f"- Updated at: `{datetime.utcnow().isoformat()}`",
            f"- Workspace: `{self.config.workspace_path}`",
            f"- Raw snapshot dir: `{self.config.vault_path}`",
            f"- Readable docs dir: `{self.config.readable_docs_dir}`",
            f"- Normalized dir: `{self.config.normalized_output_dir}`",
            f"- Page output dir: `{self.config.markdown_output_dir}`",
            f"- Database: `{self.config.db_path}`",
            "",
            "## Latest Run",
            "",
            f"- Input paths: {', '.join(paths) if paths else 'N/A'}",
            f"- Sources processed: {len(source_ids)}",
            f"- Success: {success}",
            f"- Failed: {failed}",
            f"- Skipped: {skipped}",
            f"- Pages touched: {len(page_slugs)}",
            "",
            "## Workspace Totals",
            "",
            f"- Total pages: {len(pages)}",
            f"- Source pages: {len(source_pages)}",
            f"- Topic pages: {len(topic_pages)}",
            f"- Compile status counts: {json.dumps(compile_counts, ensure_ascii=False)}",
            "",
            "## Recent Sources",
            "",
        ]
        body.extend(f"- {title}" for title in latest_sources) if latest_sources else body.append("- N/A")
        body.extend(["", "## Top Topics", ""])
        body.extend(f"- {title}" for title in top_topics) if top_topics else body.append("- N/A")
        body.append("")
        self.config.summary_path.write_text("\n".join(body), encoding="utf-8")

    # ========== 辅助方法 ==========

    def _supported_extensions(self) -> List[str]:
        """返回支持的扩展名"""
        return [
            ".md", ".markdown", ".txt", ".text",
            ".html", ".htm",
            ".csv", ".json",
            ".pdf", ".pptx", ".ppt",
        ]

    def _generate_source_id(self, file_path: Path) -> str:
        """从文件路径生成 source_id"""
        return hashlib.md5(str(file_path.resolve()).encode()).hexdigest()[:16]

    def _copy_to_vault(self, file_path: Path, source_id: str) -> Optional[Path]:
        """复制文件到 vault 目录"""
        try:
            dest_dir = self.config.vault_path / source_id[:2]
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_path = dest_dir / f"{source_id}{file_path.suffix}"
            shutil.copy2(file_path, dest_path)
            return dest_path
        except Exception as e:
            logger.warning(f"Failed to copy to vault: {e}")
            return None

    def _detect_source_type(self, file_path: Path) -> SourceType:
        """检测源类型"""
        suffix = file_path.suffix.lower()
        type_map = {
            ".md": SourceType.MARKDOWN,
            ".markdown": SourceType.MARKDOWN,
            ".txt": SourceType.TEXT,
            ".text": SourceType.TEXT,
            ".html": SourceType.HTML,
            ".htm": SourceType.HTML,
            ".csv": SourceType.CSV,
            ".json": SourceType.JSON,
            ".pdf": SourceType.PDF,
            ".pptx": SourceType.PPTX,
            ".ppt": SourceType.PPT,
            ".docx": SourceType.DOCX,
            ".yaml": SourceType.YAML,
            ".yml": SourceType.YAML,
        }
        return type_map.get(suffix, SourceType.TEXT)

    def _detect_mime(self, file_path: Path) -> str:
        """检测 MIME 类型"""
        import mimetypes
        mime, _ = mimetypes.guess_type(str(file_path))
        return mime or "application/octet-stream"

    def _compute_sha256(self, file_path: Path) -> str:
        """计算文件 SHA256"""
        h = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return ""

    def _compute_content_hash(self, sections, passages: List[Passage]) -> str:
        material = "\n".join(
            [f"{section.title}:{section.text}" for section in sections[:100]]
            + [passage.text for passage in passages[:100]]
        )
        return self._compute_text_hash(material)

    def _compute_text_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _derive_source_title(self, file_path: Path, sections) -> str:
        candidates: List[str] = []
        for section in sections:
            title = (getattr(section, "title", None) or "").strip()
            text = (getattr(section, "text", None) or "").strip()
            candidates.extend([title, self._extract_heading_text(text)])
            if title.lower() in {"title", "name", "subject"} or title in {"标题", "名称", "主题"}:
                candidates.append(text)
            meta = getattr(section, "meta_json", None) or {}
            if isinstance(meta, str):
                try:
                    meta = json.loads(meta)
                except json.JSONDecodeError:
                    meta = {}
            if isinstance(meta, dict):
                candidates.append(str(meta.get("source_title") or ""))
            candidates.append(self._extract_question_text(text))
        candidates.append(file_path.stem)
        for candidate in candidates:
            candidate = self._sanitize_title(candidate)
            if candidate:
                return candidate
        return self._sanitize_title(file_path.stem) or normalize_title(file_path.stem, str(file_path))

    def _extract_heading_text(self, text: str) -> str:
        first_line = text.splitlines()[0].strip() if text else ""
        if first_line.startswith("#"):
            return first_line.lstrip("#").strip()
        return ""

    def _extract_question_text(self, text: str) -> str:
        if not text:
            return ""
        match = re.search(r"(?ms)^##\s+(?:Question|问题)\s*\n+(.+?)(?=^##\s+|\Z)", text)
        if not match:
            match = re.search(r"(?m)^\[(?:user|human)\]\s*:\s*(.+)$", text, flags=re.IGNORECASE)
        if not match:
            return ""
        first_line = next((line.strip() for line in match.group(1).splitlines() if line.strip()), "")
        first_line = re.sub(r"^\[(user|assistant|system|unknown)\]\s*:\s*", "", first_line, flags=re.IGNORECASE)
        first_line = re.sub(r"^(请帮我|帮我|请问|想知道|求问|我想|能否|可否|请)\s*", "", first_line)
        first_line = re.split(r"[。！？!?]\s*", first_line, maxsplit=1)[0].strip(" -_#*？?。.:：")
        return first_line[:120]

    def _sanitize_title(self, title: str) -> str:
        title = title.strip()
        title = re.sub(r"^[0-9a-f]{8}-[0-9a-f-]{27}[_\-\s]*", "", title, flags=re.IGNORECASE)
        title = re.sub(r"^[0-9a-f]{8,64}[_\-\s]*", "", title, flags=re.IGNORECASE)
        title = re.sub(r"^(source|conversation)\s*[:：]\s*", "", title, flags=re.IGNORECASE)
        title = re.sub(r"\bconversation[_\-\s]*id\b", "", title, flags=re.IGNORECASE)
        title = re.sub(r"\bsource[_\-\s]*id\b", "", title, flags=re.IGNORECASE)
        title = re.sub(r"^tmp[_\-\s]+", "", title, flags=re.IGNORECASE)
        title = re.sub(r"[_]+", " ", title)
        title = re.sub(r"[_\-]+", " ", title).strip(" -_:.：")
        lowered = title.lower()
        if lowered in {"untitled", "untitled source", "untitled conversation", "source", "conversation", "conversation id", "question", "title", "name", "subject"}:
            return ""
        if re.search(r"(?i)\bconversation\b", title):
            return ""
        if re.fullmatch(r"[0-9a-f]{8,}", lowered):
            return ""
        return title[:120]

    def _should_recompile_existing(self, source: SourceRecord, file_sha: str) -> bool:
        current_model = self.compiler.client.model_name() if self.compiler.client.is_enabled() else None
        if source.sha256 != file_sha:
            return True
        if self.config.compile_on_ingest:
            if self.compiler.client.is_enabled():
                if source.compiled_by_model != current_model:
                    return True
                if source.compile_status != "success":
                    return True
            elif source.compile_status in {"pending"}:
                return True
        return False

    def _delete_source_bundle(self, source_id: str) -> None:
        """Delete a source and its source pages so it can be reingested cleanly."""
        pages = self.storage.get_pages_by_source(source_id)
        for page in pages:
            if len(page.source_ids) <= 1 or page.kind.value == "source_note":
                self._delete_page_data(page.slug)
        self._delete_source_data(source_id)

    def _delete_source_data(self, source_id: str) -> None:
        """删除 source 相关数据"""
        with self.storage.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT conversation_id FROM conversations WHERE source_id = ?",
                (source_id,),
            )
            conversation_ids = [row["conversation_id"] for row in cursor.fetchall()]
            cursor.execute(
                "SELECT passage_id FROM passages WHERE source_id = ?",
                (source_id,),
            )
            passage_ids = [row["passage_id"] for row in cursor.fetchall()]
            for passage_id in passage_ids:
                cursor.execute("DELETE FROM passages_fts WHERE passage_id = ?", (passage_id,))
            # 删除 passages
            cursor.execute("DELETE FROM passages WHERE source_id = ?", (source_id,))
            # 删除 page_sources
            cursor.execute("DELETE FROM page_sources WHERE source_id = ?", (source_id,))
            for conversation_id in conversation_ids:
                cursor.execute("DELETE FROM turns WHERE conversation_id = ?", (conversation_id,))
            cursor.execute("DELETE FROM conversations WHERE source_id = ?", (source_id,))
            # 删除 source
            cursor.execute("DELETE FROM sources WHERE source_id = ?", (source_id,))
            conn.commit()

    def _delete_page_data(self, slug: str) -> None:
        """删除页面数据"""
        with self.storage.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM pages WHERE slug = ?", (slug,))
            cursor.execute("DELETE FROM page_sources WHERE slug = ?", (slug,))
            cursor.execute("DELETE FROM links WHERE from_slug = ? OR to_slug = ?", (slug, slug))
            cursor.execute("DELETE FROM pages_fts WHERE slug = ?", (slug,))
            conn.commit()

    def _build_citations(self, passage_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """从段落搜索结果构建引用列表"""
        citations = []
        for passage in passage_results:
            meta = passage.get("meta", {})
            source_id = meta.get("source_id", "")
            if source_id:
                source = self.storage.get_source(source_id)
                if source:
                    citations.append({
                        "source_id": source_id,
                        "title": source.title or source.original_path,
                        "authority": source.authority,
                        "source_type": source.source_type.value if hasattr(source.source_type, "value") else source.source_type,
                        "locator": meta.get("locator"),
                        "excerpt": passage.get("snippet", ""),
                    })
        return citations

    def _generate_snippet(self, text: str, query: str, max_length: int = 200) -> str:
        """生成搜索结果片段"""
        if not text:
            return ""
        pos = text.find(query)
        if pos == -1:
            return text[:max_length] + "..." if len(text) > max_length else text
        start = max(0, pos - 50)
        end = min(len(text), pos + len(query) + 150)
        snippet = text[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        return snippet

    def _extract_citations_from_body(self, body_md: str) -> List[Dict[str, Any]]:
        """从 page body 中提取内部链接引用（基于 [[link]] 格式）"""
        import re
        citations = []
        # 提取 [[slug]] 或 [[slug|text]] 格式的链接
        links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', body_md)
        seen = set()
        for slug in links:
            if slug not in seen:
                seen.add(slug)
                citations.append({"slug": slug, "type": "internal_link"})
        return citations

    def _build_page_citations(self, page, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        citations: List[Dict[str, Any]] = []
        seen = set()
        for source in sources:
            source_id = source.get("source_id")
            if not source_id or source_id in seen:
                continue
            seen.add(source_id)
            passages = self.storage.get_passages_by_source(source_id)
            citations.append(
                {
                    "source_id": source_id,
                    "title": source.get("title") or source.get("original_path"),
                    "authority": source.get("authority"),
                    "source_type": source.get("source_type"),
                    "locator": source.get("original_path"),
                    "excerpt": passages[0].text[:200] if passages else "",
                    "type": "source",
                }
            )
        citations.extend(self._extract_citations_from_body(page.body_md or ""))
        return citations

    def _rebuild_fts_indexes(self) -> None:
        """重建 FTS 索引（直接操作数据库）"""
        with self.storage.get_conn() as conn:
            cursor = conn.cursor()
            # 删除并重建 pages FTS
            cursor.execute("DROP TABLE IF EXISTS pages_fts")
            cursor.execute("""
                CREATE VIRTUAL TABLE pages_fts USING fts5(slug, title, body_md)
            """)
            # 删除并重建 passages FTS
            cursor.execute("DROP TABLE IF EXISTS passages_fts")
            cursor.execute("""
                CREATE VIRTUAL TABLE passages_fts USING fts5(passage_id, text, cjk_terms)
            """)
            conn.commit()

            # 重新填充 pages
            cursor.execute("SELECT slug, title, body_md FROM pages")
            for row in cursor.fetchall():
                cursor.execute(
                    "INSERT INTO pages_fts (slug, title, body_md) VALUES (?, ?, ?)",
                    (row["slug"], row["title"], row["body_md"] or "")
                )

            # 重新填充 passages
            cursor.execute("SELECT passage_id, text, cjk_terms FROM passages")
            for row in cursor.fetchall():
                cursor.execute(
                    "INSERT INTO passages_fts (passage_id, text, cjk_terms) VALUES (?, ?, ?)",
                    (row["passage_id"], row["text"], row["cjk_terms"] or "[]")
                )

            conn.commit()

    def list_pages(self, limit: int = 100) -> List[Dict[str, Any]]:
        """列出所有页面（供 CLI 使用）"""
        pages = self.storage.list_pages(limit=limit)
        return [_page_to_dict(p) for p in pages]


def _result_to_dict(result) -> Dict[str, Any]:
    """将搜索结果统一转为 dict"""
    if isinstance(result, dict):
        return result
    return {
        "result_id": result.result_id,
        "result_type": result.result_type,
        "title": result.title,
        "snippet": result.snippet,
        "score": result.score,
        "meta": result.meta,
    }


def _page_to_dict(page) -> Dict[str, Any]:
    """WikiPage -> dict"""
    return {
        "slug": page.slug,
        "title": page.title,
        "kind": page.kind.value if hasattr(page.kind, "value") else page.kind,
        "summary": page.summary,
        "body_md": page.body_md,
        "source_ids": page.source_ids,
        "link_slugs": page.link_slugs,
        "version": page.version,
        "updated_at": page.updated_at.isoformat() if page.updated_at else None,
        "markdown_path": page.markdown_path,
        "compiled_at": page.compiled_at.isoformat() if page.compiled_at else None,
        "compile_status": page.compile_status,
        "compile_error": page.compile_error,
        "compiled_by_model": page.compiled_by_model,
    }


def _source_to_dict(source) -> Dict[str, Any]:
    """SourceRecord -> dict"""
    return {
        "source_id": source.source_id,
        "source_type": source.source_type.value if hasattr(source.source_type, "value") else source.source_type,
        "authority": source.authority,
        "title": source.title,
        "original_path": source.original_path,
        "status": source.status,
        "created_at": source.created_at.isoformat() if source.created_at else None,
        "compiled_at": source.compiled_at.isoformat() if source.compiled_at else None,
        "compile_status": source.compile_status,
        "compile_error": source.compile_error,
        "compiled_by_model": source.compiled_by_model,
    }
