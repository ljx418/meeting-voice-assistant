# ResearchNotebook V1.1 使用指南图像 Prompt

文档状态：已生成可复用 GPT Image 2 prompt。
日期：2026-05-24。

## 运行模式

本地 `gpt-image-2` 技能检测结果：

```text
mode = B-or-C
garden_mode_enabled = false
has_api_key = false
model = gpt-image-2
```

因此当前执行方式是 Host-Native / Advisor 模式：prompt 落盘在本文件，图片由宿主图像工具生成。

## 总体视觉规范

- 语言：中文主导，少量英文技术名词保留。
- 画幅：16:9 横版。
- 风格：清爽技术产品使用指南、浅色背景、蓝绿主色、少量橙色提示。
- 元素：扁平化 UI 截面、流程箭头、状态标签、清晰标题。
- 禁止：不要画真实品牌 logo，不要使用夸张营销海报风，不要用黑暗模糊背景，不要渲染成代码截图。

## Prompt 1：项目总览

```text
Create a clean Chinese product guide infographic for “ResearchNotebook V1.1 使用指南”.

Canvas: 16:9 horizontal, light background, blue/green primary palette, restrained orange warning accents.

Show a polished product workflow overview with these labeled areas:
1. Workspace
2. Source Library
3. Ask
4. Source Preview Drawer
5. DocumentUnit
6. EvidenceSpan Highlight

Main headline in Chinese:
ResearchNotebook V1.1 使用指南

Subtitle:
从答案 citation 跳转到来源预览、DocumentUnit 与证据高亮

Visual composition:
Left side shows a simplified workspace panel with source cards and an ask box.
Right side shows a drawer UI with source preview, document units list, and highlighted evidence text.
Use small badges: PASS, LIMITED PASS, NOT_READY.

Include a small boundary note:
当前 ready 范围：text / markdown / json 的受限证据导航路径

Do not include real company logos. Do not include tiny unreadable text. Make text crisp and readable.
```

## Prompt 2：证据导航流程

```text
Create a Chinese technical workflow infographic titled “从答案到证据高亮”.

Canvas: 16:9 horizontal, clean white and pale blue background.

Show a left-to-right flow with five large steps:
提问
Answer Citation
Source Preview Drawer
DocumentUnit
EvidenceSpan 高亮

Under the citation step, show the required identifiers:
source_id + unit_id + evidence_id

Use a green success path for supported citations.
Use a gray fallback path for sourceRef only / artifact_ref only.

Important labels:
artifact_ref 只作为 metadata
不解析本地路径
不使用 dangerouslySetInnerHTML

Visual style: modern SaaS documentation graphic, precise, readable, no decorative blobs, no dark theme.
```

## Prompt 3：多格式支持边界

```text
Create a Chinese support matrix infographic titled “V1.1 格式支持边界”.

Canvas: 16:9 horizontal, light background, structured table layout.

Show two columns:
已通过浏览器 smoke
仍为 NOT_READY

In the supported column:
text
markdown
json

For each supported type show:
Preview PASS
DocumentUnit PASS
EvidenceSpan PASS

In the NOT_READY column:
PDF
PPTX
HTML
video
audio

Add boundary notes:
markdown/json 仅代表 workspace query citation path browser-smoke-ready
不代表 all-source-type precise backjump
不代表 native PDF/PPTX/video/audio ingestion

Use green checks for supported rows and red/gray lock icons for NOT_READY rows. Text must be readable.
```

## Prompt 4：手工验收清单

```text
Create a Chinese manual acceptance checklist infographic titled “V1.1 手工验收路径”.

Canvas: 16:9 horizontal, clean checklist board style, light neutral background.

Show seven checklist cards:
1. 启动前端与后端
2. Text workspace citation 高亮
3. Text session citation 高亮
4. Markdown workspace citation 高亮
5. JSON workspace citation 高亮
6. Source Trace scoped path
7. Unsupported fallback 与 cleanup

For each card include a compact checkbox line and a short expected result.

Add a bottom warning band:
禁止扩大 ready 声明：all-session / all-source-type / PDF/PPTX/video/audio / Assessment / Governance / Cloud sync

Style: professional engineering handoff guide, readable Chinese typography, restrained color palette, no cartoon style.
```

## Combined Prompt：四联使用指南图

```text
Create one 16:9 Chinese product guide image composed as a clean 2x2 grid of four panels for “ResearchNotebook V1.1 使用指南”.

Overall style:
Light background, modern SaaS documentation aesthetic, blue and green primary palette, small orange warning accents, crisp readable Chinese text, flat UI illustrations, no logos, no dark blurry background.

Panel 1 title:
项目总览
Content:
Workspace -> Source Library -> Ask -> Source Preview Drawer -> DocumentUnit -> EvidenceSpan Highlight.
Show a simplified app UI with source cards, ask box, and right-side preview drawer.

Panel 2 title:
从答案到证据高亮
Content:
提问 -> Answer Citation -> Source Preview Drawer -> DocumentUnit -> EvidenceSpan 高亮.
Show required identifiers: source_id + unit_id + evidence_id.
Show fallback: sourceRef only / artifact_ref only = metadata only.

Panel 3 title:
格式支持边界
Content:
Supported browser-smoke-ready: text, markdown, json.
Still NOT_READY: PDF, PPTX, HTML, video, audio.
Notes: markdown/json only for workspace query citation path; not all-source-type ready.

Panel 4 title:
手工验收清单
Content:
前后端启动, text workspace, text session, markdown workspace, json workspace, source trace, unsupported fallback, cleanup.
Bottom note:
不声明 Assessment / Governance / Graph editing / Cloud sync ready.

Use large readable headings, compact UI-like labels, clear arrows, and professional product-documentation composition.
```
