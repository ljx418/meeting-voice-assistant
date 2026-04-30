# LLMWiki 本地知识模块开发计划（可直接贴给 Claude Code）

你现在是 Claude Code。请在当前仓库中实现一个名为 `llmwiki` 的本地知识模块。严格按下面计划执行，不要擅自升级成重型 RAG 平台，不要引入向量数据库、LangChain、图数据库或 Web 前端。目标是：

- 在本地把 AI 学习资料和聊天记录编译成可持续维护的 wiki
- 核心模块高内聚、低依赖、易调试
- 默认在 MacBook Pro 2020 上稳定运行
- 后续可以作为本地 MCP server 被 Claude Code 或其他 MCP Host 调用

---

## 1. 产品目标

实现一个“编译型知识库”而不是“临时问答型 RAG”。

核心流程：

`原始资料 -> 标准化抽取 -> 分段索引 -> wiki 页面编译 -> 本地搜索/阅读 -> MCP 暴露`

系统必须支持以下资料进入同一条流水线：

- `md`
- `txt`
- `html`
- `csv`
- `json`
- `pdf`
- `pptx`
- `ppt`（作为可选兼容，不纳入核心强依赖）
- 以 `json` 为主的大语言模型聊天历史记录

---

## 2. 硬性约束

### 2.1 运行约束

- 目标机器：MacBook Pro 2020
- 默认 CPU 模式
- 串行优先，避免大批量并发
- 不依赖常驻后台服务
- 默认单进程可运行
- 单次 ingest 尽量按“单文件 -> 单文件”处理，避免内存峰值

### 2.2 依赖约束

核心运行层尽量只用 Python 标准库：

- `sqlite3`
- `pathlib`
- `json`
- `hashlib`
- `dataclasses`
- `argparse`
- `re`
- `logging`
- `zipfile`
- `xml.etree.ElementTree`
- `datetime`
- `tempfile`
- `shutil`
- `subprocess`
- `typing`

允许的可选依赖：

- `pypdf`：仅用于数字型 PDF 文本提取
- 不允许在首版引入向量数据库、LangChain、LlamaIndex、FAISS、Chroma、Neo4j
- 不允许首版依赖 OCR 工具链

### 2.3 工程约束

- 核心能力必须集中在 `llmwiki/` 内部
- CLI 和 MCP 只是薄适配层，不承载业务逻辑
- 所有写入操作必须原子化
- 所有日志写到 stderr 或日志文件，不污染 MCP stdout
- 所有行为尽量可重复、可恢复、可增量更新

---

## 3. 首版范围与非目标

### 3.1 首版必须完成

1. 本地资料导入与增量更新
2. 多格式文本抽取
3. SQLite 持久化与全文索引
4. wiki 页面生成与更新
5. 基于页面和证据片段的本地搜索
6. CLI
7. 本地 stdio MCP server
8. 基础测试和 README

### 3.2 首版明确不做

1. Web UI
2. 多用户协同
3. 远程服务部署
4. 向量库
5. OCR
6. 自动联网抓取资料
7. 图数据库
8. 大而全的 Agent 编排
9. 把聊天记录中的模型回答直接当作权威事实

---

## 4. 关键设计原则

### 4.1 权威级别分层

定义数据来源权威级别：

- `PRIMARY_DOC`：MD / PDF / PPTX / HTML / TXT / CSV 等文档资料
- `SECONDARY_CHAT`：聊天历史中的内容，尤其是 assistant 回答
- `DERIVED_WIKI`：编译产物，不是原始事实来源

规则：

- `PRIMARY_DOC` 可以直接作为事实证据
- `SECONDARY_CHAT` 只能作为“学习示例 / 提问上下文 / 候选结论”，不能无验证写入事实区
- 聊天记录中的 assistant 内容若未被文档或其他来源佐证，必须落在 `Examples`、`Notes`、`Hypotheses`、`Unverified` 等区域，不得进入 `Facts`

### 4.2 先编译，再查询

不要把原始文档直接当最终问答面。优先从已编译的 wiki 页面回答，再回落到原始证据片段。

