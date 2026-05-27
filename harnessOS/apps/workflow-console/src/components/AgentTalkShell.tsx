import { useState, type KeyboardEvent } from "react";
import type { AgentTalkFixture } from "../api/agentTalkTypes.js";
import { safeText } from "../api/redaction.js";
import type { AgentActionHandoff, AgentActionProposal, AgentTalkInteractionState, AgentTalkSession, AgentTalkSuggestion, WorkflowBoard, WorkflowContextSummary, WorkflowEvent } from "../api/types.js";

export interface AgentTalkShellProps {
  fixture?: AgentTalkFixture;
  session?: AgentTalkSession;
  interactionState?: AgentTalkInteractionState | null;
  suggestions?: AgentTalkSuggestion[];
  actionProposals?: AgentActionProposal[];
  board?: WorkflowBoard;
  context?: WorkflowContextSummary | null;
  events?: WorkflowEvent[];
  selectedStationId?: string;
  selectedStationName?: string;
  onSendMessage?: (content: string, context?: { selected_station_id?: string; selected_station_name?: string }) => Promise<void> | void;
  onShowDiff?: (patchId?: string) => void;
  onNavigateToEditing?: () => void;
  onNavigateToEvidenceReview?: () => void;
  onCreateHandoff?: (proposal: AgentActionProposal, targetPanel: AgentActionHandoff["target_panel"]) => Promise<AgentActionHandoff | undefined> | AgentActionHandoff | undefined;
  onDismissSuggestion?: (suggestionId: string) => Promise<void> | void;
  onDismissActionProposal?: (proposalId: string) => Promise<void> | void;
}

