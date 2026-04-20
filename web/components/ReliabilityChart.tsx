"use client";
import { useMemo, useState } from "react";
import type { RecordRow } from "@/lib/types";
import { formatModelName, modelAccent } from "@/lib/format";

interface ReliabilityChartProps {
  records: RecordRow[];
  availableModels: string[];
  nBins?: number;
}

function normalCdf(x: number): number {
  const t = 1 / (1 + 0.2316419 * Math.abs(x));
  const d = 0.3989422804014327 * Math.exp(-0.5 * x * x);
  const p =
    d *
    t *
    (0.31938153 +
      t *
        (-0.356563782 +
          t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))));
  return x >= 0 ? 1 - p : p;
}

export function ReliabilityChart({
  records,
  availableModels,
  nBins = 10,
}: ReliabilityChartProps) {
  const [active, setActive] = useState(availableModels[0] ?? "");

  const bins = useMemo(() => {
    const rows = records.filter((r) => r.model === active);
    if (rows.length === 0)
      return [] as { nominal: number; empirical: number; count: number }[];
    const pit = rows.map((r) => {
      const sigma = Math.max(r.sigma, 1e-9);
      const z = (r.y_true - r.y_pred) / sigma;
      return Math.min(1, Math.max(0, normalCdf(z)));
    });
    const out: { nominal: number; empirical: number; count: number }[] = [];
    for (let i = 0; i < nBins; i++) {
      const lo = i / nBins;
      const hi = (i + 1) / nBins;
      const inBin = pit.filter((p) =>
        i === nBins - 1 ? p >= lo && p <= hi : p >= lo && p < hi,
      );
      const atOrBelowHi = pit.filter((p) => p <= hi).length / pit.length;
      out.push({
        nominal: (lo + hi) / 2,
        empirical: atOrBelowHi,
        count: inBin.length,
      });
    }
    return out;
  }, [records, active, nBins]);

  const width = 520;
  const height = 320;
  const padding = { top: 24, right: 24, bottom: 40, left: 48 };

  const xScale = (v: number) =>
    padding.left + v * (width - padding.left - padding.right);
  const yScale = (v: number) =>
    height - padding.bottom - v * (height - padding.top - padding.bottom);

  const pathD = bins
    .map(
      (b, i) =>
        `${i === 0 ? "M" : "L"} ${xScale(b.nominal)} ${yScale(b.empirical)}`,
    )
    .join(" ");

  const accent = modelAccent(active);

  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-900/60 backdrop-blur-sm p-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
        <div>
          <h3 className="text-sm font-semibold text-zinc-200">
            Reliability diagram
          </h3>
          <p className="text-xs text-zinc-500 mt-1">
            Calibrated forecasters hug the diagonal. Above = overconfident on
            the low end; below = overconfident on the high end.
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

      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full h-auto"
        role="img"
      >
        {[0, 0.25, 0.5, 0.75, 1].map((t) => (
          <g key={t}>
            <line
              x1={padding.left}
              x2={width - padding.right}
              y1={yScale(t)}
              y2={yScale(t)}
              stroke="rgba(255,255,255,0.05)"
              strokeDasharray="3 3"
            />
            <text
              x={padding.left - 8}
              y={yScale(t) + 3}
              textAnchor="end"
              fontSize={10}
              fill="#71717a"
            >
              {(t * 100).toFixed(0)}%
            </text>
            <text
              x={xScale(t)}
              y={height - padding.bottom + 18}
              textAnchor="middle"
              fontSize={10}
              fill="#71717a"
            >
              {(t * 100).toFixed(0)}%
            </text>
          </g>
        ))}
        <line
          x1={xScale(0)}
          x2={xScale(1)}
          y1={yScale(0)}
          y2={yScale(1)}
          stroke="#6366f1"
          strokeWidth={1.2}
          strokeDasharray="5 4"
          opacity={0.7}
        />
        <path d={pathD} fill="none" stroke={accent} strokeWidth={2} />
        {bins.map((b, i) => (
          <circle
            key={i}
            cx={xScale(b.nominal)}
            cy={yScale(b.empirical)}
            r={3.5}
            fill={accent}
          />
        ))}
      </svg>
      <div className="mt-3 flex gap-4 text-xs text-zinc-400">
        <span className="flex items-center gap-1.5">
          <span
            className="w-6 border-t-2 border-dashed border-indigo-400"
            aria-hidden="true"
          />
          perfect calibration
        </span>
        <span className="flex items-center gap-1.5">
          <span
            className="w-6 border-t-2"
            style={{ borderColor: accent }}
            aria-hidden="true"
          />
          {formatModelName(active)}
        </span>
      </div>
    </div>
  );
}
