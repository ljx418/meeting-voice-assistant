import type { GraphCommunitiesResponse, GraphNeighborsResponse, SessionGraphContextResponse } from '../types/api';
import { StateBlock } from './StateBlock';

function graphNodeDescriptor(node: GraphNeighborsResponse['nodes'][number] | GraphNeighborsResponse['neighbors'][number]) {
  if ('relationship' in node && node.relationship) return node.relationship;
  return node.node_type || 'node';
}

export function MissingGraphArtifactState() {
  return (
    <StateBlock title="缺少图谱工件" tone="warning">
      使用图谱上下文前，需要先由后端构建图谱工件。
    </StateBlock>
  );
}

export function GraphNeighborsList({
  graph,
  selectedNodeId,
  onSelectNode
}: {
  graph: GraphNeighborsResponse;
  selectedNodeId?: string | null;
  onSelectNode?: (nodeId: string) => void;
}) {
  if (graph.status === 'missing_artifact') return <MissingGraphArtifactState />;
  if (graph.neighbors.length === 0 && graph.nodes.length === 0) {
    return <StateBlock title="暂无图谱邻居" tone="neutral">图谱接口没有返回相关节点。</StateBlock>;
  }

  const nodes = graph.neighbors.length > 0 ? graph.neighbors : graph.nodes;
  return (
    <div className="graph-node-list" aria-label="图谱邻居">
      {nodes.map((node) => (
        <button
          className={`graph-node${selectedNodeId === node.node_id ? ' selected' : ''}`}
          key={node.node_id}
          type="button"
          onClick={() => onSelectNode?.(node.node_id)}
        >
          <span>{node.label}</span>
          <small>{graphNodeDescriptor(node)}</small>
        </button>
      ))}
    </div>
  );
}

export function GraphCommunitiesList({
  communities,
  selectedNodeId,
  onSelectNode
}: {
  communities: GraphCommunitiesResponse;
  selectedNodeId?: string | null;
  onSelectNode?: (nodeId: string) => void;
}) {
  if (communities.status === 'missing_artifact') return <MissingGraphArtifactState />;
  if (communities.communities.length === 0) {
    return <StateBlock title="暂无图谱社区" tone="neutral">图谱接口没有返回社区。</StateBlock>;
  }

  return (
    <div className="graph-community-list" aria-label="图谱社区">
      {communities.communities.map((community) => (
        <article className="graph-community-card" key={community.community_id}>
          <h3>{community.title}</h3>
          {community.summary ? <p>{community.summary}</p> : null}
          <dl className="source-meta-grid">
            <div>
              <dt>community_id</dt>
              <dd>{community.community_id}</dd>
            </div>
            <div>
              <dt>节点数</dt>
              <dd>{community.node_count ?? '未知'}</dd>
            </div>
            <div>
              <dt>关系数</dt>
              <dd>{community.relationship_count ?? '未知'}</dd>
            </div>
            <div>
              <dt>分数</dt>
              <dd>{community.score ?? '未知'}</dd>
            </div>
          </dl>
          {community.members?.length ? (
            <div className="graph-node-list" aria-label={`${community.title} members`}>
              {community.members.map((member) => (
                <button
                  className={`graph-node${selectedNodeId === member.node_id ? ' selected' : ''}`}
                  key={member.node_id}
                  type="button"
                  onClick={() => onSelectNode?.(member.node_id)}
                >
                  <span>{member.label}</span>
                  <small>{member.entity_id || member.node_type || 'node'}</small>
                </button>
              ))}
            </div>
          ) : null}
        </article>
      ))}
    </div>
  );
}

export function SessionGraphContext({ graph }: { graph: SessionGraphContextResponse }) {
  if (graph.status === 'missing_artifact') return <MissingGraphArtifactState />;
  if (graph.related_nodes.length === 0 && graph.related_communities.length === 0) {
    return <StateBlock title="暂无会话图谱上下文" tone="neutral">当前会话没有返回相关图谱上下文。</StateBlock>;
  }

  return (
    <div className="session-graph-context">
      {graph.summary ? <p>{graph.summary}</p> : null}
      {graph.related_nodes.length > 0 ? (
        <div className="graph-node-list" aria-label="会话图谱节点">
          {graph.related_nodes.map((node) => (
            <div className="graph-node static" key={node.node_id}>
              <span>{node.label}</span>
              <small>{node.node_type || 'node'}</small>
            </div>
          ))}
        </div>
      ) : null}
      {graph.related_communities.length > 0 ? <GraphCommunitiesList communities={{ ...graph, communities: graph.related_communities }} /> : null}
    </div>
  );
}
