import type { WorkflowEvent } from "../api/types.js";
import { safeText } from "../api/redaction.js";

export interface AgentEventTimelineProps {
  events: WorkflowEvent[];
}

export function AgentEventTimeline({ events }: AgentEventTimelineProps) {
  return (
    <section className="agent-section">
      <h3>事件时间线</h3>
      <div className="event-feed">
        {events.map((event, index) => (
          <div className="event-row" key={event.id || `${event.type}_${index}`}>
            <strong>{event.type}</strong>
            <span className="status">{event.source || "live"}</span>
            {event.timestamp ? <div className="muted">{event.timestamp}</div> : null}
            {event.data ? <small>{safeText(event.data)}</small> : null}
          </div>
        ))}
      </div>
    </section>
  );
}
