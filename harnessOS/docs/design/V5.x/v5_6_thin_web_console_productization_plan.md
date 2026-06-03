# V5-6 Thin Web Console Productization Plan

文档状态：V5-6 implementation planning。

## Productization Path

```text
stabilize shell navigation
surface tenant/workspace/app context
open Runtime Report
open Evidence Chain
request audit export
manage external app entries
show manual confirmation dialogs
```

## Acceptance Rules

```text
browser does not call /v1/rpc directly
browser does not call /v1/events/subscribe directly
manual confirmation is explicit
read-only panels do not show execution buttons
```

