import type { WorkflowEvent } from "../api/types.js";
import { safeText } from "../api/redaction.js";

export interface EventFeedProps {
  events: WorkflowEvent[];
}

export function EventFeed({ events }: EventFeedProps) {
  return (
    <section className="panel" data-testid="event-feed">
      <h3>事件流</h3>
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
