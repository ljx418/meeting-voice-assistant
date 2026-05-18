import { useMemo, useRef, useState, type PointerEvent } from "react";
import type { StationBoardSummary } from "../api/types.js";
import { StationCard } from "./StationCard.js";

export interface StationBoardProps {
  stations: StationBoardSummary[];
  onSelectRun: (stationRunId: string) => void;
}

interface Point {
  x: number;
  y: number;
}

const DEFAULT_POSITIONS: Point[] = [
  { x: 40, y: 180 },
  { x: 320, y: 180 },
  { x: 600, y: 180 },
  { x: 880, y: 180 },
  { x: 1160, y: 180 },
  { x: 1440, y: 180 },
  { x: 1720, y: 180 },
  { x: 2000, y: 180 },
];

export function StationBoard({ stations, onSelectRun }: StationBoardProps) {
  const surfaceRef = useRef<HTMLDivElement | null>(null);
  const [zoom, setZoom] = useState(0.82);
  const [viewport, setViewport] = useState<Point>({ x: 120, y: 30 });
  const [positions, setPositions] = useState<Record<string, Point>>(() => Object.fromEntries(
    stations.map((station, index) => [station.station.station_id, DEFAULT_POSITIONS[index] || { x: 80 + index * 280, y: 180 }]),
  ));
  const [drag, setDrag] = useState<
    | { kind: "pan"; start: Point; origin: Point }
    | { kind: "node"; stationId: string; start: Point; origin: Point }
    | null
  >(null);

  const edges = useMemo(() => stations.slice(0, -1).map((station, index) => {
    const from = positions[station.station.station_id];
    const to = positions[stations[index + 1].station.station_id];
    return {
      id: `${station.station.station_id}_${stations[index + 1].station.station_id}`,
      x1: from.x + 224,
      y1: from.y + 92,
      x2: to.x,
      y2: to.y + 92,
    };
  }), [positions, stations]);

  function pointFromEvent(event: PointerEvent): Point {
    return { x: event.clientX, y: event.clientY };
  }

  function handleMove(event: PointerEvent) {
    if (!drag) return;
    const point = pointFromEvent(event);
    if (drag.kind === "pan") {
      setViewport({ x: drag.origin.x + point.x - drag.start.x, y: drag.origin.y + point.y - drag.start.y });
      return;
    }
    setPositions((current) => ({
      ...current,
      [drag.stationId]: {
        x: drag.origin.x + (point.x - drag.start.x) / zoom,
        y: drag.origin.y + (point.y - drag.start.y) / zoom,
      },
    }));
  }

  function fitView() {
    setZoom(0.82);
    setViewport({ x: 120, y: 30 });
  }

  return (
    <section className="studio-canvas" aria-label="工作流画布">
      <div className="canvas-header">
        <div>
          <span className="eyebrow">Workflow Canvas</span>
          <h2>工作流画布</h2>
        </div>
        <div className="canvas-toolbar" aria-label="画布工具栏">
          <button type="button" disabled>撤销</button>
          <button type="button" disabled>重做</button>
          <button type="button" onClick={() => setZoom((value) => Math.max(0.45, value - 0.08))}>-</button>
          <span>{Math.round(zoom * 100)}%</span>
          <button type="button" onClick={() => setZoom((value) => Math.min(1.4, value + 0.08))}>+</button>
          <button type="button" onClick={fitView}>适配画布</button>
          <button type="button" disabled>小地图</button>
        </div>
      </div>
      <div
        className="canvas-surface"
        ref={surfaceRef}
        onPointerDown={(event) => {
          const target = event.target as HTMLElement;
          if (target.closest(".canvas-node") || target.closest("button")) return;
          event.currentTarget.setPointerCapture(event.pointerId);
          setDrag({ kind: "pan", start: pointFromEvent(event), origin: viewport });
        }}
        onPointerMove={handleMove}
        onPointerUp={() => setDrag(null)}
        onPointerCancel={() => setDrag(null)}
      >
        <div className="infinite-layer" style={{ transform: `translate(${viewport.x}px, ${viewport.y}px) scale(${zoom})` }}>
          <svg className="edge-layer" width="2400" height="720" aria-hidden="true">
            {edges.map((edge) => (
              <path
                d={`M ${edge.x1} ${edge.y1} C ${edge.x1 + 70} ${edge.y1}, ${edge.x2 - 70} ${edge.y2}, ${edge.x2} ${edge.y2}`}
                key={edge.id}
              />
            ))}
          </svg>
          {stations.map((station) => {
            const position = positions[station.station.station_id] || { x: 0, y: 0 };
            return (
              <div
                className="canvas-node"
                key={station.station.station_id}
                style={{ transform: `translate(${position.x}px, ${position.y}px)` }}
                onPointerDown={(event) => {
                  const target = event.target as HTMLElement;
                  if (target.closest("button")) return;
                  event.stopPropagation();
                  (event.currentTarget as HTMLElement).setPointerCapture(event.pointerId);
                  setDrag({
                    kind: "node",
                    stationId: station.station.station_id,
                    start: pointFromEvent(event),
                    origin: position,
                  });
                }}
              >
                <StationCard station={station} onSelectRun={onSelectRun} />
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
