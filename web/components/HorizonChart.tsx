"use client";
import { useMemo } from "react";
import type { HorizonSummary } from "@/lib/types";
import { formatModelName, modelAccent } from "@/lib/format";

interface HorizonChartProps {
  horizons: HorizonSummary[];
  metric: "mae" | "rmse" | "smape";
  title: string;
}

export function HorizonChart({ horizons, metric, title }: HorizonChartProps) {
  const byModel = useMemo(() => {
    const map = new Map<string, HorizonSummary[]>();
    for (const row of horizons) {
      if (!map.has(row.model)) map.set(row.model, []);
      map.get(row.model)!.push(row);
    }
    for (const arr of map.values()) {
      arr.sort((a, b) => a.horizon_step - b.horizon_step);
    }
    return map;
  }, [horizons]);

  const width = 820;
  const height = 300;
  const padding = { top: 24, right: 24, bottom: 40, left: 48 };

  const { xs, xScale, yScale, yTicks } = useMemo(() => {
    const allSteps = horizons.map((h) => h.horizon_step);
    const allVals = horizons.map((h) => h[metric]);
    const xMin = Math.min(...allSteps);
    const xMax = Math.max(...allSteps);
    const yMax = Math.max(...allVals) * 1.08;
    const yMin = 0;
    const xs = Array.from(new Set(allSteps)).sort((a, b) => a - b);
    const xScale = (s: number) =>
      padding.left +
      ((s - xMin) / (xMax - xMin || 1)) *
        (width - padding.left - padding.right);
    const yScale = (v: number) =>
      height -
      padding.bottom -
      ((v - yMin) / (yMax - yMin || 1)) *
        (height - padding.top - padding.bottom);
    const tickCount = 5;
    const yTicks = Array.from(
      { length: tickCount },
      (_, i) => yMin + (i * (yMax - yMin)) / (tickCount - 1),
    );
    return { xs, xScale, yScale, yTicks };
  }, [horizons, metric]);

  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-900/60 backdrop-blur-sm p-6">
      <div className="flex items-baseline justify-between mb-4">
        <h3 className="text-sm font-semibold text-zinc-200">{title}</h3>
        <span className="text-xs text-zinc-500">
          metric: {metric.toUpperCase()}
        </span>
      </div>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full h-auto"
        role="img"
      >
        {yTicks.map((v, i) => (
          <g key={i}>
            <line
              x1={padding.left}
              x2={width - padding.right}
              y1={yScale(v)}
              y2={yScale(v)}
              stroke="rgba(255,255,255,0.05)"
              strokeDasharray="3 3"
            />
            <text
              x={padding.left - 8}
              y={yScale(v) + 3}
              textAnchor="end"
              fontSize={10}
              fill="#71717a"
            >
              {v.toFixed(0)}
            </text>
          </g>
        ))}
        {xs.map((s) => (
          <text
            key={s}
            x={xScale(s)}
            y={height - padding.bottom + 18}
            textAnchor="middle"
            fontSize={10}
            fill="#71717a"
          >
            h = {s}
          </text>
        ))}
        {[...byModel.entries()].map(([model, rows]) => {
          const color = modelAccent(model);
          const path = rows
            .map(
              (r, i) =>
                `${i === 0 ? "M" : "L"} ${xScale(r.horizon_step)} ${yScale(r[metric])}`,
            )
            .join(" ");
          return (
            <g key={model}>
              <path d={path} fill="none" stroke={color} strokeWidth={2} />
              {rows.map((r) => (
                <circle
                  key={r.horizon_step}
                  cx={xScale(r.horizon_step)}
                  cy={yScale(r[metric])}
                  r={3}
                  fill={color}
                />
              ))}
            </g>
          );
        })}
      </svg>
      <div className="flex flex-wrap gap-x-4 gap-y-1.5 text-xs text-zinc-400 mt-3">
        {[...byModel.keys()].map((m) => (
          <span key={m} className="flex items-center gap-1.5">
            <span
              className="h-2 w-3 rounded-sm"
              style={{ background: modelAccent(m) }}
              aria-hidden="true"
            />
            {formatModelName(m)}
          </span>
        ))}
      </div>
    </div>
  );
}
