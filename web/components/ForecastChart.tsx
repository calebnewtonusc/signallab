"use client";
import { useMemo, useState } from "react";
import type { RecordRow } from "@/lib/types";
import { formatModelName, modelAccent } from "@/lib/format";

interface ForecastChartProps {
  records: RecordRow[];
  horizonStep: number;
  availableModels: string[];
}

export function ForecastChart({
  records,
  horizonStep,
  availableModels,
}: ForecastChartProps) {
  const [active, setActive] = useState(availableModels[0] ?? "");

  const filtered = useMemo(() => {
    return records
      .filter((r) => r.model === active && r.horizon_step === horizonStep)
      .sort((a, b) => a.test_time.localeCompare(b.test_time));
  }, [records, active, horizonStep]);

  const { ticks, xScale, yScale, yTicks, width, height, padding } =
    useMemo(() => {
      const width = 820;
      const height = 340;
      const padding = { top: 20, right: 20, bottom: 40, left: 48 };
      if (filtered.length === 0) {
        return {
          ticks: [],
          xScale: (_: number) => 0,
          yScale: (_: number) => 0,
          yTicks: [],
          width,
          height,
          padding,
        };
      }
      const xs = filtered.map((_, i) => i);
      const ys = filtered.flatMap((r) => [
        r.y_true,
        r.y_pred,
        r.lower,
        r.upper,
      ]);
      const xMin = 0;
      const xMax = xs.length - 1 || 1;
      const yMin = Math.min(...ys);
      const yMax = Math.max(...ys);
      const yPad = (yMax - yMin) * 0.08 || 1;
      const yRange: [number, number] = [yMin - yPad, yMax + yPad];
      const xScale = (x: number) =>
        padding.left +
        ((x - xMin) / (xMax - xMin || 1)) *
          (width - padding.left - padding.right);
      const yScale = (y: number) =>
        height -
        padding.bottom -
        ((y - yRange[0]) / (yRange[1] - yRange[0])) *
          (height - padding.top - padding.bottom);
      const step = Math.max(1, Math.floor(filtered.length / 6));
      const ticks = filtered
        .map((r, i) => ({ i, label: r.test_time.slice(0, 7) }))
        .filter((_, i) => i % step === 0);
      const yTickCount = 5;
      const yTicks = Array.from({ length: yTickCount }, (_, i) => {
        const v = yRange[0] + (i / (yTickCount - 1)) * (yRange[1] - yRange[0]);
        return v;
      });
      return { ticks, xScale, yScale, yTicks, width, height, padding };
    }, [filtered]);

  const bandPath = useMemo(() => {
    if (filtered.length === 0) return "";
    const top = filtered.map(
      (r, i) => `${i === 0 ? "M" : "L"} ${xScale(i)} ${yScale(r.upper)}`,
    );
    const bottom = [...filtered].reverse().map((r, revI) => {
      const i = filtered.length - 1 - revI;
      return `L ${xScale(i)} ${yScale(r.lower)}`;
    });
    return `${top.join(" ")} ${bottom.join(" ")} Z`;
  }, [filtered, xScale, yScale]);

  const actualPath = useMemo(() => {
    return filtered
      .map((r, i) => `${i === 0 ? "M" : "L"} ${xScale(i)} ${yScale(r.y_true)}`)
      .join(" ");
  }, [filtered, xScale, yScale]);

  const predPath = useMemo(() => {
    return filtered
      .map((r, i) => `${i === 0 ? "M" : "L"} ${xScale(i)} ${yScale(r.y_pred)}`)
      .join(" ");
  }, [filtered, xScale, yScale]);

  const accent = modelAccent(active);

  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-900/60 backdrop-blur-sm p-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
        <div>
          <h3 className="text-sm font-semibold text-zinc-200">
            Forecast vs actual — {horizonStep}-step ahead
          </h3>
          <p className="text-xs text-zinc-500 mt-1">
            Shaded band: 90% prediction interval across walk-forward folds
          </p>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {availableModels.map((m) => {
            const isActive = active === m;
            return (
              <button
                key={m}
                onClick={() => setActive(m)}
                className={`px-2.5 py-1 rounded-lg text-xs font-medium cursor-pointer transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 ${
                  isActive
                    ? "bg-zinc-800 text-white border border-zinc-700"
                    : "bg-zinc-900 text-zinc-400 border border-zinc-800 hover:border-zinc-700 hover:text-zinc-200"
                }`}
                style={
                  isActive
                    ? { borderColor: modelAccent(m), color: modelAccent(m) }
                    : undefined
                }
              >
                {formatModelName(m)}
              </button>
            );
          })}
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="h-[340px] flex items-center justify-center text-zinc-500 text-sm">
          No data for this model/horizon.
        </div>
      ) : (
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-auto"
          role="img"
          aria-label={`Forecast vs actual for ${active} at horizon ${horizonStep}`}
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
          {ticks.map((t) => (
            <text
              key={t.i}
              x={xScale(t.i)}
              y={height - padding.bottom + 18}
              textAnchor="middle"
              fontSize={10}
              fill="#71717a"
            >
              {t.label}
            </text>
          ))}

          <path d={bandPath} fill={accent} fillOpacity={0.12} stroke="none" />
          <path d={actualPath} fill="none" stroke="#e4e4e7" strokeWidth={1.5} />
          <path
            d={predPath}
            fill="none"
            stroke={accent}
            strokeWidth={2}
            strokeDasharray="4 3"
          />
        </svg>
      )}

      <div className="flex gap-4 text-xs text-zinc-400 mt-3">
        <span className="flex items-center gap-1.5">
          <span className="w-6 border-t border-zinc-300" aria-hidden="true" />{" "}
          actual
        </span>
        <span className="flex items-center gap-1.5">
          <span
            className="w-6 border-t-2 border-dashed"
            style={{ borderColor: accent }}
            aria-hidden="true"
          />
          forecast
        </span>
        <span className="flex items-center gap-1.5">
          <span
            className="w-6 h-2 rounded-sm"
            style={{ background: accent, opacity: 0.2 }}
            aria-hidden="true"
          />
          90% PI
        </span>
      </div>
    </div>
  );
}