export function AgentTalkShell({ fixture, session, interactionState, suggestions = [], actionProposals = [], board, context, events = [], selectedStationId, selectedStationName, onSendMessage, onShowDiff, onNavigateToEditing, onNavigateToEvidenceReview, onCreateHandoff, onDismissSuggestion, onDismissActionProposal }: AgentTalkShellProps) {
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [selectedProposal, setSelectedProposal] = useState<AgentActionProposal | null>(null);
  const fallbackPatchProposal = fixture?.patch_proposal;
  const realMessages = session?.messages || [];
  const realSuggestions = suggestions.length ? suggestions : session?.suggestions || [];
  const visibleSuggestions = realSuggestions.length ? realSuggestions : fallbackSuggestions(fixture);
  const visibleActionProposals = actionProposals.length ? actionProposals : fallbackActionProposals(visibleSuggestions);
  const eventCount = events.length || fixture?.events.length || 0;
  const businessContext = context?.business || fixture?.context_summary.business || {};

  async function submitMessage() {
    const content = draft.trim();
    if (!content || !onSendMessage) {
      return;
    }
    setBusy(true);
    try {
      await onSendMessage(content, { selected_station_id: selectedStationId, selected_station_name: selectedStationName });
      setDraft("");
    } finally {
      setBusy(false);
    }
  }

  function applyQuickPrompt(prompt: string) {
    if (prompt === "查看 Diff") {
      onShowDiff?.(fallbackPatchProposal?.workflow_patch_id);
      return;
    }
    setDraft(prompt);
  }

  async function requestSuggestion(summary: string) {
    const content = `生成建议：${summary}`;
    if (!onSendMessage) {
      setDraft(content);
      return;
    }
    setBusy(true);
    try {
      await onSendMessage(content, { selected_station_id: selectedStationId, selected_station_name: selectedStationName });
    } finally {
      setBusy(false);
    }
  }

  function handleInputKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key !== "Enter" || event.shiftKey) {
      return;
    }
    event.preventDefault();
    void submitMessage();
  }

  return (
    <section className="panel agent-talk-shell" aria-label="画布助手" data-testid="agent-talk-panel">
      <div className="agent-chat-header">
        <div>
          <span className="eyebrow">Canvas Copilot · Agent 工作流助手</span>
          <h2>画布助手</h2>
        </div>
        <span className="status">提案模式</span>
      </div>

      <div className="agent-status-bar" aria-label="画布助手状态">
        <span>当前节点：{safeText(selectedStationName || "文件夹输入")}</span>
        <span data-testid="agent-user-status">{interactionState?.stale_reasons.length ? "存在失效选择，已阻断继续操作" : visibleActionProposals.some((item) => item.workflow_patch_id) ? "草案已生成，等待你查看 Diff 并确认" : "等待你的自然语言需求"}</span>
        <span data-testid="agent-interaction-refresh-generation">状态已刷新</span>
        <span>边界：Agent 只生成建议，不会替你应用、发布或运行。</span>
        {interactionState?.stale_reasons.length ? (
          <p className="operation-message" data-testid="agent-interaction-stale-warning">
            已阻断失效选择，请刷新后重新选择建议。
          </p>
        ) : null}
      </div>

      <div className="agent-conversation agent-message-stream" data-testid="agent-message-list">
        {realMessages.length ? (
          realMessages.map((message) => (
            <div className={`chat-bubble ${message.role === "user" ? "user" : "agent"}`} key={message.message_id}>
              {safeText(message.content)}
            </div>
          ))
        ) : (
          <>
            <div className="chat-bubble user">帮我创建一个工作流，读取 Desktop/技术分享 文件夹，递归解析里面的 md 文件，并为每个子文件夹生成单独总结，最后生成总览总结。</div>
            <div className="chat-bubble agent">
              可以。Agent 只负责建议。我会先生成工作流草案和 Patch proposal，不会自动扫描、发布或运行。你确认后再应用到草稿。
              <div className="agent-action-grid">
                <button type="button" onClick={() => void requestSuggestion("创建本地 Markdown 文件夹总结工作流")}>生成工作流草案</button>
                <button type="button" onClick={() => void requestSuggestion("解释当前文件夹扫描流程")}>解释扫描流程</button>
                <button type="button" onClick={() => void requestSuggestion("修复空文件夹总结规则")}>Agent 生成修复 Proposal</button>
                <button type="button" onClick={() => onNavigateToEditing?.()}>打开 Patch 面板</button>
              </div>
            </div>
          </>
        )}

        <div className="agent-action-proposal-queue" aria-label="Agent action proposal queue" data-testid="agent-action-proposal-queue">
          {visibleActionProposals.map((proposal) => (
            <div className="chat-bubble agent proposal" data-testid="agent-proposal-result-message" key={proposal.proposal_id}>
              <span className="eyebrow">Proposal Result</span>
              <article className="agent-proposal-card" data-testid="agent-action-proposal-card">
                <div className="agent-proposal-head">
                  <strong>{safeText(proposal.title)}</strong>
                  <span className="status">{safeText(proposal.lifecycle)}</span>
                </div>
                <p>{safeText(proposal.summary)}</p>
                {proposal.workflow_patch_id ? (
                  <p className="operation-message">
                    {proposal.intent_type === "show_patch_diff" ? "已生成 Patch，等待用户确认。请查看 Diff 后在编辑面板确认。" : "已生成 Patch，等待用户确认。请打开差异后在编辑面板确认。"}
                  </p>
                ) : null}
                <dl className="agent-proposal-meta">
                  <dt>操作</dt>
                  <dd>{safeText(proposalOperationLabel(proposal))}</dd>
                  <dt>风险</dt>
                  <dd>{safeText(proposal.risk_level)}</dd>
                  <dt>策略</dt>
                  <dd>{safeText(proposal.policy_class)}</dd>
                </dl>
                {proposal.requires_approval ? <em>需要治理审批</em> : null}
                <div className="button-row">
                  <button type="button" onClick={() => setSelectedProposal(proposal)}>查看详情</button>
                  <button type="button" onClick={() => onNavigateToEvidenceReview?.()}>查看治理审计</button>
                  {proposal.workflow_patch_id ? (
                    <button type="button" onClick={() => onShowDiff?.(proposal.workflow_patch_id || undefined)}>
                      {proposal.intent_type === "show_patch_diff" ? "查看 Diff" : "打开 Diff"}
                    </button>
                  ) : null}
                  <button
                    type="button"
                    onClick={() => {
                      if (isReadOnlyIntent(proposal.intent_type)) {
                        if (proposal.workflow_patch_id) {
                          onShowDiff?.(proposal.workflow_patch_id);
                        } else {
                          onNavigateToEvidenceReview?.();
                        }
                        return;
                      }
                      const panel = handoffPanel(proposal.target_panel);
                      if (onCreateHandoff && panel) {
                        void onCreateHandoff(proposal, panel);
                      } else {
                        onNavigateToEditing?.();
                      }
                    }}
                  >
                    {proposalActionLabel(proposal)}
                  </button>
                  {onDismissActionProposal && proposal.lifecycle !== "dismissed" ? (
                    <button type="button" onClick={() => void onDismissActionProposal(proposal.proposal_id)}>忽略建议</button>
                  ) : null}
                </div>
              </article>
            </div>
          ))}
        </div>
      </div>

      {selectedProposal ? (
        <div className="agent-context-card agent-proposal-detail" data-testid="agent-action-proposal-detail">
          <strong>{safeText(selectedProposal.title)}</strong>
          <p>{safeText(selectedProposal.summary)}</p>
          <dl>
            <dt>生命周期</dt>
            <dd>{safeText(selectedProposal.lifecycle)}</dd>
            <dt>策略</dt>
            <dd>{safeText(selectedProposal.policy_class)}</dd>
            <dt>目标面板</dt>
            <dd>{safeText(selectedProposal.target_panel || "read_only")}</dd>
            <dt>风险</dt>
            <dd>{safeText(selectedProposal.risk_flags.join(", ") || selectedProposal.risk_level)}</dd>
          </dl>
          <p className="operation-message">详情仅用于导航和审查，不执行任何 mutation。</p>
        </div>
      ) : null}

      <details className="agent-context-card agent-secondary-panel" data-testid="agent-suggestion-list" open>
        <summary>更多建议与审计入口</summary>
        <div className="suggestion-grid" aria-label="Agent 修改建议">
          {visibleSuggestions.map((suggestion) => (
            <article data-testid="agent-suggestion-card" key={suggestion.suggestion_id}>
              <strong>{safeText(suggestion.title)}</strong>
              <p>{safeText(suggestion.summary)}</p>
              {suggestion.requires_approval ? <em>需要治理审批</em> : null}
              <div className="button-row">
                <button type="button" onClick={() => void requestSuggestion(suggestion.summary)}>生成建议</button>
                <button type="button" onClick={() => onShowDiff?.(suggestion.workflow_patch_id)}>查看 Diff</button>
                <button type="button" onClick={() => onNavigateToEditing?.()}>前往编辑面板</button>
                {onDismissSuggestion && suggestion.status !== "dismissed" ? (
                  <button type="button" onClick={() => void onDismissSuggestion(suggestion.suggestion_id)}>忽略</button>
                ) : null}
              </div>
            </article>
          ))}
        </div>
        <button type="button" onClick={() => onNavigateToEvidenceReview?.()}>查看治理审计</button>
      </details>

      <details className="agent-context-card agent-secondary-panel" data-testid="agent-context-summary">
        <summary>上下文与事件摘要</summary>
        <strong>上下文与事件摘要</strong>
        <p>事件数量：{eventCount}</p>
        <p>业务上下文：{Object.keys(businessContext).length ? "已加载，可用于解释流程" : "暂无业务上下文"}</p>
      </details>

      <details className="agent-context-card agent-secondary-panel" data-testid="agent-developer-diagnostics">
        <summary>开发诊断</summary>
        <p>刷新代次：{safeText(interactionState?.refresh_generation || "local")}</p>
        <p>建议数量：{visibleSuggestions.length}</p>
        <p>Proposal 数量：{visibleActionProposals.length}</p>
      </details>

      <div className="agent-input-area">
        <div className="quick-prompts">
          {["创建本地总结工作流", "解释当前流程", "为什么没有生成总结", "修复空文件夹总结", "查看 Diff"].map((item) => (
            <button type="button" key={item} onClick={() => applyQuickPrompt(item)}>{item}</button>
          ))}
        </div>
        <label>
          <span className="sr-only">Agent 输入</span>
          <textarea
            data-testid="agent-message-input"
            onKeyDown={handleInputKeyDown}
            onChange={(event) => setDraft(event.currentTarget.value)}
            placeholder="请输入你的需求，例如：读取 Desktop/技术分享 并为每个子文件夹生成总结。"
            value={draft}
          />
        </label>
        <button data-testid="agent-send-button" disabled={!draft.trim() || busy || !onSendMessage} type="button" onClick={() => void submitMessage()}>
          {busy ? "发送中…" : "发送"}
        </button>
      </div>
    </section>
  );
}

