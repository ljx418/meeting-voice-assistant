# V2.16 Phase 78 开发计划：Runtime Profile Manager

## 1. 阶段定位

Phase 78 在 V2.13 allowlisted runtime command 基础上增加 profile 层。用户不直接运行任意命令，而是选择系统生成的 profile，并获得 passed / failed / timeout / blocked 等结构化结果。

## 2. In Scope

- 生成 runtime profiles registry。
- profile 来源于已验收 allowlisted commands。
- profile run 必须通过 profile_id 执行。
- 非 profile 命令 blocked。
- run artifact 记录 redacted logs、status、error、linked profile。
- HTTP / MCP / CLI build/read/run/result。

## 3. Out of Scope

- 任意 shell 命令。
- 网络访问。
- 修改源码。
- git commit / push / reset / restore。

## 4. Artifact

```text
workspace/assets/codebase/{codebase_id}/coding_agent/v2_16/runtime_profiles/
  profiles.json
  runs/{profile_run_id}.json
```

## 5. 出门条件

- profiles 非空或结构化 `NO_RUNTIME_PROFILES`。
- non-profile run blocked。
- allowlisted profile run 可产生 redacted artifact。
- HTTP / MCP / CLI parity 通过。
- V2.13 runtime regression 不退化。