### 4.3 所有结论可追溯

每个页面中的事实条目必须能追溯到：

- 源文件
- 源文件内部位置
- 提取片段

### 4.4 高内聚

核心对外只暴露 4 个主动作：

- `ingest()`
- `search()`
- `read_page()`
- `rebuild()`

---

## 5. 目录结构

请实现以下目录布局：

```text
project/
├─ llmwiki/
│  ├─ __init__.py
│  ├─ engine.py
│  ├─ config.py
│  ├─ models.py
│  ├─ storage.py
│  ├─ normalize.py
│  ├─ extractors/
│  │  ├─ __init__.py
│  │  ├─ base.py
│  │  ├─ markdown.py
│  │  ├─ text.py
│  │  ├─ html.py
│  │  ├─ csvfile.py
│  │  ├─ jsonfile.py
│  │  ├─ pdf_pypdf.py
│  │  ├─ pptx_zip.py
│  │  └─ ppt_legacy.py
│  ├─ compiler/
│  │  ├─ __init__.py
│  │  ├─ classifier.py
│  │  ├─ page_builder.py
│  │  ├─ merger.py
│  │  └─ linker.py
│  ├─ search/
│  │  ├─ __init__.py
│  │  ├─ fts.py
│  │  ├─ ranker.py
│  │  └─ cjk.py
│  ├─ providers/
│  │  ├─ __init__.py
│  │  ├─ base.py
│  │  ├─ null_provider.py
│  │  └─ http_provider.py
│  ├─ cli.py
│  └─ mcp_stdio.py
│
├─ vault/
│  ├─ raw/
│  ├─ normalized/
│  ├─ wiki/
│  │  ├─ pages/
│  │  ├─ indexes/
│  │  └─ logs/
│  └─ state/
│     └─ llmwiki.db
│
├─ tests/
├─ samples/
├─ README.md
└─ pyproject.toml
```

要求：

- `vault/raw/` 保存导入后的原始文件副本或稳定引用信息
- `vault/normalized/` 保存标准化抽取结果（推荐 JSON）
- `vault/wiki/pages/` 保存 markdown 页面
- `vault/state/llmwiki.db` 保存索引与状态

---

## 6. 统一数据模型

请先定义 dataclass / typed models。

### 6.1 SourceRecord

字段建议：

- `source_id: str`
- `source_type: str`
- `authority: str`
- `original_path: str`
- `stored_path: str | None`
- `sha256: str`
- `title: str | None`
- `mime: str | None`
- `created_at: str | None`
- `updated_at: str | None`
- `extractor_name: str`
- `extractor_version: str`
- `status: str`
- `meta_json: dict`

### 6.2 NormalizedSection

字段建议：

- `section_id: str`
- `source_id: str`
- `kind: str`
- `title: str | None`
- `text: str`
- `locator: dict`
- `order_index: int`
- `meta_json: dict`

### 6.3 Passage

字段建议：

- `passage_id: str`
- `source_id: str`
- `section_id: str`
- `text: str`
- `cjk_terms: str`
- `token_count_est: int`
- `locator: dict`
- `order_index: int`

### 6.4 WikiPage

字段建议：

- `slug: str`
- `title: str`
- `kind: str`
- `summary: str`
- `body_md: str`
- `source_ids: list[str]`
- `link_slugs: list[str]`
- `version: int`
- `updated_at: str`
- `meta_json: dict`

### 6.5 Citation

字段建议：

- `source_id: str`
- `locator: dict`
- `label: str`
- `excerpt: str | None`

### 6.6 Conversation / Turn

为 JSON 聊天记录定义统一模型：

#### Conversation
- `conversation_id`
- `source_id`
- `title`
- `participants`
- `created_at`
- `updated_at`
- `meta_json`

#### Turn
- `turn_id`
- `conversation_id`
- `role`
- `content_text`
- `timestamp`
- `order_index`
- `meta_json`

---

## 7. 数据库设计

使用 SQLite。

至少实现以下表：

- `sources`
- `normalized_sections`
- `passages`
- `pages`
- `page_sources`
- `links`
- `conversations`
- `turns`
- `ingest_runs`

