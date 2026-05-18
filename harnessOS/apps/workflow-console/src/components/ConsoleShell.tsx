import { useState } from "react";
import type { AgentTalkFixture } from "../api/agentTalkTypes.js";
import type {
  WorkflowBoard,
  WorkflowEvent,
  WorkflowInstanceSummary,
  WorkflowPatchDiff,
  WorkflowPatchProposal,
  WorkflowStatus,
  WorkflowSummary,
  WorkflowVersionSummary,
} from "../api/types.js";
import { AgentTalkShell } from "./AgentTalkShell.js";
import { EventFeed } from "./EventFeed.js";
import { StationBoard } from "./StationBoard.js";
import { WorkflowEditingPanel } from "./WorkflowEditingPanel.js";
import { WorkflowHeader } from "./WorkflowHeader.js";

export interface ConsoleShellProps {
  workflows: WorkflowSummary[];
  versions: WorkflowVersionSummary[];
  instances: WorkflowInstanceSummary[];
  selectedWorkflowId: string;
  selectedVersionId: string;
  selectedInstanceId: string;
  board: WorkflowBoard;
  status: WorkflowStatus;
  events: WorkflowEvent[];
  patchProposal?: WorkflowPatchProposal;
  patchDiff?: WorkflowPatchDiff;
  highRiskPatchDiff?: WorkflowPatchDiff;
  agentTalkFixture?: AgentTalkFixture;
  onWorkflowChange: (value: string) => void;
  onVersionChange: (value: string) => void;
  onInstanceChange: (value: string) => void;
}

