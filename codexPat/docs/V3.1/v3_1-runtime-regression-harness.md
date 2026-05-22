# V3.1 Phase 4：Runtime Regression Harness

文档状态：active phase design and acceptance。

## 目标

把当前多猫、多实例路由、`petctl` 和 Manager UI 的关键运行链路整理成一套可重复执行的本地 smoke。

本阶段只验证 runtime / API / CLI，不新增桌宠体验功能，不替代人工视觉验收。

## 运行方式

前置：

- Desktop app 已启动。
- `GET http://127.0.0.1:17321/api/health` 可用。
- `packages/petctl/dist/cli.js` 已构建。

执行：

```bash
node scripts/v3_1_runtime_smoke.mjs
```

脚本会：

- 检查 desktop app 是否启动。
- 读取当前 instance 列表并记录 `preExistingInstanceCount`。
- 创建带唯一 `runId` 的 `Smoke Cat A` / `Smoke Cat B`。
- 验证 instance routing、env routing、legacy route、安全拒绝和 hard limit。
- 只清理本次创建的 Smoke 实例。
- 输出结构化 summary。

## 最小清理接口

为避免 smoke 脚本残留测试猫，本阶段增加最小清理能力：

- `DELETE /api/instances/:instanceId`
- `petctl detach --instance <instanceId>`

边界：

- 必须 Bearer token。
- 只能 detach 非 default instance。
- unknown instance 返回 `instance_not_found`。
- invalid instanceId 返回 `instance_id_invalid`。
- default 返回 `default_instance_cannot_detach`。
- 不打印 token、Authorization header、token 文件路径或 raw payload。

## 覆盖范围

Required runtime cases：

- health API 可用。
- attach A/B。
- `petctl list --json` 能看到 default + A + B。
- `notify --instance A` 只路由到 A。
- `notify --instance B` 只路由到 B。
- `AGENT_DESKTOP_PET_INSTANCE_ID=A` 时 notify 无 `--instance` 进入 A。
- env=A 但 `--instance=B` 时显式 `--instance` 优先。
- legacy notify 只影响 default route，不影响 A/B。
- unknown instance 返回 `404 instance_not_found`。
- invalid instanceId 返回安全错误。
- `AGENT_DESKTOP_PET_INSTANCE_ID=not-found` 不 fallback default。
- invalid sound path 被拒绝且不回显敏感输入。
- hard limit 到 12 只后第 13 只失败或被拒绝。
- detach 临时实例并确认 list 中不再出现。
- detach 后 notify 返回 `404 instance_not_found`。

## 安全边界

脚本 summary 不得包含：

- `AGENT_DESKTOP_PET_TOKEN=`
- `Authorization: Bearer`
- `api-token.json`
- `Application Support`
- `raw payload`
- `../../x.wav`
- `file://`
- `/Users/`

脚本不得：

- 删除、隐藏、重命名用户已有实例。
- 启动 GUI 自动视觉判断。
- 声明 Phase 3 人工验收完成。

## 证据

- `docs/V3.1/evidence/runtime-regression-harness-2026-05-21.md`

完成后最多声明：

```text
V3.1 Phase 4 complete: repeatable runtime regression smoke ready.
```
