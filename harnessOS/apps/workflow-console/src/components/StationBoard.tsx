import { useMemo, useRef, useState, type DragEvent, type PointerEvent } from "react";
import type { StationBoardSummary } from "../api/types.js";
import { StationCard } from "./StationCard.js";

export interface StationBoardProps {
  stations: StationBoardSummary[];
  onSelectRun: (stationRunId: string) => void;
  ghostNodes?: Array<{ id: string; label: string }>;
  onNodeDrop?: (nodeCatalogId: string) => void;
  onEdgeProposal?: (fromStationId: string, toStationId: string) => void;
}

interface Point {
  x: number;
  y: number;
}

const DEFAULT_POSITIONS: Point[] = [
  { x: 60, y: 260 },
  { x: 290, y: 260 },
  { x: 520, y: 260 },
  { x: 750, y: 260 },
  { x: 980, y: 260 },
  { x: 1210, y: 260 },
  { x: 1440, y: 260 },
  { x: 1670, y: 260 },
];

function getInitialViewport(): Point {
  if (typeof window !== "undefined" && window.matchMedia("(max-width: 720px)").matches) {
    return { x: 52, y: 118 };
  }
  return { x: 320, y: 82 };
}

export function StationBoard({ stations, onSelectRun, ghostNodes = [], onNodeDrop, onEdgeProposal }: StationBoardProps) {
  const surfaceRef = useRef<HTMLDivElement | null>(null);
  const displayStations = useMemo(() => stations, [stations]);
  const [zoom, setZoom] = useState(0.78);
  const [viewport, setViewport] = useState<Point>(() => getInitialViewport());
  const [positions, setPositions] = useState<Record<string, Point>>(() => Object.fromEntries(
    displayStations.map((station, index) => [station.station.station_id, DEFAULT_POSITIONS[index] || { x: 80 + index * 280, y: 180 }]),
  ));
  const [drag, setDrag] = useState<
    | { kind: "pan"; start: Point; origin: Point }
    | { kind: "node"; stationId: string; start: Point; origin: Point }
    | null
  >(null);

  const edges = useMemo(() => displayStations.slice(0, -1).map((station, index) => {
    const from = positionForStation(positions, station.station.station_id, index);
    const to = positionForStation(positions, displayStations[index + 1].station.station_id, index + 1);
    return {
      id: `${station.station.station_id}_${displayStations[index + 1].station.station_id}`,
      x1: from.x + 188,
      y1: from.y + 92,
      x2: to.x,
      y2: to.y + 92,
    };
  }), [displayStations, positions]);

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
    setZoom(0.78);
    setViewport(getInitialViewport());
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    const nodeCatalogId = event.dataTransfer.getData("application/x-harnessos-node");
    if (nodeCatalogId) {
      onNodeDrop?.(nodeCatalogId);
    }
  }

  return (
    <section className="studio-canvas" aria-label="工作流画布" data-testid="station-board">
      <div className="canvas-header">
        <div>
          <span className="eyebrow">Workflow Canvas</span>
          <h2>工作流画布</h2>
        </div>
        <div className="canvas-toolbar" aria-label="画布工具栏">
          <button type="button" aria-label="缩小" onClick={() => setZoom((value) => Math.max(0.45, value - 0.08))}>−</button>
          <span>{Math.round(zoom * 100)}%</span>
          <button type="button" aria-label="放大" onClick={() => setZoom((value) => Math.min(1.4, value + 0.08))}>＋</button>
          <button type="button" onClick={fitView}>适配画布</button>
          <button type="button" disabled title="小地图属于后续画布布局能力，当前可使用缩放和平移。">小地图（后续）</button>
        </div>
      </div>
      <div className="canvas-navigation" aria-hidden="true">
        <span>⌕</span>
        <span>−</span>
        <span>{Math.round(zoom * 100)}%</span>
        <span>＋</span>
        <span>⛶</span>
      </div>
      <div className="canvas-runtime-meter" aria-hidden="true">
        <span>Projection fresh</span>
        <span>Draft read model</span>
        <span>Proposal only</span>
      </div>
      <div className="canvas-action-bar" aria-hidden="true">
        <button type="button" disabled title="画布当前只生成 proposal；保存工作流需走用户确认的 patch/publish 路径。">等待用户确认</button>
      </div>
      <div className="canvas-ghost-link left" aria-hidden="true" />
      <div className="canvas-ghost-link right" aria-hidden="true" />
      <div className="canvas-ghost-port left" aria-hidden="true" />
      <div className="canvas-ghost-port right" aria-hidden="true" />
      <div className="canvas-hidden-toolbar" aria-hidden="true">
        <div className="canvas-toolbar">
          <button type="button" onClick={() => setZoom((value) => Math.max(0.45, value - 0.08))}>-</button>
          <span>{Math.round(zoom * 100)}%</span>
          <button type="button" onClick={() => setZoom((value) => Math.min(1.4, value + 0.08))}>+</button>
          <button type="button" onClick={fitView}>适配画布</button>
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
        onDragOver={(event) => event.preventDefault()}
        onDrop={handleDrop}
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
          {displayStations.map((station, index) => {
            const position = positionForStation(positions, station.station.station_id, index);
            return (
              <div
                className="canvas-node"
                key={station.station.station_id}
                data-testid="station-card"
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
                {displayStations[index + 1] ? (
                  <button
                    className="edge-proposal-button"
                    data-testid="edge-proposal-button"
                    type="button"
                    onClick={(event) => {
                      event.stopPropagation();
                      onEdgeProposal?.(station.station.station_id, displayStations[index + 1].station.station_id);
                    }}
                  >
                    生成连线 Patch
                  </button>
                ) : null}
              </div>
            );
          })}
          {ghostNodes.map((ghost, index) => (
            <div
              className="canvas-node ghost-node"
              data-testid="ghost-node"
              key={ghost.id}
              style={{ transform: `translate(${80 + (displayStations.length + index) * 230}px, 88px)` }}
            >
              <div className="station-card">
                <span className="status">Pending Proposal</span>
                <h3>{ghost.label}</h3>
                <p>等待生成 Patch，尚未写入工作流草稿</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function positionForStation(positions: Record<string, Point>, stationId: string, index: number): Point {
  return positions[stationId] || DEFAULT_POSITIONS[index] || { x: 80 + index * 280, y: 180 };
}
