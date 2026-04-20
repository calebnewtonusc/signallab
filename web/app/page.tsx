import {
  Activity,
  BarChart3,
  Boxes,
  Braces,
  CheckCircle2,
  Gauge,
  GitBranch,
  LineChart,
  SlidersHorizontal,
  Sparkles,
  Target,
  Terminal,
  Waves,
} from "lucide-react";
import { Navbar } from "@/components/Navbar";
import { Reveal } from "@/components/Reveal";
import { BenchmarkTable } from "@/components/BenchmarkTable";
import { ForecastChart } from "@/components/ForecastChart";
import { HorizonChart } from "@/components/HorizonChart";
import { CoverageChart } from "@/components/CoverageChart";
import airlineResults from "./data/airline.json";
import shiftResults from "./data/shift.json";
import airlineRecords from "./data/airline_records.json";
import shiftRecords from "./data/shift_records.json";
import type { RecordRow, ResultsFile } from "@/lib/types";

const airline = airlineResults as ResultsFile;
const shift = shiftResults as ResultsFile;
const airlineRecs = airlineRecords as RecordRow[];
const shiftRecs = shiftRecords as RecordRow[];

const BENCHMARK_MODELS = [
  "naive",
  "seasonal_naive",
  "drift",
  "moving_avg",
  "ets",
  "theta",
  "lag_ridge",
];

const CLI_SNIPPET = `# Run the end-to-end benchmark on a monthly series
signallab benchmark \\
  --dataset airline \\
  --horizon 6 \\
  --initial-train 72 \\
  --mode expanding \\
  --seasonality 12 \\
  --alpha 0.1 \\
  --outdir artifacts/run

# Sweep lag-window size for the regression model
signallab tune-window \\
  --dataset synthetic \\
  --horizon 7 \\
  --grid 3,7,14,21,28`;

const EXPERIMENT_SNIPPET = `from signallab import Experiment, WalkForwardSplit, load_airline
from signallab.models import SeasonalNaiveForecaster, ThetaForecaster, LagRegressionForecaster
from signallab.features import FeatureSpec

series = load_airline()
splitter = WalkForwardSplit(initial_train=72, horizon=6, step=1, mode="expanding")

experiment = Experiment(
    series=series,
    splitter=splitter,
    models={
        "seasonal_naive": lambda: SeasonalNaiveForecaster(seasonality=12),
        "theta": lambda: ThetaForecaster(),
        "lag_ridge": lambda: LagRegressionForecaster(
            feature_spec=FeatureSpec(lags=(1, 2, 3, 7, 14), calendar=True),
        ),
    },
    alpha=0.1,
    seasonality=12,
)

result = experiment.run()
result.save("artifacts/airline")`;

