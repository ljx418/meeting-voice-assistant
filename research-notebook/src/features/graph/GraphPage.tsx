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
      <UnsupportedFeatureState title="请先从工作区打开知识图谱">
        只读图谱上下文属于具体工作区。请先打开一个工作区，再进入知识图谱。
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
          <div className="eyebrow">只读上下文</div>
          <h2 className="page-title">知识图谱上下文</h2>
        </div>
        <Link className="secondary-button" to={`/workspaces/${workspaceId}`}>
          返回工作区
        </Link>
      </div>

      <section className="panel" aria-labelledby="graph-status-title">
        <div className="panel-header">
          <h2 id="graph-status-title">图谱状态</h2>
        </div>
        <div className="panel-body page-grid">
          {communitiesQuery.isLoading || (selectedNodeId && neighborsQuery.isLoading) ? <LoadingState label="正在加载图谱上下文" /> : null}
          {graphMissing ? <MissingGraphArtifactState /> : null}
          {selectedNodeId && neighborsQuery.error && !graphMissing ? (
            <ApiErrorState title="图谱邻居不可用" error={neighborsQuery.error} onRetry={() => void neighborsQuery.refetch()} />
          ) : null}
          {communitiesQuery.error && !graphMissing ? (
            <ApiErrorState title="图谱社区不可用" error={communitiesQuery.error} onRetry={() => void communitiesQuery.refetch()} />
          ) : null}
          {!graphMissing && communitiesQuery.data ? (
            <StateBlock title="图谱上下文已加载" tone="neutral">
              图谱概览默认使用社区数据。选择图谱节点后，才会加载邻居关系。
            </StateBlock>
          ) : null}
        </div>
      </section>

      <section className="panel" aria-labelledby="graph-communities-title">
        <div className="panel-header">
          <h2 id="graph-communities-title">社区</h2>
        </div>
        <div className="panel-body page-grid">
          {communitiesQuery.data ? (
            <GraphCommunitiesList communities={communitiesQuery.data} selectedNodeId={selectedNodeId} onSelectNode={setSelectedNodeId} />
          ) : null}
        </div>
      </section>

      <section className="panel" aria-labelledby="graph-neighbors-title">
        <div className="panel-header">
          <h2 id="graph-neighbors-title">邻居节点</h2>
        </div>
        <div className="panel-body page-grid">
          {!selectedNodeId ? (
            <StateBlock title="请选择图谱节点" tone="neutral">
              选择一个图谱节点后，可以查看它的邻居关系。
            </StateBlock>
          ) : null}
          {selectedNodeId && neighborsQuery.isLoading ? <LoadingState label="正在加载图谱邻居" /> : null}
          {selectedNodeId && neighborsQuery.data ? (
            <GraphNeighborsList graph={neighborsQuery.data} selectedNodeId={selectedNodeId} onSelectNode={setSelectedNodeId} />
          ) : null}
          {selectedNodeId ? <p className="workspace-meta">已选节点：{selectedNodeId}</p> : null}
        </div>
      </section>

      <section className="panel" aria-labelledby="graph-feedback-title">
        <div className="panel-header">
          <h2 id="graph-feedback-title">图谱反馈</h2>
        </div>
        <div className="panel-body">
          <LightweightFeedback workspaceId={workspaceId} target={{ target_type: 'graph_context' }} />
        </div>
      </section>
    </div>
  );
}
