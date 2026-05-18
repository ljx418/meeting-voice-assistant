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
      <StateBlock title="Workspace request failed" tone="error">
        {error.message}
      </StateBlock>
    );
  }

  return (
    <StateBlock title="Workspace request failed" tone="error">
      The workspace list could not be loaded.
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
    <form className="panel" onSubmit={submit} aria-label="Create workspace">
      <div className="panel-header">
        <h2>Create workspace</h2>
      </div>
      <div className="panel-body page-grid">
        <label>
          <span className="field-label">Name</span>
          <input
            id={nameInputId}
            className="text-input"
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Technical interview notes"
          />
        </label>
        <label>
          <span className="field-label">Description</span>
          <input
            id={descriptionInputId}
            className="text-input"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            placeholder="Optional"
          />
        </label>
        {createWorkspace.error ? (
          <StateBlock title="Create workspace failed" tone="error">
            {isNormalizedApiError(createWorkspace.error)
              ? createWorkspace.error.message
              : 'The workspace could not be created.'}
          </StateBlock>
        ) : null}
        <div>
          <button className="primary-button" type="submit" disabled={createWorkspace.isPending || !name.trim()}>
            <Plus size={16} aria-hidden="true" /> {createWorkspace.isPending ? 'Creating' : 'Create workspace'}
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
          <div className="eyebrow">Workspace Home</div>
          <h2 className="page-title">Personal knowledge workspaces</h2>
        </div>
      </div>

      <div className="placeholder-layout">
        <section className="panel" aria-labelledby="workspace-list-title">
          <div className="panel-header">
            <h2 id="workspace-list-title">Workspaces</h2>
          </div>
          <div className="panel-body">
            {workspacesQuery.isLoading ? <LoadingState label="Loading workspaces" /> : null}
            {workspacesQuery.error ? (
              <WorkspaceError error={workspacesQuery.error} onRetry={() => void workspacesQuery.refetch()} />
            ) : null}
            {workspacesQuery.data && workspacesQuery.data.length === 0 ? (
              <EmptyState title="No workspaces yet">
                Create a workspace to start a source-grounded personal knowledge library.
              </EmptyState>
            ) : null}
            {workspacesQuery.data && workspacesQuery.data.length > 0 ? (
              <div className="workspace-list" aria-label="Workspace list">
                {workspacesQuery.data.map((workspace) => (
                  <Link
                    className="workspace-card"
                    to={`/workspaces/${encodeURIComponent(workspace.workspace_id)}`}
                    key={workspace.workspace_id}
                  >
                    <div>
                      <p className="workspace-title">{workspace.name}</p>
                      <div className="workspace-meta">
                        {workspace.description || 'No description'} · {workspace.workspace_id}
                      </div>
                    </div>
                    <span className="service-status">{workspace.archived ? 'Archived' : 'Active'}</span>
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
