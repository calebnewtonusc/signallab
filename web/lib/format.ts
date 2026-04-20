export function formatModelName(name: string): string {
  const map: Record<string, string> = {
    naive: "Naive",
    seasonal_naive: "Seasonal Naive",
    drift: "Drift",
    moving_avg: "Moving Avg",
    moving_average: "Moving Avg",
    ets: "ETS",
    theta: "Theta",
    lag_ridge: "Lag Ridge",
    lag_regression: "Lag Regression",
  };
  return map[name] ?? name;
}

export function formatPercent(x: number, digits = 1): string {
  return `${(x * 100).toFixed(digits)}%`;
}

export function formatNumber(x: number, digits = 2): string {
  return x.toFixed(digits);
}

export function modelAccent(name: string): string {
  const palette: Record<string, string> = {
    naive: "#f97316",
    seasonal_naive: "#6366f1",
    drift: "#10b981",
    moving_avg: "#a855f7",
    moving_average: "#a855f7",
    ets: "#ec4899",
    theta: "#14b8a6",
    lag_ridge: "#38bdf8",
    lag_regression: "#38bdf8",
  };
  return palette[name] ?? "#a1a1aa";
}
