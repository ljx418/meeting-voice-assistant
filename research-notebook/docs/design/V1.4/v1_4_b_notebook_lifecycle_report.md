# ResearchNotebook V1.4-B Notebook Lifecycle Report

日期：2026-05-26

## 阶段结论

V1.4-B Notebook 生命周期补齐：PASS_LIMITED。

当前已覆盖创建、列表、重命名、归档、最近打开。删除采用后端已有 archive 合同满足 PRD 中“删除或归档”的 MVP 边界，不声明物理删除。

## 已完成内容

- 工作区首页展示工作区列表。
- 创建工作区后进入对应工作区。
- 工作区详情页支持重命名。
- 工作区详情页支持归档。
- 最近打开使用浏览器本地存储记录，并在工作区首页排序展示。
- 最近打开状态只作为本机 convenience 功能，不声明云同步或跨设备同步。

## 未完成内容

- 物理删除工作区未实现。
- 最近打开不跨设备同步。
- 工作区重命名/归档仍依赖 data_service 对应 route。

## 验收记录

| 验收项 | 结果 | 说明 |
| --- | --- | --- |
| 创建 | PASS | 已有 create workspace flow。 |
| 列表 | PASS | 已有 workspace list。 |
| 重命名 | PASS | 前端接入 `workspaces.rename`，失败时显示局部错误。 |
| 删除或归档 | PASS_LIMITED | 使用 archive route；不声明物理删除。 |
| 最近打开 | PASS_LIMITED | 本地浏览器状态，可排序展示；不跨设备。 |
| npm run check | PASS | boundary、lint、117 个测试、build 通过。 |

## 规格漂移评估

风险等级：LOW。

原因：PRD 要求 Notebook 创建、列表、重命名、删除或归档、最近打开；本阶段没有引入额外产品方向，也没有把归档扩大成物理删除。

收敛措施：文档明确“删除或归档”当前由归档满足，物理删除进入后续 backlog。

## 虚假验收评估

风险等级：MEDIUM。

原因：最近打开是本地状态，容易被误读为持久化云端功能。

收敛措施：报告和 gap 文档明确 local-only，不声明跨设备同步。

## 下一阶段审计

下一阶段：V1.4-C Sources P0 导入与解析。

预期工作：

- 审计当前 source create / build / preview route 是否真正支持 PDF / TXT / Markdown。
- TXT / Markdown 可通过浏览器读取文本后提交，但仍需后端索引和引用 smoke。
- PDF 不得只提交元数据就声明 ready；必须有后端文件上传、抽取、preview、citation 合同。
- 解析状态、删除、重命名、失败重试需要真实 UI 和 route 验证。

下一阶段风险初评：

- 规格漂移：MEDIUM。
- 虚假验收：HIGH。

停止条件：如果后续浏览器上传 UX 仍无法把 PDF/TXT/Markdown 可靠送入已验证的后端合同，则 V1.4-C-FE 不能 PASS，只能记录 PASS_LIMITED_FOR_BACKEND_SMOKE。
