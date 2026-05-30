import { Bot, CheckCircle2, FileText, FolderSearch, Play, Workflow } from 'lucide-react';
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { dataServiceClient, isNormalizedApiError } from '../api/dataServiceClient';
import { isEvidenceSpanNavigationSupported, useCapabilitiesQuery } from '../api/workspaceM2Queries';
import type { AgentWorkflowDraftResponse, AnswerEvidence, EvidenceRef, FolderSummaryWorkflowRunResponse } from '../types/api';
import { StateBlock } from './StateBlock';

type AgentWorkflowPanelProps = {
  workspaceId: string;
  onNavigateEvidence?: (evidence: AnswerEvidence) => void;
};

function isJumpableSummaryEvidence(ref: EvidenceRef) {
  return Boolean(ref.evidence_status === 'source_unit_span' && ref.source_id && ref.unit_id && ref.evidence_id);
}

function evidenceStatusLabel(ref: EvidenceRef, canJump: boolean) {
  if (canJump) return '可打开原文定位';
  if (ref.evidence_status === 'relative_path_only') return '仅显示文件路径';
  return '暂不能定位';
}

function workflowStepLabel(name: string) {
  const labels: Record<string, string> = {
    scan_folder: '扫描授权目录',
    extract_text: '读取 Markdown 和文本',
    group_by_subfolder: '按子文件夹分组',
    create_sources: '登记来源文档',
    summarize_folder: '生成子文件夹总结',
    generate_index_report: '生成根目录总览',
    write_artifacts: '保存总结产物'
  };
  return labels[name] ?? name;
}

function workflowStatusLabel(status: string) {
  const labels: Record<string, string> = {
    pending: '待执行',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    skipped: '已跳过',
    draft: '草案',
    awaiting_approval: '等待确认'
  };
  return labels[status] ?? status;
}

function permissionLabel(permission: string) {
  const labels: Record<string, string> = {
    'folder:scan': '扫描目录',
    'folder:extract:md_txt': '读取 Markdown 和文本'
  };
  return labels[permission] ?? permission;
}

function workflowNameLabel(name: string, templateId?: string) {
  if (templateId === 'folder_summary_v1' || name === 'Folder Summary V1') return '文件夹总结工作流';
  return name;
}

function SummaryEvidenceRefs({
  artifactId,
  evidenceRefs,
  preciseNavigationEnabled,
  onNavigateEvidence
}: {
  artifactId: string;
  evidenceRefs: EvidenceRef[];
  preciseNavigationEnabled: boolean;
  onNavigateEvidence?: (evidence: AnswerEvidence) => void;
}) {
  if (evidenceRefs.length === 0) return <p className="workspace-meta">证据引用：0。</p>;

  return (
    <div className="evidence-list" aria-label="总结证据引用">
      {evidenceRefs.slice(0, 8).map((ref, index) => {
        const canJump = Boolean(preciseNavigationEnabled && onNavigateEvidence && isJumpableSummaryEvidence(ref));
        const label = ref.source_title ?? ref.relative_path ?? ref.source_id ?? ref.file_id ?? `证据 ${index + 1}`;
        return (
          <button
            className="evidence-chip"
            key={`${ref.source_id ?? ref.file_id ?? 'evidence'}-${ref.unit_id ?? index}-${ref.evidence_id ?? index}`}
            data-testid={canJump ? 'summary-artifact-evidence-citation' : undefined}
            type="button"
            disabled={!canJump}
            title={canJump ? '打开总结证据定位' : '该证据暂时只能作为来源说明展示。'}
            onClick={() => {
              if (!canJump || !ref.source_id) return;
              onNavigateEvidence?.({
                evidenceKey: `${artifactId}-${index}`,
                sourceId: ref.source_id,
                sourceTitle: ref.source_title ?? ref.relative_path,
                traceAvailable: true,
                snippet: ref.snippet,
                unitId: ref.unit_id,
                evidenceId: ref.evidence_id
              });
            }}
          >
            <span>{label}</span>
            {ref.snippet ? <small>{ref.snippet}</small> : null}
            {ref.unit_id ? <small>文档单元：{ref.unit_id}</small> : null}
            {ref.evidence_id ? <small>证据片段：{ref.evidence_id}</small> : null}
            <small>{evidenceStatusLabel(ref, canJump)}</small>
          </button>
        );
      })}
      {evidenceRefs.length > 8 ? <p className="workspace-meta">另有 {evidenceRefs.length - 8} 条证据引用未展开。</p> : null}
    </div>
  );
}

