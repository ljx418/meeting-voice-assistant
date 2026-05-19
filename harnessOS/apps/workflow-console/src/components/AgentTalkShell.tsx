import type { AgentTalkFixture } from "../api/agentTalkTypes.js";
import { safeText } from "../api/redaction.js";

export interface AgentTalkShellProps {
  fixture: AgentTalkFixture;
}

export function AgentTalkShell({ fixture }: AgentTalkShellProps) {
  return (
    <section className="panel agent-talk-shell" aria-label="Agent 工作流助手">
      <div className="agent-hero">
        <div>
          <span className="eyebrow">Agent Copilot</span>
          <h2>Agent 工作流助手</h2>
          <p>通过自然语言生成、修改、优化工作流；Agent 只生成建议和 Diff，等待用户确认。</p>
        </div>
        <span className="status">需要优化</span>
      </div>

      <div className="agent-context-card">
        <dl>
          <dt>当前工作流</dt>
          <dd>AI 短视频生成工作流</dd>
          <dt>当前选中节点</dt>
          <dd>分镜生成 Agent</dd>
          <dt>当前问题</dt>
          <dd>质量分 0.64，低于阈值 0.8</dd>
          <dt>建议状态</dt>
          <dd>需要优化</dd>
        </dl>
      </div>

      <div className="agent-conversation">
        <div className="chat-bubble user">
          帮我生成一个适合 60 秒科幻短片的视频制作工作流。
        </div>
        <div className="chat-bubble agent">
          我将为你生成一个 VideoStudio 工作流，包含：需求输入、剧情大纲、脚本生成、分镜生成、图像提示词、视频渲染、质量评估、人工审批和发布输出。
          <div className="agent-action-grid">
            <button type="button">生成工作流草案</button>
            <button type="button">查看节点列表</button>
            <button type="button">应用到画布（预览）</button>
          </div>
        </div>
        <div className="chat-bubble user">分镜质量太低，帮我优化这个节点。</div>
        <div className="chat-bubble agent">
          我发现「分镜生成 Agent」质量分为 0.64，低于阈值 0.8。主要问题是角色一致性不足、镜头衔接不自然。我建议你选择以下方案之一。
        </div>
      </div>

      <div className="suggestion-grid" aria-label="Agent 修改建议">
        <article>
          <strong>重跑本工位</strong>
          <p>不覆盖旧结果，生成新的 storyboard_v2.json。</p>
          <button type="button">查看建议</button>
        </article>
        <article>
          <strong>优化 Prompt</strong>
          <p>生成一个 Patch，增强角色一致性和镜头转场要求。</p>
          <button type="button">查看 Diff</button>
        </article>
        <article>
          <strong>增加质量检查节点</strong>
          <p>在分镜后增加角色一致性检查节点。</p>
          <button type="button">生成 Patch</button>
        </article>
      </div>

      <div className="agent-inline-diff">
        <div>
          <strong>Patch Proposal</strong>
          <span className="status">等待用户确认</span>
        </div>
        <dl>
          <dt>操作</dt>
          <dd>{fixture.patch_proposal.operation}</dd>
          <dt>目标节点</dt>
          <dd>分镜生成 Agent</dd>
          <dt>Before</dt>
          <dd>生成分镜描述</dd>
          <dt>After</dt>
          <dd>{safeText("生成包含角色一致性、镜头转场、时长控制和场景连续性的分镜描述")}</dd>
          <dt>Risk Flags</dt>
          <dd>prompt_change, quality_rule_affected</dd>
        </dl>
        <div className="button-row">
          <button type="button">查看 Diff</button>
          <button type="button" disabled>应用到草稿（后续阶段）</button>
          <button type="button">取消</button>
        </div>
      </div>

      <div className="agent-input-area">
        <div className="quick-prompts">
          {["生成工作流", "优化当前节点", "诊断失败原因", "生成 Patch", "解释当前流程"].map((item) => (
            <button type="button" key={item}>{item}</button>
          ))}
        </div>
        <label>
          <span className="sr-only">Agent 输入</span>
          <textarea readOnly value="请输入你的需求，例如：帮我优化分镜节点，增加人工审批。" />
        </label>
        <button type="button">发送</button>
      </div>
    </section>
  );
}
