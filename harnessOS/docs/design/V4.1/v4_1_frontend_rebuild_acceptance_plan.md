# V4.1 Frontend Rebuild Acceptance Plan

Status: active acceptance plan for the Stitch-aligned frontend rebuild.

## Evidence Output

Save stage evidence under:

```text
docs/design/V4.1/acceptance-evidence/frontend-rebuild/
```

Each substage evidence folder should contain:

```text
screenshots/
network-log.json
console-errors.json
result-summary.md
ux-review.md
prd-spec-review.md
```

## Browser Acceptance Path

1. Open Workflow Console.
2. Confirm light five-zone workbench.
3. Open Agent assistant.
4. Enter:

```text
帮我创建一个工作流，读取 Desktop/技术分享 文件夹，递归解析里面的 md 文件，并为每个子文件夹生成单独总结，最后生成总览总结。
```

5. Confirm Agent creates proposal only.
6. Confirm pending / ghost nodes appear.
7. Open Patch Diff.
8. Apply to draft with user confirmation.
9. Confirm 9 formal nodes appear.
10. Select folder input node.
11. Authorize folder read.
12. Debug scan.
13. Confirm scan shows counts and no summaries.
14. Publish with user confirmation.
15. Run with user confirmation.
16. Open run board and confirm 9 node states.
17. Open artifacts and confirm required files.
18. Open quality report and confirm unsupported file and empty folder.
19. Refresh and confirm recovery.
20. Trigger failed parse fixture and rerun current node.
21. Ask Agent debug question and confirm proposal-only behavior.
22. Open governance evidence and confirm read-only chain.

## Required Assertions

Required artifacts:

```text
AgentOS_总结.md
前端低代码_总结.md
项目复盘_总结.md
总览总结.md
quality_report.json
```

Required logical nodes:

```text
folder_input
folder_scan
markdown_filter
markdown_parse
folder_group
per_folder_summary
overview_summary
quality_check
artifact_publish
```

Forbidden browser requests:

```text
/v1/rpc
/v1/events/subscribe
```

Forbidden DOM/network strings:

```text
capability_token
subscription_token
Authorization
Bearer
secret
raw_trace_payload
raw_artifact_content
raw_connector_payload
raw prompt
upstream signed URL
```

Forbidden UI copy:

```text
自动应用
自动发布
Agent 已执行
Agent 已发布
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
```

## Validation Commands

Focused frontend validation:

```bash
cd apps/workflow-console && npm test
cd apps/workflow-console && npm run build
cd apps/workflow-console && npm run test:e2e
```

Optional visible local Chrome validation:

```bash
cd apps/workflow-console && npm run acceptance:workflow-agent-visible:slow
```

Note:

The shell currently does not expose `chromecli` or `chrome-cli` in PATH. The project already provides `chrome-local` Playwright acceptance scripts for the installed local Chrome browser. If a concrete ChromeCLI binary path is provided, add it as a separate acceptance runner without changing the PRD scope.
