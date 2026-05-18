import type { StationBoardSummary } from "../api/types.js";
import { safeText } from "../api/redaction.js";

export interface StationCardProps {
  station: StationBoardSummary;
  onSelectRun: (stationRunId: string) => void;
}

export function StationCard({ station, onSelectRun }: StationCardProps) {
  const latestRun = station.runs[0];
  return (
    <article className="station-card">
      <div className="station-card-head">
        <span className="node-port" aria-hidden="true" />
        <strong>{station.station.name || station.station.station_id}</strong>
        <span className="status">{station.status}</span>
      </div>
      <p className="muted">{station.station.role || "未设置角色"}</p>
      {latestRun ? (
        <button type="button" onClick={() => onSelectRun(latestRun.station_run_id)}>
          查看节点输出
        </button>
      ) : null}
      <dl>
        <dt>工件</dt>
        <dd>{station.output_artifacts?.length || 0}</dd>
        <dt>审批</dt>
        <dd>{station.approvals?.map((approval) => approval.status).join(", ") || "无"}</dd>
        <dt>质量</dt>
        <dd>{station.quality?.map((quality) => `${quality.status}${quality.score !== undefined ? ` ${quality.score}` : ""}`).join(", ") || "无"}</dd>
        <dt>Trace</dt>
        <dd>{safeText(station.trace_summary?.summary || station.trace_summary?.trace_id || "无")}</dd>
      </dl>
    </article>
  );
}