并实现以下全文索引：

- `pages_fts`
- `passages_fts`

要求：

- 首次启动时自动建表
- 提供 schema version
- 提供基础迁移机制
- 检查 SQLite FTS5 可用性；不可用时给出明确报错

---

## 8. 中文检索支持（必须实现）

不要假设全文都是英文。为了在尽量不引入外部中文分词依赖的前提下支持中文搜索，请实现一个轻量的 CJK 检索策略：

### 8.1 方案

- 对中文文本抽取连续 CJK 字符
- 生成二元组（bigram）和必要时三元组（trigram）
- 以空格拼接后写入 `cjk_terms`
- 对查询语句同样生成 CJK n-gram
- 搜索时同时查 `text` 和 `cjk_terms`

### 8.2 目标

- 英文依赖 FTS5
- 中文通过 n-gram 辅助
- 保持低依赖

---

## 9. 各格式抽取规则

### 9.1 Markdown / TXT / HTML / CSV / 普通 JSON

要求：

- 保留标题层级
- 记录可定位信息（行号、标题路径、键路径等）
- 统一输出为 `NormalizedSection`

### 9.2 PDF

首版要求：

- 支持“数字型 PDF”文本提取
- 每页单独生成 section
- 记录 `page_number`
- 如 PDF 无可提取文本，则标记为 `SCANNED_OR_UNSUPPORTED_PDF`
- 不要静默失败

实现建议：

- 使用可选依赖 `pypdf`
- 如果未安装 `pypdf`，给出清晰错误和安装提示

### 9.3 PPTX

必须支持，无需外部依赖。

实现要求：

- 使用 `zipfile + xml.etree.ElementTree` 解析
- 提取每页 slide 的：
  - slide number
  - title
  - body text
  - bullet 层级
  - notes（若存在）
- 每张 slide 至少形成一个 `NormalizedSection`

### 9.4 Legacy PPT

首版不做强支持，但要做兼容入口：

- 若检测到 `.ppt`
- 优先检查系统中是否存在 `soffice`
- 若存在，则通过可选转换流程转为 `.pptx`
- 若不存在，则返回 `UNSUPPORTED_LEGACY_PPT`
- 核心模块不得强依赖 LibreOffice

### 9.5 JSON 聊天历史

必须重点支持。

至少兼容以下形态：

1. `[{"role": "user", "content": "..."}, ...]`
2. `{"messages": [...]}`
3. 常见导出结构中包含 `mapping` / `conversation` / `items` / `turns`
4. 未知结构时，尽量递归提取 role/content/timestamp/title，失败则报告不支持而非静默跳过

处理规则：

- 保留 turn 顺序
- 保留 role
- 保留时间戳（若存在）
- 将用户提问、模型回答、系统提示拆成 turn
- 生成 conversation 级 summary
- 生成 conversation 页面
- conversation 中的重要主题可以回链到 topic 页面
- assistant 回答默认是 `SECONDARY_CHAT`

---

## 10. 标准化输出与定位规则

请统一 locator 设计，保证任何片段都可追溯。

### 10.1 locator 示例

- Markdown/TXT/HTML: `{ "kind": "lines", "start": 10, "end": 28, "heading_path": ["A", "B"] }`
- PDF: `{ "kind": "pdf_page", "page": 12 }`
- PPTX: `{ "kind": "slide", "slide": 5 }`
- JSON Chat: `{ "kind": "turn", "conversation_id": "...", "turn": 14 }`
- CSV: `{ "kind": "row_range", "start": 101, "end": 120 }`

### 10.2 引用展示格式

请统一生成面向用户的 citation label：

- `paper.md#Transformer/Attention [L12-L35]`
- `notes.pdf [p.12]`
- `lecture.pptx [slide 8]`
- `chat_history.json [turn 14]`

---

## 11. 分段策略

在 `NormalizedSection` 基础上再切为 `Passage`。

要求：

- 目标长度：约 800~1500 中文字或等价英文长度
- 小重叠：100~150 字
- 不要粗暴跨标题拼接
- 分段必须保留 section 和 locator 继承关系