export function ConsoleShell(props: ConsoleShellProps) {
  const [selectedRunId, setSelectedRunId] = useState(props.board.stations[0]?.runs[0]?.station_run_id || "");
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);
  const [rightTab, setRightTab] = useState<"inspector" | "agent">("inspector");
  const [bottomTab, setBottomTab] = useState<"events" | "trace" | "artifacts" | "quality" | "approvals" | "patch">("events");
  const selectedStation = props.board.stations.find((station) => station.runs.some((run) => run.station_run_id === selectedRunId));
  const selectedRun = selectedStation?.runs.find((run) => run.station_run_id === selectedRunId);
  const artifacts = selectedRun?.output_artifacts || selectedStation?.output_artifacts || props.board.artifacts || [];
  const shellClass = ["console-shell", leftCollapsed ? "left-collapsed" : "", rightCollapsed ? "right-collapsed" : ""].join(" ");

  return (
    <div className={shellClass}>
      <WorkflowHeader
        workflows={props.workflows}
        versions={props.versions}
        instances={props.instances}
        status={props.status}
        selectedWorkflowId={props.selectedWorkflowId}
        selectedVersionId={props.selectedVersionId}
        selectedInstanceId={props.selectedInstanceId}
        onWorkflowChange={props.onWorkflowChange}
        onVersionChange={props.onVersionChange}
        onInstanceChange={props.onInstanceChange}
      />
      <main className="console-content">
        <aside className="left-rail" aria-label="节点库">
          <button className="collapse-button" type="button" onClick={() => setLeftCollapsed((value) => !value)}>
            {leftCollapsed ? "展开节点库" : "折叠节点库"}
          </button>
          <div className="rail-content">
            <span className="eyebrow">Node Library</span>
            <h2>节点库</h2>
            <p className="muted">拖拽节点到画布，快速搭建工作流</p>
            <input className="node-search" placeholder="搜索节点" aria-label="搜索节点" />
            <div className="filter-tabs">
              <span className="status">全部</span>
              <span className="status">常用</span>
              <span className="status">VideoStudio</span>
              <span className="status">自定义</span>
            </div>
            <div className="node-category">
              <strong>输入节点</strong>
              {["用户输入", "文件输入", "表单输入", "Webhook 输入", "数据源输入"].map((name) => (
                <button className="library-node" draggable key={name} type="button"><span>{name}</span><small>接收或读取工作流输入</small></button>
              ))}
            </div>
            <div className="node-category">
              <strong>AI Agent 节点</strong>
              {["Planner Agent", "Script Writer Agent", "Director Agent", "Reviewer Agent", "多 Agent 协作"].map((name) => (
                <button className="library-node" draggable key={name} type="button"><span>{name}</span><small>编排推理、生成与审查任务</small></button>
              ))}
            </div>
            <div className="node-category">
              <strong>VideoStudio 推荐节点</strong>
              {["剧情大纲生成", "脚本生成", "分镜生成", "视频渲染", "视频质量评估", "发布输出"].map((name) => (
                <button className="library-node" draggable key={name} type="button"><span>{name}</span><small>推荐 · 视频工作流</small></button>
              ))}
            </div>
            <div className="node-category">
              <strong>质量与治理节点</strong>
              {["质量评估", "一致性检查", "安全检查", "人工审批", "条件审批"].map((name) => (
                <button className="library-node" draggable key={name} type="button"><span>{name}</span><small>治理、质量与审批控制</small></button>
              ))}
            </div>
          </div>
        </aside>
        <StationBoard stations={props.board.stations} onSelectRun={setSelectedRunId} />
        <aside className="right-rail" aria-label="节点配置">
          <button className="collapse-button" type="button" onClick={() => setRightCollapsed((value) => !value)}>
            {rightCollapsed ? "展开检查器" : "折叠检查器"}
          </button>
          <div className="rail-content inspector-stack">
            <span className="eyebrow">Inspector</span>
            <div className="inspector-tabs">
              <button className={rightTab === "inspector" ? "active" : ""} type="button" onClick={() => setRightTab("inspector")}>节点配置</button>
              <button className={rightTab === "agent" ? "active" : ""} type="button" onClick={() => setRightTab("agent")}>Agent 助手</button>
            </div>
            {rightTab === "inspector" ? (
              <section className="panel selected-node">
                <h2>{selectedStation?.station.name || "未选择节点"}</h2>
                <p className="muted">{selectedRun?.status || "选择画布节点查看运行详情"}</p>
                <div className="inspector-form">
                  <label>节点名称<input disabled value={selectedStation?.station.name || ""} readOnly /></label>
                  <label>Agent 角色<input disabled value={selectedStation?.station.role || ""} readOnly /></label>
                  <label>输入合同<input disabled value={selectedRun?.input_artifacts?.[0]?.name || "待绑定"} readOnly /></label>
                  <label>输出合同<input disabled value={artifacts[0]?.name || "待生成"} readOnly /></label>
                  <label>质量规则<input disabled value="visual_consistency >= 0.8" readOnly /></label>
                </div>
              </section>
            ) : props.agentTalkFixture ? <AgentTalkShell fixture={props.agentTalkFixture} /> : null}
          </div>
        </aside>
      </main>
      <section className="bottom-run-panel" aria-label="运行观察区">
        <div className="bottom-tabs">
          {(["events", "trace", "artifacts", "quality", "approvals", "patch"] as const).map((tab) => (
            <button className={bottomTab === tab ? "active" : ""} key={tab} type="button" onClick={() => setBottomTab(tab)}>
              {({ events: "事件", trace: "Trace", artifacts: "产物", quality: "质量", approvals: "审批", patch: "Patch" } as const)[tab]}
            </button>
          ))}
        </div>
        <div className="bottom-content">
          {bottomTab === "events" ? <EventFeed events={props.events} /> : null}
          {bottomTab === "trace" ? <pre>{props.board.trace_summary?.summary || props.board.trace_summary?.trace_id}</pre> : null}
          {bottomTab === "artifacts" ? <pre>{artifacts.map((artifact) => artifact.name || artifact.artifact_id).join("\n")}</pre> : null}
          {bottomTab === "quality" ? <pre>{props.board.quality_evaluations?.map((quality) => `${quality.evaluation_id} ${quality.status} ${quality.score ?? ""}`).join("\n")}</pre> : null}
          {bottomTab === "approvals" ? <pre>{props.board.approvals?.map((approval) => `${approval.approval_id} ${approval.status}`).join("\n")}</pre> : null}
          {bottomTab === "patch" && props.patchProposal && props.patchDiff ? (
            <WorkflowEditingPanel proposal={props.patchProposal} diff={props.patchDiff} highRiskDiff={props.highRiskPatchDiff} />
          ) : null}
        </div>
      </section>
    </div>
  );
}
