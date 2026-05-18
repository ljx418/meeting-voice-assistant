import { ConsoleShell } from "./components/ConsoleShell.js";
import { useWorkflowConsoleDemo } from "./hooks/useWorkflowConsoleDemo.js";

export function App() {
  const demo = useWorkflowConsoleDemo();
  return (
    <ConsoleShell
      workflows={demo.workflows}
      versions={demo.versions}
      instances={demo.instances}
      selectedWorkflowId={demo.selectedWorkflowId}
      selectedVersionId={demo.selectedVersionId}
      selectedInstanceId={demo.selectedInstanceId}
      board={demo.board}
      status={demo.status}
      events={demo.events}
      patchProposal={demo.patchProposal}
      patchDiff={demo.patchDiff}
      highRiskPatchDiff={demo.highRiskPatchDiff}
      agentTalkFixture={demo.agentTalkFixture}
      onWorkflowChange={demo.setSelectedWorkflowId}
      onVersionChange={demo.setSelectedVersionId}
      onInstanceChange={demo.setSelectedInstanceId}
    />
  );
}
