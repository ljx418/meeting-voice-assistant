import React from "react";
import type { UseApprovalsResult } from "@harnessos/client/react";

export function ApprovalPanel({ approvals }: { approvals: UseApprovalsResult }): JSX.Element {
  return (
    <section>
      <h2>Approvals</h2>
      {approvals.pendingApprovals.map((approval) => (
        <button key={approval.approval_id || approval.id} onClick={() => approvals.respond({ approvalId: String(approval.approval_id || approval.id), decision: "approve" })}>
          Approve
        </button>
      ))}
      <pre>{JSON.stringify({ status: approvals.status, count: approvals.pendingApprovals.length }, null, 2)}</pre>
    </section>
  );
}
