import React from "react";
import type { UseHarnessSessionResult, UseTurnResult } from "@harnessos/client/react";

export function SessionPanel({ session, turn }: { session: UseHarnessSessionResult; turn: UseTurnResult }): JSX.Element {
  return (
    <section>
      <h2>Session</h2>
      <button onClick={() => session.startSession({ model: "reference" })}>Start session</button>
      <button onClick={() => turn.startTurn({ input: "hello", sessionId: String(session.session?.session_id || "") })}>Start turn</button>
      <pre>{JSON.stringify({ session: session.status, turn: turn.status }, null, 2)}</pre>
    </section>
  );
}

