import { FormEvent, useId, useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus } from 'lucide-react';
import { isNormalizedApiError } from '../../shared/api/dataServiceClient';
import { useCreateWorkspaceMutation, useWorkspacesQuery } from '../../shared/api/workspaceQueries';
import {
  BackendUnavailableState,
  EmptyState,
  LoadingState,
  StateBlock,
  VersionMismatchState
} from '../../shared/components/StateBlock';

function WorkspaceError({ error, onRetry }: { error: unknown; onRetry: () => void }) {
  if (isNormalizedApiError(error)) {
    if (error.code === 'backend_unavailable' || error.code === 'request_timeout') {
      return <BackendUnavailableState onRetry={onRetry} />;
    }
    if (error.code === 'version_or_schema_mismatch') {
      return <VersionMismatchState />;
    }
    return (
      <StateBlock title="工作区请求失败" tone="error">
        {error.message}
      </StateBlock>
    );
  }

  return (
    <StateBlock title="工作区请求失败" tone="error">
      工作区列表无法加载。
    </StateBlock>
  );
}

function CreateWorkspaceForm() {
  const nameInputId = useId();
  const descriptionInputId = useId();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const createWorkspace = useCreateWorkspaceMutation();

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmedName = name.trim();
    if (!trimmedName) return;
    createWorkspace.mutate({
      name: trimmedName,
      description: description.trim() || undefined
    });
  };

  return (
    <form className="panel" onSubmit={submit} aria-label="创建工作区">
      <div className="panel-header">
        <h2>创建工作区</h2>
      </div>
      <div className="panel-body page-grid">
        <label>
          <span className="field-label">名称</span>
          <input
            id={nameInputId}
            className="text-input"
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="例如：技术访谈笔记"
          />
        </label>
        <label>
          <span className="field-label">描述</span>
          <input
            id={descriptionInputId}
            className="text-input"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            placeholder="可选"
          />
        </label>
        {createWorkspace.error ? (
          <StateBlock title="创建工作区失败" tone="error">
            {isNormalizedApiError(createWorkspace.error)
              ? createWorkspace.error.message
              : '工作区无法创建。'}
          </StateBlock>
        ) : null}
        <div>
          <button className="primary-button" type="submit" disabled={createWorkspace.isPending || !name.trim()}>
            <Plus size={16} aria-hidden="true" /> {createWorkspace.isPending ? '创建中' : '创建工作区'}
          </button>
        </div>
      </div>
    </form>
  );
}

export function HomePage() {
  const workspacesQuery = useWorkspacesQuery();

  return (
    <div className="page-grid">
      <div className="toolbar-row">
        <div>
          <div className="eyebrow">工作区首页</div>
          <h2 className="page-title">个人知识工作区</h2>
        </div>
      </div>

      <div className="placeholder-layout">
        <section className="panel" aria-labelledby="workspace-list-title">
          <div className="panel-header">
            <h2 id="workspace-list-title">工作区列表</h2>
          </div>
          <div className="panel-body">
            {workspacesQuery.isLoading ? <LoadingState label="正在加载工作区" /> : null}
            {workspacesQuery.error ? (
              <WorkspaceError error={workspacesQuery.error} onRetry={() => void workspacesQuery.refetch()} />
            ) : null}
            {workspacesQuery.data && workspacesQuery.data.length === 0 ? (
              <EmptyState title="暂无工作区">
                创建一个工作区，开始管理基于来源的个人知识库。
              </EmptyState>
            ) : null}
            {workspacesQuery.data && workspacesQuery.data.length > 0 ? (
              <div className="workspace-list" aria-label="工作区列表">
                {workspacesQuery.data.map((workspace) => (
                  <Link
                    className="workspace-card"
                    to={`/workspaces/${encodeURIComponent(workspace.workspace_id)}`}
                    key={workspace.workspace_id}
                  >
                    <div>
                      <p className="workspace-title">{workspace.name}</p>
                      <div className="workspace-meta">
                        {workspace.description || '暂无描述'} · {workspace.workspace_id}
                      </div>
                    </div>
                    <span className="service-status">{workspace.archived ? '已归档' : '可用'}</span>
                  </Link>
                ))}
              </div>
            ) : null}
          </div>
        </section>
        <CreateWorkspaceForm />
      </div>
    </div>
  );
}
