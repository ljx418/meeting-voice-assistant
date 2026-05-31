# V1.8-B Agent-Led Source Import Plan

日期：2026-05-30

## 目标

让 Agent 编排 P0/P1 来源导入，而不是依赖用户在弱前端中手动完成。

## 范围

- PDF
- TXT
- Markdown
- limited public URL

## 开发内容

1. Agent 创建 workspace。
2. Agent 扫描授权目录。
3. Agent 过滤文件类型。
4. Agent 导入 Markdown / TXT / PDF。
5. Agent 添加 URL source。
6. Agent 记录 skipped files。
7. Agent 启动 build/index。
8. Agent 轮询状态。
9. Agent 生成 source import report。

## 验收标准

- 目录读取必须经过授权。
- 至少导入一个 Markdown。
- 至少导入一个 TXT。
- 至少导入一个可抽取文本 PDF。
- 至少处理三个 URL，其中一个稳定失败。
- 不支持文件进入 skipped list。
- 每个 skipped item 有 reason。
- 不泄露绝对路径。
- source list 返回 registry source_id。
- build/index 完成。

## 必跑命令

```bash
npm run check
npm run smoke:v1.4-sources-p0
npm run smoke:v1.6-a-url
npm run smoke:v1.8-agent-source-import
```

## 风险

- 规格漂移：MEDIUM。limited URL 不能写成 all websites。
- 虚假验收：MEDIUM。导入成功不代表 citation 可用。