---

## 12. wiki 编译策略

不要只做 source 摘要。要生成真正可导航的 wiki。

### 12.1 页面类型

至少实现以下类型：

1. `source_note`
   - 每个源文件一页
   - 包含来源信息、摘要、章节结构、主题标签、关键片段

2. `topic`
   - 按主题聚合
   - 例如：Transformer、RAG、MCP、Fine-tuning、LoRA、Prompt Engineering

3. `conversation_note`
   - 每个聊天记录一页
   - 包含摘要、关键问题、关键回答、未验证结论、相关主题

4. `index`
   - 总索引页
   - 最近导入
   - 按主题索引
   - 按资料类型索引

### 12.2 topic page 结构

所有 topic 页面尽量使用统一结构：

```md
---
slug: transformer
kind: topic
updated_at: 2026-04-23T10:00:00Z
sources: [src_x, src_y]
---

# Transformer

## TL;DR
...

## Facts
- ...

## Key Ideas
- ...

## Examples
- ...

## Open Questions
- ...

## Related Pages
- [[attention]]
- [[llm]]

## Citations
- ...
```

规则：

- `Facts` 只能写入由 PRIMARY_DOC 直接支持的事实
- `Examples` 可以吸收聊天记录中的问答片段
- `Open Questions` 可来自聊天记录中的未解决问题

### 12.3 source_note 结构

要求至少包含：

- 文件信息
- 摘要
- 章节/页/slide 提纲
- 主要主题
- 关键摘录
- 反向链接

### 12.4 conversation_note 结构

要求至少包含：

- 会话摘要
- 主题标签
- 关键 turn 摘录
- 常见误区 / 未验证结论
- 可回链 topic 页面

---

## 13. 页面生成策略

必须分为两层：

### 13.1 规则优先层（首版必须完成）

无论是否配置外部 LLM，都必须能跑通。

需要实现：

- 基于标题/文件名/关键词的主题归类
- 基于频次和规则的关键词抽取
- 基于模板的页面骨架生成
- 基于已有页面的增量 merge

### 13.2 可选 LLM 增强层（首版可选实现）

定义一个非常小的 provider 接口：

- `summarize(text, instruction)`
- `extract_topics(text)`
- `merge_page(old_page, evidence, instruction)`

要求：

- 未配置 provider 时，系统仍可运行
- provider 只能作为增强，不可成为系统刚需
- 支持一个 `http_provider.py`，兼容 OpenAI-style HTTP API

---

## 14. 页面归类与链接

实现基础分类器和链接器：

### 14.1 分类器规则

综合以下信号：

- 文件名
- 标题
- heading
- 高频术语
- 聊天中的高频问题
- 现有 page 的 aliases

### 14.2 链接器规则

建立以下链接：

- topic -> topic
- source_note -> topic
- conversation_note -> topic
- topic -> source_note

至少实现简单别名映射机制：

- `Transformer`
- `transformer`
- `transformers`
- `注意力机制`
- `attention`

可以映射到同一主题或相关主题

---

## 15. 增量更新机制

必须支持增量构建，不允许每次全量重建。

### 15.1 指纹

使用以下信息确定是否需要重建：

- 文件内容 sha256
- extractor version
- compiler version
- 配置版本

### 15.2 策略

- 新文件：新增 source + 构建相关页面
- 文件变更：只重建受影响的 passages / pages
- 文件删除：在索引中标记失效，并更新引用页面
- 支持 `rebuild --all`

### 15.3 日志

每次 ingest 记录：

- ingest run id
- 成功/失败文件
- 新增/更新 page
- 跳过原因
- 错误信息

日志写入：

- SQLite `ingest_runs`
- `vault/wiki/logs/*.jsonl`

---

## 16. 搜索设计

实现“page 优先 + evidence 回退”的混合检索。

### 16.1 查询流程

1. 先查 `pages_fts`
2. 再查 `passages_fts`
3. 对中文查询同时查 `cjk_terms`
4. 合并结果
5. 去重
6. 轻量重排
7. 返回：页面、证据片段、引用、相关页面

