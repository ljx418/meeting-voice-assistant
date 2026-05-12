# V3.5 Pack / Connector Template Plan

文档状态：V3.5-G implementation baseline。

## 1. Goal

提供 Pack / Connector 模板，让新业务不改 Core 即可声明业务能力和外部能力边界。

V3.5-G 明确区分 template 与 runtime instance：

- `templates/pack` 和 `templates/connector` 是可复制模板，不是运行时实例。
- `pack.list` / `connector.health` 不应自动发现 templates 目录。
- 模板文件必须声明 `metadata.template=true`，loader 遇到该标记时跳过，避免误把模板当实例。
- 被 registry 发现的必须是由模板实例化出来的 pack / connector，例如 `tests/fixtures/v3_5/dummy_pack` 和 `tests/fixtures/v3_5/dummy_connector`。
- dummy pack / connector 必须通过 external pack path / connector descriptor path 显式注入。
- 不允许在 `core/packs/registry.py`、`apps/gateway/connectors.py` 或 `GatewayService` 默认注册表硬编码 dummy id。

## 2. Pack Template

目标目录：

```text
templates/pack/
  manifest.json
  workflows/
  skills/
  policies/
  artifact_kinds/
  examples/
```

manifest 必须声明：

- `name`
- `domain`
- `version`
- `manifest_schema_version`
- `min_harnessos_version`
- `target_harnessos_version`
- `workflows`
- `workflow_dsl`
- `skills`
- `policy_bundles`
- `connectors`
- `connector_capabilities`
- `artifact_kinds`
- `artifact_schemas`
- `metadata`

Version compatibility：

- `manifest_schema_version` 标识 manifest 文件结构版本。
- `min_harnessos_version` 标识 pack 可运行的最低 harnessOS 版本。
- `target_harnessos_version` 标识模板生成时面向的目标 harnessOS 版本。
- `compatibility_warnings` 不由 manifest 自声明为事实；loader / assembly result 根据 schema/version/dependency 状态生成。
- `pack.get` / PackAssemblyResult 暴露 compatibility warnings，不能只返回 assembled/degraded/blocked。

字段兼容规则：

- 不在 G 阶段发明与当前 PackRegistry 不兼容的新 schema。
- `pack_id` 如需出现，只能作为 alias/metadata，不替代 `name/domain`。
- `app_id` 不作为 Pack 必填字段；如需 App 约束，使用 `app_scope` 或 `compatible_app_ids`。
- `policies` 统一为 `policy_bundles`。
- `artifact_types` 统一为 `artifact_kinds` / `artifact_schemas`。

## 3. Connector Template

目标目录：

```text
templates/connector/
  descriptor.json
  health.py
  tools.py
  README.md
  tests/
```

descriptor 必须声明：

- `connector_id`
- `domain`
- `descriptor_schema_version`
- `min_harnessos_version`
- `target_harnessos_version`
- `kind`
- `app_scope`
- `capabilities`
- `execution_mode`
- `trust_level`
- `config_ref`
- `secret_ref`
- `allowed_commands`
- `allowed_paths`
- `allowed_network_hosts`
- `network_policy`
- `requires_approval_for`
- `security`
- `metadata`

Connector discovery 只读取 `descriptor.json`：

- 不自动 import 或执行 `health.py` / `tools.py`。
- `health.py` / `tools.py` 只作为开发示例。
- dummy connector 使用 `execution_mode=stub` 和 `health.mode=static`。
- missing dependency 返回 blocked/degraded envelope，而不是 ImportError/path exception。
- `compatibility_warnings` 不由 descriptor 自声明为事实；loader / health result 生成。

Version compatibility：

- 当前 harnessOS version 来源为 `core/protocol/version.py`。
- unsupported schema version -> blocked。
- `min_harnessos_version` 高于当前版本 -> blocked。
- `target_harnessos_version` 不匹配 -> degraded + compatibility warning。
- optional dependency missing -> degraded。
- required dependency missing -> blocked。

## 4. Dummy Acceptance

dummy pack：

- 只有通过 external pack path 显式注入后，才可被 `pack.list` / `pack.get` 发现。
- `pack.get` 返回 assembly status。

dummy connector：

- 只有通过 external descriptor path 显式注入后，才可被 `connector.health` 消费。
- missing dependency 返回 explainable degraded/blocked。
- templates 目录本身不会被自动发现。

## 5. Tests

- pack manifest schema test
- pack manifest version compatibility test
- connector descriptor schema test
- connector descriptor version compatibility test
- external pack path discovery
- external connector descriptor path discovery
- connector health contract
- no-Core-change verification
- templates not auto-discovered
- blocked/degraded envelope shape
- platform neutrality: no meeting/knowledge/data_service/voice_service/funasr dependencies
