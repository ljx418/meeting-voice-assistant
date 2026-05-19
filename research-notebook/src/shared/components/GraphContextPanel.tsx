import type { GraphCommunitiesResponse, GraphNeighborsResponse, SessionGraphContextResponse } from '../types/api';
import { StateBlock } from './StateBlock';

function graphNodeDescriptor(node: GraphNeighborsResponse['nodes'][number] | GraphNeighborsResponse['neighbors'][number]) {
  if ('relationship' in node && node.relationship) return node.relationship;
  return node.node_type || 'node';
}

export function MissingGraphArtifactState() {
  return (
    <StateBlock title="Missing graph artifact" tone="warning">
      Build graph artifacts in the backend before using graph context.
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
    return <StateBlock title="No graph neighbors" tone="neutral">The graph route returned no related nodes.</StateBlock>;
  }

  const nodes = graph.neighbors.length > 0 ? graph.neighbors : graph.nodes;
  return (
    <div className="graph-node-list" aria-label="Graph neighbors">
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
    return <StateBlock title="No graph communities" tone="neutral">The graph route returned no communities.</StateBlock>;
  }

  return (
    <div className="graph-community-list" aria-label="Graph communities">
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
              <dt>nodes</dt>
              <dd>{community.node_count ?? 'unknown'}</dd>
            </div>
            <div>
              <dt>relationships</dt>
              <dd>{community.relationship_count ?? 'unknown'}</dd>
            </div>
            <div>
              <dt>score</dt>
              <dd>{community.score ?? 'unknown'}</dd>
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
    return <StateBlock title="No session graph context" tone="neutral">No related graph context was returned for this session.</StateBlock>;
  }

  return (
    <div className="session-graph-context">
      {graph.summary ? <p>{graph.summary}</p> : null}
      {graph.related_nodes.length > 0 ? (
        <div className="graph-node-list" aria-label="Session graph nodes">
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