### 16.2 返回结构

搜索结果对象至少包含：

- `pages: list[...]`
- `passages: list[...]`
- `citations: list[...]`
- `related_pages: list[...]`
- `debug: dict`（可选）

### 16.3 排序信号

至少考虑：

- page 命中分数
- passage 命中分数
- 标题命中加权
- topic 精确命中加权
- 最近更新时间轻微加权
- 主文档来源优先于聊天来源

---

## 17. 核心对外 API

`engine.py` 对外只暴露以下能力：

```python
class WikiEngine:
    def ingest(self, paths: list[str] | str) -> dict: ...
    def search(self, query: str, top_k: int = 8, scope: str = "hybrid") -> dict: ...
    def read_page(self, slug: str) -> dict: ...
    def rebuild(self, source_id: str | None = None, page_slug: str | None = None, all: bool = False) -> dict: ...
```

要求：

- 所有上层接口都只能调用 `WikiEngine`
- CLI 和 MCP 不允许直接操作底层存储逻辑

---

## 18. CLI 设计

请实现：

```bash
python -m llmwiki.cli ingest <path-or-dir>
python -m llmwiki.cli search "query"
python -m llmwiki.cli read-page <slug>
python -m llmwiki.cli rebuild --all
python -m llmwiki.cli list-pages
python -m llmwiki.cli doctor
python -m llmwiki.cli serve-mcp
```

### 18.1 doctor

必须检查：

- SQLite / FTS5 可用性
- 可选依赖状态（如 pypdf）
- vault 目录
- `.ppt` 转换器可用性（如 soffice）
- 数据库可写性

---

## 19. MCP 设计

实现本地 stdio MCP server，文件为：

- `llmwiki/mcp_stdio.py`

### 19.1 目标

把 llmwiki 暴露为本地 MCP server，使 Claude Code 能直接调用工具和引用资源。

### 19.2 server 能力

实现以下 resources：

- `llmwiki://index`
- `llmwiki://page/{slug}`
- `llmwiki://source/{source_id}`
- `llmwiki://conversation/{conversation_id}`

实现以下 tools：

- `wiki_search`
- `wiki_read_page`
- `wiki_ingest`
- `wiki_rebuild`
- `wiki_list_pages`
- `wiki_list_recent`

prompts 可先留空或最小实现。

### 19.3 重要约束

- MCP server 只负责暴露能力，不负责最终自然语言回答
- MCP 层不能复制业务逻辑
- stdout 只允许输出 JSON-RPC 消息
- 所有调试日志写 stderr

### 19.4 MCP 返回风格

- `wiki_search` 返回结构化 JSON
- `wiki_read_page` 返回 markdown 正文 + metadata
- resources/read 返回可直接附加为上下文的文本内容

---

## 20. slug 与命名规则

为避免中文 slug 和特殊字符问题，采用保守策略：

- 优先使用可清洗的 ASCII slug
- 若标题无法安全转为 slug，则使用 `page-<hash8>`
- 原标题写入 frontmatter
- 保留 aliases

---

## 21. 配置设计

实现一个轻量配置层，例如 `llmwiki.config.json` 或等价方案。

至少支持：

- `vault_path`
- `copy_raw_files`
- `enable_pdf`
- `enable_ppt_legacy_conversion`
- `llm_provider`
- `llm_api_base`
- `llm_api_key_env`
- `max_passage_chars`
- `overlap_chars`
- `rebuild_policy`

要求：

- 配置未给出时有合理默认值
- 支持环境变量覆盖关键项

---

## 22. 测试要求

必须建立 `tests/`。

### 22.1 单元测试

至少覆盖：

- sha256 / fingerprint
- locator 生成
- passage 切分
- cjk n-gram
- slug 规则
- citation label 生成
- topic 分类规则

### 22.2 集成测试

提供 sample fixtures：

- 1 个 md
- 1 个 pdf（数字文本）
- 1 个 pptx
- 1 个 json chat history

测试以下流程：

1. ingest
2. 生成 source_note
3. 生成 topic page
4. search
5. read_page
6. rebuild
7. MCP tool 基本调用

