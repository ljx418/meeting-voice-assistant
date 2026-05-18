import type { ArtifactSummary } from "../api/types.js";
import { safeText } from "../api/redaction.js";

export interface ArtifactSummaryPanelProps {
  artifacts: ArtifactSummary[];
}

export function ArtifactSummaryPanel({ artifacts }: ArtifactSummaryPanelProps) {
  return (
    <section className="panel">
      <h3>工件摘要</h3>
      {artifacts.length === 0 ? <p className="muted">暂无工件</p> : null}
      {artifacts.map((artifact) => (
        <div key={artifact.artifact_id}>
          <strong>{artifact.name || artifact.artifact_id}</strong>
          <div className="muted">{artifact.kind || "unknown"}</div>
          {artifact.parent_ids?.length ? <div>父工件：{artifact.parent_ids.join(", ")}</div> : null}
          {artifact.metadata ? <small>{safeText(artifact.metadata)}</small> : null}
        </div>
      ))}
    </section>
  );
}
