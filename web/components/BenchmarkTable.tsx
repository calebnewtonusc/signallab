"use client";
import { useMemo, useState } from "react";
import { ArrowUpDown } from "lucide-react";
import type { OverallSummary } from "@/lib/types";
import {
  formatModelName,
  formatNumber,
  formatPercent,
  modelAccent,
} from "@/lib/format";

type SortKey =
  | "mae"
  | "rmse"
  | "smape"
  | "mase"
  | "coverage"
  | "calibration_error";

const COLUMNS: { key: SortKey; label: string; lowerBetter: boolean }[] = [
  { key: "mae", label: "MAE", lowerBetter: true },
  { key: "rmse", label: "RMSE", lowerBetter: true },
  { key: "smape", label: "sMAPE", lowerBetter: true },
  { key: "mase", label: "MASE", lowerBetter: true },
  { key: "coverage", label: "Coverage", lowerBetter: false },
  { key: "calibration_error", label: "Cal Err", lowerBetter: true },
];

export function BenchmarkTable({
  rows,
  targetCoverage,
}: {
  rows: OverallSummary[];
  targetCoverage: number;
}) {
  const [sortKey, setSortKey] = useState<SortKey>("mae");
  const [asc, setAsc] = useState(true);

  const sorted = useMemo(() => {
    const copy = [...rows];
    copy.sort((a, b) => {
      const av = a[sortKey];
      const bv = b[sortKey];
      return asc ? av - bv : bv - av;
    });
    return copy;
  }, [rows, sortKey, asc]);

  const best: Record<SortKey, number> = useMemo(() => {
    const out: Partial<Record<SortKey, number>> = {};
    for (const col of COLUMNS) {
      if (col.key === "coverage") {
        out.coverage = rows.reduce(
          (best, r) =>
            Math.abs(r.coverage - targetCoverage) <
            Math.abs(best - targetCoverage)
              ? r.coverage
              : best,
          rows[0]?.coverage ?? 0,
        );
      } else {
        out[col.key] = Math.min(...rows.map((r) => r[col.key]));
      }
    }
    return out as Record<SortKey, number>;
  }, [rows, targetCoverage]);

  const toggleSort = (k: SortKey) => {
    if (sortKey === k) setAsc(!asc);
    else {
      setSortKey(k);
      setAsc(true);
    }
  };

  return (
    <div className="overflow-x-auto rounded-2xl border border-zinc-800 bg-zinc-900/60 backdrop-blur-sm">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-xs uppercase tracking-wider text-zinc-500 border-b border-zinc-800">
            <th className="text-left px-5 py-3 font-medium">Model</th>
            {COLUMNS.map((col) => (
              <th key={col.key} className="text-right px-4 py-3 font-medium">
                <button
                  onClick={() => toggleSort(col.key)}
                  className="inline-flex items-center gap-1 hover:text-zinc-200 transition-colors cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 rounded"
                >
                  {col.label}
                  <ArrowUpDown className="w-3 h-3" aria-hidden="true" />
                </button>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((row) => (
            <tr
              key={row.model}
              className="border-b border-zinc-800/70 last:border-0 hover:bg-zinc-800/40 transition-colors"
            >
              <td className="px-5 py-3 text-zinc-200 font-medium">
                <div className="flex items-center gap-2.5">
                  <span
                    className="h-2 w-2 rounded-full"
                    style={{ background: modelAccent(row.model) }}
                    aria-hidden="true"
                  />
                  {formatModelName(row.model)}
                </div>
              </td>
              {COLUMNS.map((col) => {
                const value = row[col.key];
                const isBest =
                  col.key === "coverage"
                    ? value === best.coverage
                    : value === best[col.key];
                const display =
                  col.key === "coverage"
                    ? formatPercent(value, 1)
                    : col.key === "smape"
                      ? `${formatNumber(value, 2)}%`
                      : formatNumber(value, 3);
                return (
                  <td
                    key={col.key}
                    className={`px-4 py-3 text-right tabular-nums ${
                      isBest ? "text-indigo-300 font-semibold" : "text-zinc-400"
                    }`}
                  >
                    {display}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