function proposalOperationLabel(proposal: AgentActionProposal): string {
  if (proposal.workflow_patch_id && proposal.intent_type === "suggest_patch") {
    return "workflow.patch.propose";
  }
  if (proposal.intent_type === "show_patch_diff") {
    return "patch.diff.view";
  }
  return proposal.intent_type;
}

function fallbackActionProposals(suggestions: AgentTalkSuggestion[]): AgentActionProposal[] {
  return suggestions.slice(0, 3).map((suggestion) => ({
    proposal_id: `fixture_action_${suggestion.suggestion_id}`,
    agent_session_id: "fixture_agent_session",
    workflow_instance_id: suggestion.workflow_instance_id,
    workflow_template_id: suggestion.workflow_template_id,
    intent_type: suggestion.action_intent.action,
    policy_class: suggestion.action_intent.action === "suggest_patch" ? "proposal_only" : "display_only",
    lifecycle: "proposed",
    status: "proposed",
    title: suggestion.title,
    summary: suggestion.summary,
    target_panel: suggestion.workflow_patch_id ? "editing" : null,
    workflow_patch_id: suggestion.workflow_patch_id,
    risk_level: suggestion.requires_approval ? "high" : suggestion.risk_flags?.length ? "medium" : "low",
    risk_flags: suggestion.risk_flags || [],
    requires_approval: Boolean(suggestion.requires_approval),
    policy_decision: "proposal_only",
    redaction_status: "redacted",
  }));
}

