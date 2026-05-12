import React from "react";
import type { UseJobsResult } from "@harnessos/client/react";

export function JobPanel({ jobs }: { jobs: UseJobsResult }): JSX.Element {
  return (
    <section>
      <h2>Jobs</h2>
      <button onClick={() => jobs.refresh()}>Refresh jobs</button>
      <pre>{JSON.stringify({ status: jobs.status, count: Array.isArray(jobs.jobs) ? jobs.jobs.length : 0 }, null, 2)}</pre>
    </section>
  );
}
