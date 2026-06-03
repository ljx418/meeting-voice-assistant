import type { Meta, StoryObj } from "@storybook/react";
import { ArtifactCard, Button, EmptyState, ErrorState, EvidenceCard, Panel, QualityBadge, StatusBadge, Tabs } from "./BaseComponents.js";
import "../../design-system/tokens.css";
import "../../design-system/components.css";

function ComponentGallery() {
  return (
    <main style={{ background: "var(--hos-bg-page)", minHeight: "100vh", padding: "var(--hos-space-6)" }}>
      <Panel title="基础组件库">
        <div style={{ display: "grid", gap: "var(--hos-space-4)" }}>
          <div style={{ display: "flex", gap: "var(--hos-space-2)", flexWrap: "wrap" }}>
            <Button variant="primary">主按钮</Button>
            <Button variant="secondary">次按钮</Button>
            <Button variant="ghost">文本按钮</Button>
            <Button variant="danger">危险按钮</Button>
            <Button disabled>不可用</Button>
            <Button loading>加载</Button>
          </div>
          <Tabs activeId="artifacts" items={["events", "trace", "artifacts", "quality", "approval", "patch", "evidence"].map((id) => ({ id, label: id }))} />
          <div style={{ display: "flex", gap: "var(--hos-space-2)", flexWrap: "wrap" }}>
            <StatusBadge status="pending" />
            <StatusBadge status="running" />
            <StatusBadge status="completed" />
            <StatusBadge status="failed" />
            <StatusBadge status="waiting_approval" />
            <StatusBadge status="ghost" />
            <StatusBadge status="stale" />
            <QualityBadge status="passed" />
            <QualityBadge status="warning" />
            <QualityBadge status="failed" />
          </div>
          <div style={{ display: "grid", gap: "var(--hos-space-3)", gridTemplateColumns: "repeat(2, minmax(0, 1fr))" }}>
            <ArtifactCard kind="Markdown" name="AgentOS_总结.md" summary="包含内容概览、核心主题、关键知识点和引用文件。" />
            <EvidenceCard handoffId="handoff_001" operationType="workflow.folder_summary.apply" policyDecision="user_confirmed_only" proposalId="proposal_001" redactionStatus="redacted" />
            <EmptyState title="暂无运行数据" message="运行工作流后，这里会显示节点状态和产物。" />
            <ErrorState title="连接失败" message="请检查本地 BFF 服务是否启动。" />
          </div>
        </div>
      </Panel>
    </main>
  );
}

const meta = {
  title: "Components/Base",
  component: ComponentGallery,
} satisfies Meta<typeof ComponentGallery>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Gallery: Story = {};
