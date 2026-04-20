# SignalLab

Time-series forecasting and simulation pipeline. Walk-forward validation, calibration tracking, and distribution-shift robustness analysis in one package, with a polished showcase site.

- **Python package** — `signallab/` with models, validation, metrics, calibration, features, pipeline, CLI
- **Examples** — `examples/run_airline.py` and `examples/run_shift.py` produce real artifacts
- **Web showcase** — `web/` is a Next.js site that renders benchmark results directly from the pipeline output

## What it does

1. **Data + shift injection** — bundled airline series and synthetic generators with trend, seasonality, AR(1), drift breaks, and variance breaks. Inject controlled shifts to stress-test models.
2. **Walk-forward splits** — expanding or rolling windows, configurable horizon and step, max-fold cap.
3. **Model zoo** — `NaiveForecaster`, `SeasonalNaiveForecaster`, `DriftForecaster`, `MovingAverageForecaster`, `ExponentialSmoothingForecaster` (Holt-Winters), `ThetaForecaster`, and `LagRegressionForecaster` (recursive, sklearn-style). Every model returns mean, lower, upper, sigma.
4. **Metrics + calibration** — MAE, RMSE, MAPE, sMAPE, MASE, interval coverage, average width, pinball loss, PIT-based calibration error, rolling coverage.
5. **Split conformal prediction** — per-horizon empirical residual quantiles replace the parametric sigma widths. Turn it on with `conformal=True` in `Experiment` or `--conformal` on the CLI.

## Quick start

```bash
python -m venv .venv
.venv/bin/pip install -e .
.venv/bin/pip install pytest

# tests
.venv/bin/python -m pytest tests/ -q

# end-to-end benchmarks
.venv/bin/python examples/run_airline.py
.venv/bin/python examples/run_shift.py

# CLI
.venv/bin/signallab benchmark --dataset airline --horizon 6 --seasonality 12
.venv/bin/signallab tune-window --grid 3,7,14,21,28
```

Artifacts land in `artifacts/` as per-fold records CSV, per-horizon summary CSV, overall summary CSV, and a single `results.json` bundle.

## Library usage

```python
from signallab import Experiment, WalkForwardSplit, load_airline
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
result.save("artifacts/airline")
```

## Repo layout

```
signallab/
├── signallab/              # Python package
│   ├── data.py             # loaders + synthetic + inject_shift
│   ├── validation.py       # WalkForwardSplit
│   ├── features.py         # lag/rolling/calendar features
│   ├── metrics.py          # MAE, RMSE, MASE, pinball, interval metrics
│   ├── calibration.py      # PIT, reliability, rolling coverage
│   ├── pipeline.py         # Experiment, ExperimentResult, tune_feature_window
│   ├── reporting.py        # rich-table output
│   ├── cli.py              # typer CLI
│   └── models/
│       ├── base.py
│       ├── baselines.py    # naive, seasonal naive, drift, moving average
│       ├── statistical.py  # ETS (Holt-Winters), Theta
│       └── ml.py           # recursive lag ridge
├── tests/                  # 24 tests covering metrics, validation, models, pipeline, calibration
├── examples/               # runnable end-to-end scripts
├── artifacts/              # generated: records.csv, horizon_summary.csv, overall_summary.csv, results.json
├── web/                    # Next.js 16 showcase site (Tailwind 4, Framer Motion, Lucide)
└── pyproject.toml
```

## Web showcase

```bash
cd web
npm install
npm run dev
```

The site reads `artifacts/{airline,shift}/results.json` directly (committed into `web/app/data/` for static rendering) and renders benchmark tables, forecast-vs-actual charts, per-horizon error curves, and a rolling-coverage chart that marks where the distribution shift occurs.

## License

MIT

All glory to God! ✝️❤️