export function AgentWorkflowPanel({ workspaceId, onNavigateEvidence }: AgentWorkflowPanelProps) {
  const [userGoal, setUserGoal] = useState('递归总结 Desktop/技术分享，每个子文件夹生成一份总结。');
  const [authorizedRoot, setAuthorizedRoot] = useState('Desktop/技术分享');
  const [draft, setDraft] = useState<AgentWorkflowDraftResponse | null>(null);
  const [runResult, setRunResult] = useState<FolderSummaryWorkflowRunResponse | null>(null);
  const capabilitiesQuery = useCapabilitiesQuery(workspaceId);
  const preciseNavigationEnabled = isEvidenceSpanNavigationSupported(capabilitiesQuery.data);

  const createDraft = useMutation({
    mutationFn: () => dataServiceClient.agentWorkflows.createDraft(workspaceId, { user_goal: userGoal }),
    onSuccess: (result) => {
      setDraft(result);
      const rootHint = result.workflow?.draft_parameters?.authorized_root_hint;
      if (rootHint) setAuthorizedRoot(rootHint);
    }
  });

  const runWorkflow = useMutation({
    mutationFn: (mode: 'dry-run' | 'confirmed') =>
      dataServiceClient.folderSummaryWorkflows.startRun(workspaceId, {
        authorized_root: authorizedRoot,
        permission_grant_id: `ui-grant-${Date.now()}`,
        dry_run: mode === 'dry-run',
        confirm_extract: mode === 'confirmed',
        recursive: true,
        include_extensions: ['.md', '.txt'],
        exclude_globs: ['**/*.tmp'],
        max_depth: 16,
        follow_symlinks: false
      }),
    onSuccess: setRunResult
  });

  const workflowError = createDraft.error ?? runWorkflow.error;
  const errorMessage = workflowError
    ? isNormalizedApiError(workflowError)
      ? workflowError.message
      : '工作流请求失败。'
    : null;
  const steps = runResult?.workflow.steps ?? [];
  const artifacts = runResult?.run.artifacts ?? [];
  const draftSteps = draft?.workflow?.steps ?? [];

  return (
    <section className="panel agent-workflow-panel" aria-labelledby="agent-workflow-title">
      <div className="panel-header">
        <div>
          <div className="eyebrow">智能研究助手</div>
          <h2 id="agent-workflow-title">文件夹总结工作流</h2>
        </div>
      </div>
      <div className="panel-body page-grid">
        <div className="agent-hero">
          <div>
            <h3>把一个资料文件夹整理成可追溯的研究总结</h3>
            <p>
              输入目标后，系统会先生成工作流草案。你确认授权目录后，才会扫描 Markdown 和文本文件、生成总览与子文件夹总结。
            </p>
          </div>
          <span className="state-pill state-ready">受限可用</span>
        </div>

        <StateBlock title="授权边界">
          生成草案不会读取本地目录；预览扫描只返回文件清单；确认生成总结后才读取 Markdown 和文本内容。界面只展示相对路径，不展示本机绝对路径。
        </StateBlock>

        <div className="form-grid">
          <label className="wide-field">
            任务指令
            <textarea
              className="text-area"
              value={userGoal}
              onChange={(event) => setUserGoal(event.target.value)}
              placeholder="递归总结 Desktop/技术分享，每个子文件夹生成一份总结。"
              aria-label="任务指令"
            />
          </label>
          <label>
            授权目录
            <input
              value={authorizedRoot}
              onChange={(event) => setAuthorizedRoot(event.target.value)}
              placeholder="Desktop/技术分享"
              aria-label="授权目录"
            />
          </label>
          <div className="toolbar-row">
            <button
              className="secondary-button"
              type="button"
              onClick={() => createDraft.mutate()}
              disabled={createDraft.isPending || runWorkflow.isPending || !userGoal.trim()}
            >
              <Bot size={16} aria-hidden="true" />
              生成工作流草案
            </button>
            <button
              className="secondary-button"
              type="button"
              onClick={() => runWorkflow.mutate('dry-run')}
              disabled={createDraft.isPending || runWorkflow.isPending || !authorizedRoot.trim()}
            >
              <FolderSearch size={16} aria-hidden="true" />
              扫描目录
            </button>
            <button
              className="primary-button"
              type="button"
              onClick={() => runWorkflow.mutate('confirmed')}
              disabled={createDraft.isPending || runWorkflow.isPending || !authorizedRoot.trim()}
            >
              <Play size={16} aria-hidden="true" />
              确认并生成总结
            </button>
          </div>
        </div>

        {createDraft.isPending ? <StateBlock title="正在生成草案">正在匹配可用的文件夹总结模板，不会执行本地文件操作。</StateBlock> : null}
        {runWorkflow.isPending ? <StateBlock title="工作流运行中">正在扫描目录、整理文件并生成研究总结。</StateBlock> : null}
        {errorMessage ? (
          <StateBlock title="工作流失败" tone="error">
            {errorMessage}
          </StateBlock>
        ) : null}

        {draft?.workflow ? (
          <article className="source-card" aria-label="工作流草案">
            <div>
              <div className="source-title-row">
                <h3>{draft.workflow.name}</h3>
                <span className="state-pill state-idle">等待用户确认</span>
              </div>
              <p className="workspace-meta">
                需要权限：{draft.workflow.required_permissions.map(permissionLabel).join('、') || '无'}；预计步骤：{draftSteps.length}
              </p>
              <p className="workspace-meta">
                目录提示：{draft.workflow.draft_parameters?.authorized_root_hint ?? '未提供'}。草案不会自动运行，也不会授权读取文件夹。
              </p>
            </div>
            <Bot size={18} aria-hidden="true" />
          </article>
        ) : null}

        {runResult ? (
          <div className="source-list" aria-label="工作流运行结果">
            <article className="source-card">
              <div>
                <div className="source-title-row">
                  <h3>{workflowNameLabel(runResult.workflow.name, runResult.workflow.template_id)}</h3>
                  <span className="state-pill state-ready">{runResult.run.dry_run ? '已生成扫描预览' : '总结已生成'}</span>
                </div>
                <p className="workspace-meta">
                  文件 {runResult.run.run_report?.manifest_file_count ?? 0}，跳过 {runResult.run.run_report?.skipped_file_count ?? 0}，
                  产物 {runResult.run.run_report?.generated_artifact_count ?? 0}
                </p>
              </div>
              <Bot size={18} aria-hidden="true" />
            </article>

            <article className="source-card">
              <div>
                <div className="source-title-row">
                  <h3>步骤时间线</h3>
                  <span className="state-pill state-idle">{steps.length} 个步骤</span>
                </div>
                <ol className="unit-list">
                  {steps.map((step) => (
                    <li key={step.step_id} className="unit-item" aria-label={`${workflowStepLabel(step.name)} ${workflowStatusLabel(step.status)}`}>
                      <span>{workflowStepLabel(step.name)}</span>
                      <span className="workspace-meta">{workflowStatusLabel(step.status)}</span>
                    </li>
                  ))}
                </ol>
              </div>
              <Workflow size={18} aria-hidden="true" />
            </article>

            <article className="source-card">
              <div>
                <div className="source-title-row">
                  <h3>总结产物</h3>
                  <span className="state-pill state-idle">{artifacts.length} 份</span>
                </div>
                {artifacts.length ? (
                  <div className="artifact-list">
                    {artifacts.slice(0, 4).map((artifact) => {
                      const jumpableEvidenceCount = artifact.evidence_refs.filter(isJumpableSummaryEvidence).length;
                      return (
                        <details key={artifact.artifact_id}>
                          <summary>{artifact.title}</summary>
                          <pre className="text-preview">{artifact.markdown}</pre>
                          <p className="workspace-meta">
                            证据引用：{artifact.evidence_refs.length}，可回跳：{jumpableEvidenceCount}。
                          </p>
                          <SummaryEvidenceRefs
                            artifactId={artifact.artifact_id}
                            evidenceRefs={artifact.evidence_refs}
                            preciseNavigationEnabled={preciseNavigationEnabled}
                            onNavigateEvidence={onNavigateEvidence}
                          />
                        </details>
                      );
                    })}
                  </div>
                ) : (
                  <p className="workspace-meta">预览扫描只展示文件清单，不生成总结产物。</p>
                )}
              </div>
              <FileText size={18} aria-hidden="true" />
            </article>

            <article className="source-card">
              <div>
                <div className="source-title-row">
                  <h3>当前边界</h3>
                  <span className="state-pill state-idle">受限能力</span>
                </div>
                <p className="workspace-meta">当前只支持已注册的文件夹总结工作流；仅文件路径证据会作为来源说明展示，暂不能打开原文定位。</p>
              </div>
              <CheckCircle2 size={18} aria-hidden="true" />
            </article>
          </div>
        ) : null}
      </div>
    </section>
  );
}
