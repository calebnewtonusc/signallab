"use client";
import { useMemo } from "react";
import { formatModelName, modelAccent } from "@/lib/format";

interface CoverageChartProps {
  rollingCoverage: Record<string, Array<number | null>>;
  target: number;
  shiftIndex?: number | null;
}

export function CoverageChart({
  rollingCoverage,
  target,
  shiftIndex,
}: CoverageChartProps) {
  const width = 820;
  const height = 300;
  const padding = { top: 24, right: 24, bottom: 36, left: 48 };

  const { xScale, yScale, length, yTicks } = useMemo(() => {
    const lengths = Object.values(rollingCoverage).map((a) => a.length);
    const length = Math.max(0, ...lengths);
    const xScale = (i: number) =>
      padding.left +
      (i / Math.max(1, length - 1)) * (width - padding.left - padding.right);
    const yScale = (v: number) =>
      height - padding.bottom - v * (height - padding.top - padding.bottom);
    const yTicks = [0, 0.25, 0.5, 0.75, 1.0];
    return { xScale, yScale, length, yTicks };
  }, [rollingCoverage]);

  const models = Object.keys(rollingCoverage);

  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-900/60 backdrop-blur-sm p-6">
      <div className="flex items-baseline justify-between mb-4">
        <h3 className="text-sm font-semibold text-zinc-200">
          Rolling coverage (window = 30 folds)
        </h3>
        <span className="text-xs text-zinc-500">
          target = {(target * 100).toFixed(0)}%
        </span>
      </div>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full h-auto"
        role="img"
      >
        {yTicks.map((v) => (
          <g key={v}>
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
              {(v * 100).toFixed(0)}%
            </text>
          </g>
        ))}
        <line
          x1={padding.left}
          x2={width - padding.right}
          y1={yScale(target)}
          y2={yScale(target)}
          stroke="#6366f1"
          strokeWidth={1.2}
          strokeDasharray="5 4"
          opacity={0.6}
        />
        <text
          x={width - padding.right - 4}
          y={yScale(target) - 6}
          fontSize={10}
          textAnchor="end"
          fill="#818cf8"
        >
          target
        </text>

        {shiftIndex != null && shiftIndex >= 0 && shiftIndex < length ? (
          <g>
            <line
              x1={xScale(shiftIndex)}
              x2={xScale(shiftIndex)}
              y1={padding.top}
              y2={height - padding.bottom}
              stroke="#f43f5e"
              strokeWidth={1.2}
              strokeDasharray="4 3"
              opacity={0.7}
            />
            <text
              x={xScale(shiftIndex) + 6}
              y={padding.top + 12}
              fontSize={10}
              fill="#fb7185"
            >
              distribution shift
            </text>
          </g>
        ) : null}

        {models.map((m) => {
          const color = modelAccent(m);
          const arr = rollingCoverage[m];
          const path: string[] = [];
          let opened = false;
          arr.forEach((v, i) => {
            if (v == null) {
              opened = false;
              return;
            }
            path.push(`${!opened ? "M" : "L"} ${xScale(i)} ${yScale(v)}`);
            opened = true;
          });
          return (
            <path
              key={m}
              d={path.join(" ")}
              fill="none"
              stroke={color}
              strokeWidth={1.6}
              opacity={0.9}
            />
          );
        })}
      </svg>
      <div className="flex flex-wrap gap-x-4 gap-y-1.5 text-xs text-zinc-400 mt-3">
        {models.map((m) => (
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
