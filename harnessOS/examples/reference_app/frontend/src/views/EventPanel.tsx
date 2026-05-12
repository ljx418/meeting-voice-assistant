import React from "react";
import type { UseEventsResult } from "@harnessos/client/react";
import { connectBffEvents } from "../harness";

export function EventPanel({ events }: { events: UseEventsResult }): JSX.Element {
  return (
    <section>
      <h2>Events</h2>
      <button onClick={() => connectBffEvents(["chat", "job", "artifact", "approval"], () => undefined)}>Connect BFF events</button>
      <pre>{JSON.stringify({ status: events.status, count: events.events.length }, null, 2)}</pre>
    </section>
  );
}

