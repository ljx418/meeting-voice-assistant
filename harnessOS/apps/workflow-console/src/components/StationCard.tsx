import type { StationBoardSummary } from "../api/types.js";
import { safeText } from "../api/redaction.js";

export interface StationCardProps {
  station: StationBoardSummary;
  onSelectRun: (stationRunId: string) => void;
}

export function StationCard({ station, onSelectRun }: StationCardProps) {
  const latestRun = station.runs[0];
  const qualityScore = station.quality?.find((quality) => quality.score !== undefined)?.score;
  const statusLabel = station.status === "warning" ? "WARNING" : station.status === "completed" ? "DONE" : station.status === "queued" ? "待执行" : station.status;
  const artifactName = station.output_artifacts?.[0]?.name || latestRun?.output_artifacts?.[0]?.name || "待生成";
  return (
    <article className={`station-card station-${station.status}`}>
      <div className="station-card-head">
        <span className="node-port" aria-hidden="true" />
        <strong>{station.station.name || station.station.station_id}</strong>
        <span className="status">{statusLabel}</span>
      </div>
      <p className="muted">{station.station.role === "director" ? "Agent · 分镜设计师" : station.station.role === "writer" ? "LLM · Qwen-Max" : station.station.role || "未设置角色"}</p>
      {latestRun ? (
        <button type="button" onClick={() => onSelectRun(latestRun.station_run_id)}>
          查看节点输出
        </button>
      ) : null}
      <div className="node-progress" aria-hidden="true"><span /></div>
      <dl>
        <dt>输入</dt>
        <dd>{station.input_artifacts?.length || latestRun?.input_artifacts?.length || 0}</dd>
        <dt>输出</dt>
        <dd>{station.output_artifacts?.length || latestRun?.output_artifacts?.length || 0}</dd>
        <dt>产物</dt>
        <dd>{artifactName}</dd>
        <dt>质量</dt>
        <dd>{qualityScore !== undefined ? qualityScore.toFixed(2) : "—"}</dd>
        <dt>审批</dt>
        <dd>{station.approvals?.map((approval) => approval.status).join(", ") || latestRun?.approvals?.map((approval) => approval.status).join(", ") || "无"}</dd>
        <dt>Trace</dt>
        <dd>{safeText(station.trace_summary?.summary || station.trace_summary?.trace_id || "无")}</dd>
      </dl>
    </article>
  );
}
