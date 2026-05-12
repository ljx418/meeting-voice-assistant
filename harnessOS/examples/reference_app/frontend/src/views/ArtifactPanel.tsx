import React from "react";
import type { UseArtifactsResult } from "@harnessos/client/react";

export function ArtifactPanel({ artifacts }: { artifacts: UseArtifactsResult }): JSX.Element {
  return (
    <section>
      <h2>Artifacts</h2>
      <button onClick={() => artifacts.refresh()}>Refresh artifacts</button>
      <pre>{JSON.stringify({ status: artifacts.status, count: Array.isArray(artifacts.artifacts) ? artifacts.artifacts.length : 0 }, null, 2)}</pre>
    </section>
  );
}