export default function Home() {
  return (
    <>
      <Navbar />
      <main id="top" className="flex-1">
        <section className="relative overflow-hidden">
          <div className="absolute inset-0 grid-pattern" aria-hidden="true" />
          <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-28 md:pt-36 pb-20 md:pb-28">
            <Reveal>
              <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                <Sparkles className="w-3.5 h-3.5" aria-hidden="true" />
                Forecasting, honestly evaluated
              </span>
            </Reveal>
            <Reveal delay={80}>
              <h1 className="mt-6 text-5xl md:text-7xl font-bold tracking-tight gradient-text leading-[1.02] max-w-4xl">
                Forecasts that hold up when the world moves.
              </h1>
            </Reveal>
            <Reveal delay={160}>
              <p className="mt-6 text-lg md:text-xl text-zinc-400 max-w-2xl leading-relaxed">
                SignalLab is a Python pipeline for time-series forecasting and
                simulation. It runs walk-forward validation, benchmarks
                baselines head-to-head, tracks calibration fold by fold, and
                surfaces where your model breaks under distribution shift.
              </p>
            </Reveal>
            <Reveal delay={240}>
              <div className="mt-9 flex flex-wrap items-center gap-3">
                <a
                  href="#benchmarks"
                  className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 transition-all duration-200 cursor-pointer"
                >
                  See live benchmarks
                  <BarChart3 className="w-4 h-4" aria-hidden="true" />
                </a>
                <a
                  href="#cli"
                  className="inline-flex items-center gap-2 rounded-xl border border-zinc-800 bg-zinc-900 hover:bg-zinc-800 hover:border-zinc-700 px-5 py-2.5 text-sm font-medium text-zinc-100 transition-all duration-200 cursor-pointer"
                >
                  <Terminal className="w-4 h-4" aria-hidden="true" />
                  CLI in 30 seconds
                </a>
              </div>
            </Reveal>

            <Reveal delay={320}>
              <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-px rounded-2xl overflow-hidden border border-zinc-800 bg-zinc-800">
                {[
                  { label: "Baselines benchmarked", value: "7", icon: Boxes },
                  {
                    label: "Walk-forward folds",
                    value: `${airline.meta.n_obs - airline.meta.initial_train}+`,
                    icon: GitBranch,
                  },
                  {
                    label: "Coverage tracked",
                    value: `${((1 - airline.meta.alpha) * 100).toFixed(0)}%`,
                    icon: Target,
                  },
                  { label: "Shift scenarios", value: "3", icon: Waves },
                ].map((stat) => (
                  <div
                    key={stat.label}
                    className="bg-zinc-950/80 px-5 py-6 flex items-start gap-3"
                  >
                    <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-400">
                      <stat.icon className="w-4 h-4" aria-hidden="true" />
                    </span>
                    <div>
                      <div className="text-2xl font-semibold text-white tabular-nums">
                        {stat.value}
                      </div>
                      <div className="text-xs text-zinc-500 mt-0.5">
                        {stat.label}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Reveal>
          </div>
        </section>

        <section id="benchmarks" className="relative border-t border-zinc-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28">
            <Reveal>
              <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6 mb-10">
                <div className="max-w-2xl">
                  <div className="text-xs uppercase tracking-wider text-indigo-400 font-semibold mb-3">
                    Live benchmark output
                  </div>
                  <h2 className="text-3xl md:text-4xl font-semibold tracking-tight text-white">
                    Airline passengers, 89 walk-forward folds, h = 6.
                  </h2>
                  <p className="mt-4 text-zinc-400 text-base leading-relaxed">
                    Every metric below is recomputed from the artifacts
                    SignalLab wrote on the last run. Best-in-column values
                    highlighted. Target coverage is{" "}
                    {((1 - airline.meta.alpha) * 100).toFixed(0)}% : models that
                    over- or under-shoot it are miscalibrated, not just
                    inaccurate.
                  </p>
                </div>
                <div className="flex flex-wrap gap-2 text-xs">
                  {["expanding window", "α = 0.10", "seasonality = 12"].map(
                    (tag) => (
                      <span
                        key={tag}
                        className="px-2.5 py-1 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-400"
                      >
                        {tag}
                      </span>
                    ),
                  )}
                </div>
              </div>
            </Reveal>

            <Reveal delay={80}>
              <BenchmarkTable
                rows={airline.overall}
                targetCoverage={1 - airline.meta.alpha}
              />
            </Reveal>

            <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Reveal delay={120}>
                <ForecastChart
                  records={airlineRecs}
                  horizonStep={1}
                  availableModels={BENCHMARK_MODELS}
                />
              </Reveal>
              <Reveal delay={180}>
                <HorizonChart
                  horizons={airline.horizons}
                  metric="mae"
                  title="How error grows with horizon"
                />
              </Reveal>
            </div>
          </div>
        </section>

        <section id="pipeline" className="relative border-t border-zinc-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28">
            <Reveal>
              <div className="max-w-2xl">
                <div className="text-xs uppercase tracking-wider text-indigo-400 font-semibold mb-3">
                  The pipeline
                </div>
                <h2 className="text-3xl md:text-4xl font-semibold tracking-tight text-white">
                  From raw series to honest metrics in four steps.
                </h2>
                <p className="mt-4 text-zinc-400 text-base leading-relaxed">
                  Each step is a single module, tested, and swappable. Plug in a
                  custom splitter, your own model, or a different metric without
                  touching the rest of the stack.
                </p>
              </div>
            </Reveal>

            <div className="mt-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
              {[
                {
                  icon: Waves,
                  title: "1. Data + shift injection",
                  body: "Load bundled series or generate synthetic ones with drift, variance breaks, and AR(1) noise. Inject controlled shifts to stress-test models.",
                  accent: "text-sky-400 bg-sky-500/10",
                },
                {
                  icon: GitBranch,
                  title: "2. Walk-forward splits",
                  body: "Expanding or rolling windows with configurable horizon and step. Every fold is a real out-of-sample evaluation, no leakage.",
                  accent: "text-indigo-400 bg-indigo-500/10",
                },
                {
                  icon: Boxes,
                  title: "3. Model zoo",
                  body: "Naive, seasonal naive, drift, moving average, Holt-Winters ETS, Theta, and a ridge lag regressor. Bring your own by implementing fit and predict.",
                  accent: "text-violet-400 bg-violet-500/10",
                },
                {
                  icon: Gauge,
                  title: "4. Metrics + calibration",
                  body: "Point errors (MAE, RMSE, MASE), interval coverage and width, pinball loss at lower and upper quantiles, PIT-based calibration error.",
                  accent: "text-emerald-400 bg-emerald-500/10",
                },
              ].map((card, i) => (
                <Reveal key={card.title} delay={60 * i}>
                  <div className="h-full rounded-2xl border border-zinc-800 bg-zinc-900/60 backdrop-blur-sm p-6 hover:border-zinc-700 transition-colors">
                    <span
                      className={`inline-flex h-10 w-10 items-center justify-center rounded-xl ${card.accent}`}
                    >
                      <card.icon className="w-5 h-5" aria-hidden="true" />
                    </span>
                    <h3 className="mt-4 text-base font-semibold text-zinc-100">
                      {card.title}
                    </h3>
                    <p className="mt-2 text-sm text-zinc-400 leading-relaxed">
                      {card.body}
                    </p>
                  </div>
                </Reveal>
              ))}
            </div>
          </div>
        </section>

        <section id="calibration" className="relative border-t border-zinc-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28">
            <div className="grid grid-cols-1 lg:grid-cols-5 gap-10 items-start">
              <Reveal className="lg:col-span-2">
                <div className="text-xs uppercase tracking-wider text-indigo-400 font-semibold mb-3">
                  Calibration, not just accuracy
                </div>
                <h2 className="text-3xl md:text-4xl font-semibold tracking-tight text-white">
                  A confidence interval that is not calibrated is a lie.
                </h2>
                <p className="mt-4 text-zinc-400 text-base leading-relaxed">
                  A 90% interval should contain the truth 90% of the time, not
                  62%, not 99%. SignalLab tracks the Probability Integral
                  Transform of every prediction, bins it into reliability
                  diagrams, and reports the weighted calibration error per model
                  and per horizon.
                </p>
                <ul className="mt-6 space-y-3 text-sm text-zinc-300">
                  {[
                    "Empirical vs nominal coverage, broken down by horizon step.",
                    "Rolling-window coverage so you can see drift as it happens.",
                    "Pinball loss at the lower and upper prediction quantiles.",
                  ].map((point) => (
                    <li key={point} className="flex items-start gap-2.5">
                      <CheckCircle2
                        className="w-4 h-4 text-indigo-400 mt-0.5 flex-shrink-0"
                        aria-hidden="true"
                      />
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </Reveal>

              <Reveal delay={100} className="lg:col-span-3">
                <HorizonChart
                  horizons={airline.horizons}
                  metric="smape"
                  title="sMAPE by forecast horizon"
                />
                <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {airline.overall
                    .slice()
                    .sort((a, b) => a.calibration_error - b.calibration_error)
                    .slice(0, 4)
                    .map((row) => (
                      <div
                        key={row.model}
                        className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-4"
                      >
                        <div className="text-xs text-zinc-500">
                          {row.model.replace("_", " ")}
                        </div>
                        <div className="mt-1 text-xl font-semibold text-white tabular-nums">
                          {(row.calibration_error * 100).toFixed(1)}
                          <span className="text-sm text-zinc-500 ml-1">
                            cal err
                          </span>
                        </div>
                        <div className="mt-1 text-xs text-zinc-500 tabular-nums">
                          coverage {(row.coverage * 100).toFixed(1)}%
                        </div>
                      </div>
                    ))}
                </div>
              </Reveal>
            </div>
          </div>
        </section>

        <section id="shift" className="relative border-t border-zinc-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28">
            <Reveal>
              <div className="max-w-2xl">
                <div className="text-xs uppercase tracking-wider text-indigo-400 font-semibold mb-3">
                  Distribution shift, at t = 220
                </div>
                <h2 className="text-3xl md:text-4xl font-semibold tracking-tight text-white">
                  When the series changes, which models recover?
                </h2>
                <p className="mt-4 text-zinc-400 text-base leading-relaxed">
                  A 3.5 sigma level shift is injected into a synthetic seasonal
                  series. Rolling coverage is tracked across folds. The red
                  marker shows the shift; the dashed line is the nominal target.
                  Faster recovery means better robustness.
                </p>
              </div>
            </Reveal>
            <Reveal delay={100}>
              <div className="mt-10">
                <CoverageChart
                  rollingCoverage={shift.rolling_coverage}
                  target={1 - shift.meta.alpha}
                  shiftIndex={Math.max(
                    0,
                    Math.floor(
                      (220 - shift.meta.initial_train) / shift.meta.step,
                    ),
                  )}
                />
              </div>
            </Reveal>

            <Reveal delay={160}>
              <div className="mt-10 grid grid-cols-1 lg:grid-cols-2 gap-6">
                <ForecastChart
                  records={shiftRecs}
                  horizonStep={1}
                  availableModels={[
                    "naive",
                    "seasonal_naive",
                    "drift",
                    "ets",
                    "theta",
                    "lag_ridge",
                  ]}
                />
                <div className="rounded-2xl border border-zinc-800 bg-zinc-900/60 backdrop-blur-sm p-6">
                  <h3 className="text-sm font-semibold text-zinc-200">
                    Post-shift benchmark
                  </h3>
                  <p className="text-xs text-zinc-500 mt-1 mb-5">
                    Aggregated across all folds on the shifted series.
                  </p>
                  <BenchmarkTable
                    rows={shift.overall}
                    targetCoverage={1 - shift.meta.alpha}
                  />
                </div>
              </div>
            </Reveal>
          </div>
        </section>

        <section id="cli" className="relative border-t border-zinc-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-start">
              <Reveal>
                <div className="text-xs uppercase tracking-wider text-indigo-400 font-semibold mb-3">
                  Ship it
                </div>
                <h2 className="text-3xl md:text-4xl font-semibold tracking-tight text-white">
                  One command. Real artifacts.
                </h2>
                <p className="mt-4 text-zinc-400 text-base leading-relaxed">
                  Run a full benchmark or a feature-window sweep from the
                  terminal. Outputs include per-fold records, per-horizon
                  summaries, overall metrics, rolling coverage, and a single
                  JSON bundle ready for downstream dashboards.
                </p>
                <div className="mt-8 space-y-3">
                  {[
                    {
                      icon: SlidersHorizontal,
                      label: "Tune windows",
                      body: "signallab tune-window --grid 3,7,14,21,28",
                    },
                    {
                      icon: LineChart,
                      label: "Benchmark",
                      body: "signallab benchmark --dataset airline",
                    },
                    {
                      icon: Braces,
                      label: "Import as a library",
                      body: "from signallab import Experiment, WalkForwardSplit",
                    },
                  ].map((row) => (
                    <div
                      key={row.label}
                      className="flex items-start gap-3 rounded-xl border border-zinc-800 bg-zinc-900/60 p-4"
                    >
                      <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-400">
                        <row.icon className="w-4 h-4" aria-hidden="true" />
                      </span>
                      <div>
                        <div className="text-sm font-semibold text-zinc-100">
                          {row.label}
                        </div>
                        <code className="text-xs text-zinc-400 font-mono">
                          {row.body}
                        </code>
                      </div>
                    </div>
                  ))}
                </div>
              </Reveal>
              <Reveal delay={100}>
                <div className="grid gap-5">
                  <div className="rounded-2xl border border-zinc-800 bg-zinc-950 overflow-hidden">
                    <div className="flex items-center justify-between px-4 py-2 border-b border-zinc-800 bg-zinc-900/60">
                      <div className="flex items-center gap-1.5">
                        <span
                          className="h-2.5 w-2.5 rounded-full bg-rose-500/80"
                          aria-hidden="true"
                        />
                        <span
                          className="h-2.5 w-2.5 rounded-full bg-amber-400/80"
                          aria-hidden="true"
                        />
                        <span
                          className="h-2.5 w-2.5 rounded-full bg-emerald-500/80"
                          aria-hidden="true"
                        />
                      </div>
                      <span className="text-xs text-zinc-500 font-mono">
                        signallab.sh
                      </span>
                    </div>
                    <pre className="p-5 text-xs text-zinc-300 font-mono leading-relaxed overflow-x-auto">
                      <code>{CLI_SNIPPET}</code>
                    </pre>
                  </div>
                  <div className="rounded-2xl border border-zinc-800 bg-zinc-950 overflow-hidden">
                    <div className="flex items-center justify-between px-4 py-2 border-b border-zinc-800 bg-zinc-900/60">
                      <div className="flex items-center gap-1.5">
                        <span
                          className="h-2.5 w-2.5 rounded-full bg-rose-500/80"
                          aria-hidden="true"
                        />
                        <span
                          className="h-2.5 w-2.5 rounded-full bg-amber-400/80"
                          aria-hidden="true"
                        />
                        <span
                          className="h-2.5 w-2.5 rounded-full bg-emerald-500/80"
                          aria-hidden="true"
                        />
                      </div>
                      <span className="text-xs text-zinc-500 font-mono">
                        experiment.py
                      </span>
                    </div>
                    <pre className="p-5 text-xs text-zinc-300 font-mono leading-relaxed overflow-x-auto">
                      <code>{EXPERIMENT_SNIPPET}</code>
                    </pre>
                  </div>
                </div>
              </Reveal>
            </div>
          </div>
        </section>

        <section className="relative border-t border-zinc-900">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28 text-center">
            <Reveal>
              <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                <Activity className="w-3.5 h-3.5" aria-hidden="true" />
                Open source
              </span>
              <h2 className="mt-5 text-4xl md:text-5xl font-semibold tracking-tight gradient-text">
                Benchmark your forecasts.
                <br />
                Trust your intervals.
              </h2>
              <p className="mt-5 text-zinc-400 max-w-xl mx-auto">
                Clone the repo, run the benchmark, and know exactly where your
                model breaks before it goes to production.
              </p>
              <div className="mt-8 flex flex-wrap justify-center gap-3">
                <a
                  href="https://github.com/calebnewtonusc/signallab"
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 transition-all duration-200 cursor-pointer"
                >
                  View on GitHub
                </a>
                <a
                  href="#benchmarks"
                  className="inline-flex items-center gap-2 rounded-xl border border-zinc-800 bg-zinc-900 hover:bg-zinc-800 hover:border-zinc-700 px-5 py-2.5 text-sm font-medium text-zinc-100 transition-all duration-200 cursor-pointer"
                >
                  Read the benchmarks
                </a>
              </div>
            </Reveal>
          </div>
        </section>

        <footer className="border-t border-zinc-900 bg-zinc-950/60">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-zinc-500">
            <div className="flex items-center gap-2">
              <span className="flex h-6 w-6 items-center justify-center rounded-md bg-indigo-500/10 text-indigo-400">
                <Activity className="w-3.5 h-3.5" aria-hidden="true" />
              </span>
              <span>SignalLab · built by Caleb Newton</span>
            </div>
            <div className="flex items-center gap-5">
              <a href="#top" className="hover:text-zinc-200 transition-colors">
                Top
              </a>
              <a
                href="#benchmarks"
                className="hover:text-zinc-200 transition-colors"
              >
                Benchmarks
              </a>
              <a
                href="https://github.com/calebnewtonusc/signallab"
                target="_blank"
                rel="noreferrer"
                className="hover:text-zinc-200 transition-colors"
              >
                GitHub
              </a>
            </div>
          </div>
        </footer>
      </main>
    </>
  );
}
