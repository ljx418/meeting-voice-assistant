# V1.10-RC Disabled Boundary Acceptance Report

日期：2026-05-31

## 当前状态

`V1_10_DISABLED_BOUNDARY_ACCEPTED`

## 环境记录

| 项 | 值 |
| --- | --- |
| frontend URL | http://127.0.0.1:5173 |
| data_service URL | http://127.0.0.1:8003 |
| browser | chrome-cdp:configured |
| tester | codex |
| timestamp | 2026-05-31T08:01:01.888Z |

## 验收结果

| 项 | 状态 | 说明 |
| --- | --- | --- |
| Phase 2/3 disabled tools visible in Studio source | PASS | 音频概览, PPT 生成, 思维导图, 文档对比 |
| disabled tools do not expose executable button | PASS |  |
| no Phase 2/3 generation route or artifact mutation | PASS |  |
| P0 Markdown/TXT/extractable PDF real data smoke remains PASS_LIMITED | PASS | PDF_EXTRACTED |
| OCR/scanned PDF remains contract-discovery disabled | PASS |  |
| V1.9 RC prerequisite remains ready for human acceptance | PASS |  |
| V1.10 documentation keeps disabled boundary wording | PASS |  |
| browser workspace create | PASS | rn-v10-disabled-1780214458362 |
| browser opened ResearchNotebook workspace | PASS | http://127.0.0.1:5173 |
| browser disabled tools visible and disabled | PASS | 4 disabled buttons |
| browser disabled tool network result | PASS | 4 disabled buttons clicked, no generation request |
| browser artifact list check | PASS | no pseudo Phase 2/3 artifact |
| browser workspace cleanup | PASS | rn-v10-disabled-1780214458362 |
| fixture/report hygiene | PASS | no sensitive path or API key |

## 结论

V1.10 disabled-boundary smoke 证明当前 UI / 文档仍保持后续输出工具 disabled：

- Audio Overview 不生成真实输出。
- PPT generation 不生成真实输出。
- Mindmap 不生成真实输出。
- Document comparison 不生成真实输出。
- 可抽取文本 PDF P0 路径使用既有真实数据 smoke 结果确认未回退。
- OCR / scanned PDF 仍保持 NOT_READY / CONTRACT_DISCOVERY_READY。

## 声明边界

不得声明：

- OCR ready
- scanned PDF ready
- Audio Overview ready
- PPT generation ready
- Mindmap ready
- Document comparison ready
- all-source-type ready
- all websites URL ready
- cloud sync / collaboration ready

## 风险评估

| 风险项 | 评级 | 说明 |
| --- | --- | --- |
| 规格漂移 | LOW | 本轮只验证 disabled boundary，不进入功能实现 |
| 虚假验收 | LOW | 报告保持 NOT_READY / DISABLED_READY，不写成功能 ready |
