# V3.5 Pack / Connector Template Plan

文档状态：V3.5-G planning artifact。

## 1. Goal

提供 Pack / Connector 模板，让新业务不改 Core 即可声明业务能力和外部能力边界。

## 2. Pack Template

目标目录：

```text
templates/pack/
  manifest.json
  workflows/
  skills/
  policies/
  artifact_types/
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
- `metadata.target_version`
- `compatibility_warnings`

Version compatibility：

- `manifest_schema_version` 标识 manifest 文件结构版本。
- `min_harnessos_version` 标识 pack 可运行的最低 harnessOS 版本。
- `target_harnessos_version` 标识模板生成时面向的目标 harnessOS 版本。
- `compatibility_warnings` 用于记录 schema 过旧、connector capability 缺失、artifact kind 不完整等非致命风险。
- `pack.get` / PackAssemblyResult 必须暴露 compatibility warning，不能只返回 assembled/degraded/blocked。

## 3. Connector Template

目标目录：

```text
templates/connector/
  descriptor.json
  health.py
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
- `compatibility_warnings`

## 4. Dummy Acceptance

dummy pack：

- 不改 Core 可被 `pack.list` 发现。
- `pack.get` 返回 assembly status。

dummy connector：

- 不改业务 Gateway 可被 `connector.health` 消费。
- missing dependency 返回 explainable degraded/blocked。

## 5. Tests

- pack manifest schema test
- pack manifest version compatibility test
- connector descriptor schema test
- connector descriptor version compatibility test
- external pack path discovery
- connector health contract
- no-Core-change verification
