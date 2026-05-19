import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { isNormalizedApiError } from '../../shared/api/dataServiceClient';
import { useGraphCommunitiesQuery, useGraphNeighborsQuery } from '../../shared/api/workspaceM4Queries';
import { ApiErrorState } from '../../shared/components/ApiErrorState';
import { GraphCommunitiesList, GraphNeighborsList, MissingGraphArtifactState } from '../../shared/components/GraphContextPanel';
import { LoadingState, StateBlock, UnsupportedFeatureState } from '../../shared/components/StateBlock';
import { LightweightFeedback } from '../../shared/components/LightweightFeedback';

export function GraphPage() {
  const { workspaceId = '' } = useParams();
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const neighborsQuery = useGraphNeighborsQuery(workspaceId, selectedNodeId ? { nodeId: selectedNodeId } : null);
  const communitiesQuery = useGraphCommunitiesQuery(workspaceId);

  if (!workspaceId) {
    return (
      <UnsupportedFeatureState title="Open Graph From A Workspace">
        Read-only graph context is scoped to a workspace. Open a workspace first, then use its graph route.
      </UnsupportedFeatureState>
    );
  }

  const graphMissing =
    communitiesQuery.data?.status === 'missing_artifact' ||
    (selectedNodeId && isNormalizedApiError(neighborsQuery.error) && neighborsQuery.error.code === 'missing_graph_artifact') ||
    (isNormalizedApiError(communitiesQuery.error) && communitiesQuery.error.code === 'missing_graph_artifact');

  return (
    <div className="page-grid">
      <div className="toolbar-row">
        <div>
          <div className="eyebrow">V1.0-M4</div>
          <h2 className="page-title">Read-only Graph Context</h2>
        </div>
        <Link className="secondary-button" to={`/workspaces/${workspaceId}`}>
          Workspace
        </Link>
      </div>

      <section className="panel" aria-labelledby="graph-status-title">
        <div className="panel-header">
          <h2 id="graph-status-title">Graph Status</h2>
        </div>
        <div className="panel-body page-grid">
          {communitiesQuery.isLoading || (selectedNodeId && neighborsQuery.isLoading) ? <LoadingState label="Loading graph context" /> : null}
          {graphMissing ? <MissingGraphArtifactState /> : null}
          {selectedNodeId && neighborsQuery.error && !graphMissing ? (
            <ApiErrorState title="Graph neighbors unavailable" error={neighborsQuery.error} onRetry={() => void neighborsQuery.refetch()} />
          ) : null}
          {communitiesQuery.error && !graphMissing ? (
            <ApiErrorState title="Graph communities unavailable" error={communitiesQuery.error} onRetry={() => void communitiesQuery.refetch()} />
          ) : null}
          {!graphMissing && communitiesQuery.data ? (
            <StateBlock title="Graph context loaded" tone="neutral">
              Graph overview uses community data by default. Neighbor inspection only starts after selecting a graph node.
            </StateBlock>
          ) : null}
        </div>
      </section>

      <section className="panel" aria-labelledby="graph-communities-title">
        <div className="panel-header">
          <h2 id="graph-communities-title">Communities</h2>
        </div>
        <div className="panel-body page-grid">
          {communitiesQuery.data ? (
            <GraphCommunitiesList communities={communitiesQuery.data} selectedNodeId={selectedNodeId} onSelectNode={setSelectedNodeId} />
          ) : null}
        </div>
      </section>

      <section className="panel" aria-labelledby="graph-neighbors-title">
        <div className="panel-header">
          <h2 id="graph-neighbors-title">Neighbors</h2>
        </div>
        <div className="panel-body page-grid">
          {!selectedNodeId ? (
            <StateBlock title="Select a graph node" tone="neutral">
              Select a graph node to inspect neighbors.
            </StateBlock>
          ) : null}
          {selectedNodeId && neighborsQuery.isLoading ? <LoadingState label="Loading graph neighbors" /> : null}
          {selectedNodeId && neighborsQuery.data ? (
            <GraphNeighborsList graph={neighborsQuery.data} selectedNodeId={selectedNodeId} onSelectNode={setSelectedNodeId} />
          ) : null}
          {selectedNodeId ? <p className="workspace-meta">Selected node: {selectedNodeId}</p> : null}
        </div>
      </section>

      <section className="panel" aria-labelledby="graph-feedback-title">
        <div className="panel-header">
          <h2 id="graph-feedback-title">Graph Feedback</h2>
        </div>
        <div className="panel-body">
          <LightweightFeedback workspaceId={workspaceId} target={{ target_type: 'graph_context' }} />
        </div>
      </section>
    </div>
  );
}
