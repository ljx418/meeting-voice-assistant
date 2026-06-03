# V5-5 API / SDK Compatibility Model

文档状态：V5-5 core slice implemented for review。

## Compatibility Fields

```text
sdk_name
sdk_version
api_version
compatibility_status
deprecated_at
sunset_at
migration_guide_ref
```

## Rules

```text
breaking changes require migration guide
SDK cannot expose raw capability token in repr/log
browser SDK cannot call /v1/rpc directly
browser SDK cannot call /v1/events/subscribe directly
```