### 22.3 回归测试

对关键 markdown 页面做 golden test，避免编译结果漂移过大。

---

## 23. README 要求

README 至少包含：

- 项目目标
- 架构图（文本版即可）
- 支持格式
- 不支持项
- 安装方式
- CLI 用法
- MCP 接入方式
- 目录说明
- 增量构建逻辑
- 常见问题

---

## 24. 性能与资源要求

请按以下目标优化：

- 默认不加载全库到内存
- 处理大文件时分段流式处理
- 单个文件抽取完成后及时释放中间对象
- 搜索优先走 SQLite，不扫全量 markdown
- 不在 ingest 阶段并发打开大量 PDF/PPTX

---

## 25. 实施阶段（必须按顺序做）

### Phase 0：项目骨架

完成：

- 目录结构
- `pyproject.toml`
- `README` 初稿
- `models.py`
- `config.py`
- 测试框架基础

验收：

- 项目能安装
- 基础 import 正常

### Phase 1：存储与状态层

完成：

- `storage.py`
- SQLite schema
- FTS5 初始化
- ingest run 记录
- pages / passages / links / conversations 基础 CRUD

验收：

- 能初始化空库
- 能插入和查询 source/page/passage

### Phase 2：抽取器

完成：

- `markdown.py`
- `text.py`
- `html.py`
- `csvfile.py`
- `jsonfile.py`
- `pdf_pypdf.py`
- `pptx_zip.py`
- `ppt_legacy.py`

验收：

- fixture 均能抽出 `NormalizedSection`
- 不支持项能明确报错

### Phase 3：标准化与分段

完成：

- `normalize.py`
- passage splitter
- locator 继承
- cjk n-gram 生成

验收：

- 每个 source 可生成 passages
- passages 带 source/section/locator

### Phase 4：wiki 编译器

完成：

- `classifier.py`
- `page_builder.py`
- `merger.py`
- `linker.py`
- source_note / topic / conversation_note / index 生成

验收：

- ingest 一个 md + 一个 chat json 后，能看到 source page、topic page、conversation page

### Phase 5：搜索层

完成：

- `fts.py`
- `ranker.py`
- `cjk.py`
- engine search

验收：

- 中文英文关键词都可命中相关页面和证据

### Phase 6：核心引擎与 CLI

完成：

- `engine.py`
- `cli.py`
- `doctor`
- `list-pages`

验收：

- CLI 能完成 ingest/search/read/rebuild

### Phase 7：MCP server

完成：

- `mcp_stdio.py`
- resources/list + read
- tools/list + call
- 最小生命周期支持

验收：

- Claude Code 可通过本地 stdio 连接
- 能调用 `wiki_search`
- 能读取 `llmwiki://page/...`

### Phase 8：文档与收尾

完成：

- README 完整化
- sample `.mcp.json`
- 错误处理
- golden tests
- 性能小幅优化

验收：

- 新人可按 README 直接跑通

---

## 26. 输出要求

当你实施时：

1. 每完成一个 Phase，先跑对应测试
2. 输出本阶段修改摘要
3. 不要一次性生成大段未验证代码
4. 如需引入新依赖，必须先说明原因，并证明无法用标准库完成
5. 出现设计冲突时，优先遵守：
   - 高内聚
   - 少依赖
   - 可追溯
   - 增量更新
   - MCP 可调用

---

## 27. 附加要求：给 Claude Code 的具体实现口径

请在实现中遵守以下口径：

- 默认“无 LLM 也能工作”
- 默认“聊天记录不是事实源，只是学习源”
- 默认“先 page 后 passage”
- 默认“中文检索必须可用”
- 默认“legacy ppt 作为可选兼容，不污染核心”
- 默认“PDF 首版只做数字文本 PDF，不做 OCR”
- 默认“MCP 只做能力暴露，不做回答生成”

---

## 28. 最终交付物

最终必须交付：

- 可运行代码
- 测试
- README
- sample fixtures
- sample `.mcp.json`
- 至少一个从实际资料生成的演示 wiki 页面

现在开始按 Phase 顺序实施。
