import { ConsoleShell } from "./components/ConsoleShell.js";
import { useWorkflowConsoleData } from "./hooks/useWorkflowConsoleData.js";

export function App() {
  const data = useWorkflowConsoleData();
  if (data.loading) {
    return <div className="console-state">正在连接真实工作流数据…</div>;
  }
  if (data.error) {
    return (
      <div className="console-state error-state">
        <strong>真实数据连接失败</strong>
        <span>{data.error}</span>
      </div>
    );
  }
  if (data.empty || !data.board || !data.status) {
    return <div className="console-state">暂无可展示的工作流实例</div>;
  }
  return (
    <ConsoleShell
      workflows={data.workflows}
      versions={data.versions}
      instances={data.instances}
      selectedWorkflowId={data.selectedWorkflowId}
      selectedVersionId={data.selectedVersionId}
      selectedInstanceId={data.selectedInstanceId}
      board={data.board}
      status={data.status}
      approvals={data.approvals}
      quality={data.quality}
      context={data.context}
      events={data.mode === "demo" ? data.events : data.events}
      patchProposal={data.patchProposal}
      patchDiff={data.patchDiff}
      highRiskPatchDiff={data.highRiskPatchDiff}
      agentTalkFixture={data.agentTalkFixture}
      modeLabel={data.mode === "demo" ? "Demo / Fixture" : undefined}
      eventState={data.eventState}
      onWorkflowChange={data.setSelectedWorkflowId}
      onVersionChange={data.setSelectedVersionId}
      onInstanceChange={data.setSelectedInstanceId}
      onApprovalRespond={data.respondApproval}
      onSetBusinessValue={data.setBusinessContextValue}
      onEmitBusinessEvent={data.emitBusinessEvent}
    />
  );
}