function targetButtonLabel(target?: AgentActionProposal["target_panel"]): string {
  if (target === "approval") {
    return "前往审批面板";
  }
  if (target === "context") {
    return "前往上下文面板";
  }
  if (target === "quality") {
    return "前往质量面板";
  }
  if (target === "artifact") {
    return "前往产物面板";
  }
  return "前往编辑面板";
}

function proposalActionLabel(proposal: AgentActionProposal): string {
  if (isReadOnlyIntent(proposal.intent_type)) {
    return "查看摘要";
  }
  if (
    proposal.target_panel === "editing" &&
    proposal.title !== "查看 Diff" &&
    proposal.title !== "生成节点调整建议" &&
    proposal.title !== "生成 Prompt 调整建议" &&
    proposal.title !== "生成连线调整建议"
  ) {
    return "前往 Patch 面板";
  }
  return targetButtonLabel(proposal.target_panel);
}

function handoffPanel(target?: AgentActionProposal["target_panel"]): AgentActionHandoff["target_panel"] {
  if (target === "approval") return "approval_panel";
  if (target === "context") return "context_panel";
  if (target === "quality") return "quality_panel";
  if (target === "artifact") return "artifact_panel";
  return "editing_panel";
}

function isReadOnlyIntent(intentType: AgentActionProposal["intent_type"]): boolean {
  return ["explain_workflow", "summarize_events", "summarize_quality", "summarize_context"].includes(intentType);
}

function fallbackSuggestions(fixture?: AgentTalkFixture): AgentTalkSuggestion[] {
  if (!fixture) {
    return [];
  }
  return [
    {
      suggestion_id: "fixture_suggest_patch",
      workflow_instance_id: fixture.workflow_instance_id,
      workflow_template_id: fixture.patch_proposal.workflow_template_id,
      workflow_patch_id: fixture.patch_proposal.workflow_patch_id,
      type: "propose_patch",
      title: "优化 Prompt",
      summary: "生成一个 Patch，增强角色一致性和镜头转场要求。",
      status: "active",
      action_intent: { action: "suggest_patch", executable: false },
      risk_flags: fixture.patch_diff.risk_flags,
      requires_approval: fixture.patch_diff.requires_approval,
      redaction_status: "redacted",
    },
  ];
}
