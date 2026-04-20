"""SignalLab command-line interface."""
from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from signallab.data import SeriesSpec, generate_synthetic_series, inject_shift, load_airline
from signallab.features import FeatureSpec
from signallab.models import (
    DriftForecaster,
    ExponentialSmoothingForecaster,
    LagRegressionForecaster,
    MovingAverageForecaster,
    NaiveForecaster,
    SeasonalNaiveForecaster,
    ThetaForecaster,
)
from signallab.pipeline import Experiment
from signallab.reporting import print_horizon_breakdown, print_overall
from signallab.validation import WalkForwardSplit


app = typer.Typer(help="SignalLab: time-series forecasting benchmarks and calibration.")
console = Console()


def _default_models(seasonality: int) -> dict:
    return {
        "naive": lambda: NaiveForecaster(),
        "seasonal_naive": lambda: SeasonalNaiveForecaster(seasonality=max(2, seasonality)),
        "drift": lambda: DriftForecaster(),
        "moving_avg": lambda: MovingAverageForecaster(window=max(3, seasonality)),
        "ets": lambda: ExponentialSmoothingForecaster(seasonality=seasonality if seasonality > 1 else 0),
        "theta": lambda: ThetaForecaster(),
        "lag_ridge": lambda: LagRegressionForecaster(
            feature_spec=FeatureSpec(lags=(1, 2, 3, 7, 14), rolling_windows=(7, 28), calendar=True)
        ),
    }


@app.command()
def benchmark(
    dataset: str = typer.Option("airline", help="'airline' or 'synthetic'."),
    horizon: int = typer.Option(6, help="Forecast horizon per fold."),
    initial_train: int = typer.Option(72, help="Initial training window."),
    step: int = typer.Option(1, help="Walk-forward step size."),
    mode: str = typer.Option("expanding", help="'expanding' or 'rolling'."),
    alpha: float = typer.Option(0.1, help="Miscoverage target (1-alpha coverage)."),
    seasonality: int = typer.Option(12, help="Series seasonality."),
    shift_at: int = typer.Option(0, help="Inject distribution shift at this index (0 = none)."),
    shift_kind: str = typer.Option("level"),
    shift_magnitude: float = typer.Option(3.0),
    conformal: bool = typer.Option(True, help="Use split conformal prediction intervals."),
    calibration_folds: int = typer.Option(10, help="Calibration folds for conformal quantile."),
    outdir: str = typer.Option("artifacts/run", help="Where to write csvs and json."),
) -> None:
    """Run a multi-model walk-forward benchmark and write artifacts."""
    if dataset == "airline":
        series = load_airline()
    elif dataset == "synthetic":
        spec = SeriesSpec(
            name="synthetic",
            n=360,
            freq="D",
            trend=0.02,
            seasonal_period=7,
            seasonal_amp=3.0,
            noise=1.0,
            ar1=0.3,
        )
        series = generate_synthetic_series(spec, seed=7)
    else:
        raise typer.BadParameter("dataset must be 'airline' or 'synthetic'")

    if shift_at > 0:
        series = inject_shift(series, at=shift_at, kind=shift_kind, magnitude=shift_magnitude)

    splitter = WalkForwardSplit(
        initial_train=initial_train, horizon=horizon, step=step, mode=mode
    )
    models = _default_models(seasonality=seasonality)
    experiment = Experiment(
        series=series,
        splitter=splitter,
        models=models,
        alpha=alpha,
        seasonality=seasonality if seasonality > 1 else 1,
        conformal=conformal,
        calibration_folds=calibration_folds,
    )
    result = experiment.run()

    print_overall(result, console=console)
    print_horizon_breakdown(result, console=console)

    out = result.save(Path(outdir))
    console.print(f"\n[bold green]Artifacts written to[/bold green] {out.resolve()}")


@app.command("tune-window")
def tune_window(
    dataset: str = typer.Option("airline"),
    horizon: int = typer.Option(6),
    initial_train: int = typer.Option(72),
    grid: str = typer.Option("3,7,14,21,28"),
    outdir: str = typer.Option("artifacts/tune"),
) -> None:
    """Sweep max-lag window on the lag regression model and print results."""
    from signallab.pipeline import tune_feature_window

    if dataset == "airline":
        series = load_airline()
    else:
        spec = SeriesSpec(
            name="synthetic",
            n=360,
            freq="D",
            trend=0.02,
            seasonal_period=7,
            seasonal_amp=3.0,
            noise=1.0,
        )
        series = generate_synthetic_series(spec, seed=7)

    lag_grid = [int(x) for x in grid.split(",") if x.strip()]
    splitter = WalkForwardSplit(initial_train=initial_train, horizon=horizon, step=1)

    def make_factory(max_lag: int):
        def _factory():
            lags = tuple(i for i in [1, 2, 3, 7, 14, 21, 28] if i <= max_lag)
            return LagRegressionForecaster(feature_spec=FeatureSpec(lags=lags, rolling_windows=(min(max_lag, 7),)))
        return _factory

    table = tune_feature_window(
        series=series, splitter=splitter, lag_grid=lag_grid, factory_template=make_factory
    )

    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    table.to_csv(out / "tuning.csv", index=False)
    console.print(table.to_string(index=False))
    console.print(f"\n[bold green]Written:[/bold green] {(out / 'tuning.csv').resolve()}")


if __name__ == "__main__":
    app()
