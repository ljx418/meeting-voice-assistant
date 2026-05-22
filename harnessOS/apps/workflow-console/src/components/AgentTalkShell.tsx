import { useState } from "react";
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
  selectedStationName?: string;
  onSendMessage?: (content: string) => Promise<void> | void;
  onShowDiff?: (patchId?: string) => void;
  onNavigateToEditing?: () => void;
  onNavigateToEvidenceReview?: () => void;
  onCreateHandoff?: (proposal: AgentActionProposal, targetPanel: AgentActionHandoff["target_panel"]) => Promise<AgentActionHandoff | undefined> | AgentActionHandoff | undefined;
  onDismissSuggestion?: (suggestionId: string) => Promise<void> | void;
  onDismissActionProposal?: (proposalId: string) => Promise<void> | void;
}

export function AgentTalkShell({ fixture, session, interactionState, suggestions = [], actionProposals = [], board, context, events = [], selectedStationName, onSendMessage, onShowDiff, onNavigateToEditing, onNavigateToEvidenceReview, onCreateHandoff, onDismissSuggestion, onDismissActionProposal }: AgentTalkShellProps) {
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const fallbackPatchProposal = fixture?.patch_proposal;
  const realMessages = session?.messages || [];
  const realSuggestions = suggestions.length ? suggestions : session?.suggestions || [];
  const visibleSuggestions = realSuggestions.length ? realSuggestions : fallbackSuggestions(fixture);
  const workflowName = board?.workflow_instance.workflow_template_id || "AI 短视频生成工作流";
  const eventCount = events.length || fixture?.events.length || 0;
  const businessContext = context?.business || fixture?.context_summary.business || {};

  async function submitMessage() {
    const content = draft.trim();
    if (!content || !onSendMessage) {
      return;
    }
    setBusy(true);
    try {
      await onSendMessage(content);
      setDraft("");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel agent-talk-shell" aria-label="Agent 工作流助手" data-testid="agent-talk-panel">
      <div className="agent-hero">
        <div>
          <span className="eyebrow">Agent Copilot</span>
          <h2>Agent 工作流助手</h2>
          <p>通过自然语言理解当前流程、生成建议和 Diff；Agent 只负责建议，执行必须由用户确认。</p>
        </div>
        <span className="status">需要优化</span>
      </div>

      <div className="agent-context-card">
        <dl>
          <dt>当前工作流</dt>
          <dd>{safeText(workflowName)}</dd>
          <dt>当前选中节点</dt>
          <dd>{safeText(selectedStationName || "分镜生成 Agent")}</dd>
          <dt>当前问题</dt>
          <dd>质量、审批、事件和上下文摘要均来自 BFF DTO。</dd>
          <dt>建议状态</dt>
          <dd>{interactionState?.stale_reasons.length ? "存在失效选择" : "等待用户确认"}</dd>
          <dt>刷新代次</dt>
          <dd data-testid="agent-interaction-refresh-generation">{safeText(interactionState?.refresh_generation || "local")}</dd>
        </dl>
        {interactionState?.stale_reasons.length ? (
          <p className="operation-message" data-testid="agent-interaction-stale-warning">
            {safeText(`已阻断失效选择：${interactionState.stale_reasons.join(", ")}`)}
          </p>
        ) : null}
      </div>

      <div className="agent-conversation" data-testid="agent-message-list">
        {realMessages.length ? (
          realMessages.map((message) => (
            <div className={`chat-bubble ${message.role === "user" ? "user" : "agent"}`} key={message.message_id}>
              {safeText(message.content)}
            </div>
          ))
        ) : (
          <>
            <div className="chat-bubble user">帮我生成一个适合 60 秒科幻短片的视频制作工作流。</div>
            <div className="chat-bubble agent">
              我会基于当前 board、context 和 patch DTO 生成建议。建议只会进入 Patch proposal / Diff，等待用户确认。
              <div className="agent-action-grid">
                <button type="button">生成建议</button>
                <button type="button" onClick={() => onShowDiff?.(fallbackPatchProposal?.workflow_patch_id)}>查看 Diff</button>
                <button type="button" onClick={() => onNavigateToEditing?.()}>前往编辑面板</button>
                <button type="button" onClick={() => onNavigateToEvidenceReview?.()}>查看治理审计</button>
	            </div>
            </div>
          </>
        )}
      </div>

      <div className="suggestion-grid" aria-label="Agent 修改建议" data-testid="agent-suggestion-list">
        {visibleSuggestions.map((suggestion) => (
          <article data-testid="agent-suggestion-card" key={suggestion.suggestion_id}>
            <strong>{safeText(suggestion.title)}</strong>
            <p>{safeText(suggestion.summary)}</p>
            {suggestion.requires_approval ? <em>需要治理审批</em> : null}
            <div className="button-row">
              <button type="button">生成建议</button>
              <button type="button" onClick={() => onShowDiff?.(suggestion.workflow_patch_id)}>查看 Diff</button>
              <button type="button" onClick={() => onNavigateToEditing?.()}>前往编辑面板</button>
              {onDismissSuggestion && suggestion.status !== "dismissed" ? (
                <button type="button" onClick={() => void onDismissSuggestion(suggestion.suggestion_id)}>忽略</button>
              ) : null}
            </div>
          </article>
        ))}
      </div>

      <div className="suggestion-grid agent-action-proposal-queue" aria-label="Agent action proposal queue" data-testid="agent-action-proposal-queue">
        {(actionProposals.length ? actionProposals : fallbackActionProposals(visibleSuggestions)).map((proposal) => (
          <article data-testid="agent-action-proposal-card" key={proposal.proposal_id}>
            <strong>{safeText(proposal.title)}</strong>
            <p>{safeText(proposal.summary)}</p>
            <small>{safeText(`${proposal.policy_class} / ${proposal.lifecycle} / ${proposal.risk_level}`)}</small>
            {proposal.requires_approval ? <em>需要治理审批</em> : null}
            <div className="button-row">
              <button type="button">查看详情</button>
              <button type="button" onClick={() => onNavigateToEvidenceReview?.()}>查看治理审计</button>
              {proposal.workflow_patch_id ? (
                <button type="button" onClick={() => onShowDiff?.(proposal.workflow_patch_id || undefined)}>查看 Diff</button>
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
                {targetButtonLabel(proposal.target_panel)}
              </button>
              {onDismissActionProposal && proposal.lifecycle !== "dismissed" ? (
                <button type="button" onClick={() => void onDismissActionProposal(proposal.proposal_id)}>忽略建议</button>
              ) : null}
            </div>
          </article>
        ))}
      </div>

      <div className="agent-inline-diff">
        <div>
          <strong>Patch Proposal</strong>
          <span className="status">等待用户确认</span>
        </div>
        <dl>
          <dt>操作</dt>
          <dd>{safeText(fallbackPatchProposal?.operation || visibleSuggestions.find((item) => item.workflow_patch_id)?.type || "show_patch_diff")}</dd>
          <dt>目标节点</dt>
          <dd>{safeText(selectedStationName || "分镜生成 Agent")}</dd>
          <dt>Before</dt>
          <dd>生成分镜描述</dd>
          <dt>After</dt>
          <dd>{safeText("生成包含角色一致性、镜头转场、时长控制和场景连续性的分镜描述")}</dd>
          <dt>Risk Flags</dt>
          <dd>prompt_change, quality_rule_affected</dd>
        </dl>
        <div className="button-row">
          <button type="button" onClick={() => onShowDiff?.(fallbackPatchProposal?.workflow_patch_id)}>查看 Diff</button>
          <button type="button" onClick={() => onNavigateToEditing?.()}>前往编辑面板</button>
        </div>
      </div>

      <div className="agent-context-card" data-testid="agent-context-summary">
        <strong>上下文与事件摘要</strong>
        <p>事件数量：{eventCount}</p>
        <p>业务上下文：{safeText(JSON.stringify(businessContext))}</p>
      </div>

      <div className="agent-input-area">
        <div className="quick-prompts">
          {["解释当前流程", "优化当前节点", "总结最近事件", "生成建议", "查看 Diff"].map((item) => (
            <button type="button" key={item}>{item}</button>
          ))}
        </div>
        <label>
          <span className="sr-only">Agent 输入</span>
          <textarea
            data-testid="agent-message-input"
            onChange={(event) => setDraft(event.currentTarget.value)}
            placeholder="请输入你的需求，例如：帮我优化当前节点。"
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
