import React from "react";
import { Scope } from "@harnessos/client";
import { useApprovals, useArtifacts, useEvents, useHarnessSession, useJobs, useTurn } from "@harnessos/client/react";
import { createBffStructuredClient } from "./harness";
import { ApprovalPanel } from "./views/ApprovalPanel";
import { ArtifactPanel } from "./views/ArtifactPanel";
import { EmbedPanel } from "./views/EmbedPanel";
import { EventPanel } from "./views/EventPanel";
import { JobPanel } from "./views/JobPanel";
import { PackConnectorPanel } from "./views/PackConnectorPanel";
import { SessionPanel } from "./views/SessionPanel";
import { TracePanel } from "./views/TracePanel";

export function App(): JSX.Element {
  const scope = React.useMemo(() => new Scope({ app_id: "reference_app", project_id: "demo", workspace_id: "local" }), []);
  const client = React.useMemo(() => createBffStructuredClient(scope), [scope]);
  const session = useHarnessSession({ client, scope });
  const turn = useTurn({ client, scope });
  const events = useEvents({ client, scope, enabled: false });
  const artifacts = useArtifacts({ client, scope });
  const jobs = useJobs({ client, scope });
  const approvals = useApprovals({ client, scope, pendingApprovals: [] });

  return (
    <main>
      <SessionPanel session={session} turn={turn} />
      <EventPanel events={events} />
      <ArtifactPanel artifacts={artifacts} />
      <JobPanel jobs={jobs} />
      <ApprovalPanel approvals={approvals} />
      <PackConnectorPanel />
      <EmbedPanel />
      <TracePanel summary={{ trace_id: "trace_redacted", trace_count: 1, redacted_summary: "Trace details require BFF debug capability." }} />
    </main>
  );
}
