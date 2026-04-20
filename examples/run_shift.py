"""Synthetic series with an injected distribution shift at t=220.

Shows how coverage and calibration drift post-shift and which baselines
recover faster. Writes artifacts/shift/ for the showcase site to read.
"""
from pathlib import Path

from signallab.data import SeriesSpec, generate_synthetic_series, inject_shift
from signallab.features import FeatureSpec
from signallab.models import (
    DriftForecaster,
    ExponentialSmoothingForecaster,
    LagRegressionForecaster,
    NaiveForecaster,
    SeasonalNaiveForecaster,
    ThetaForecaster,
)
from signallab.pipeline import Experiment
from signallab.reporting import print_overall
from signallab.validation import WalkForwardSplit


def main() -> None:
    spec = SeriesSpec(
        name="synthetic_shift",
        n=360,
        freq="D",
        trend=0.015,
        seasonal_period=7,
        seasonal_amp=2.5,
        noise=0.8,
        ar1=0.25,
    )
    series = generate_synthetic_series(spec, seed=11)
    series = inject_shift(series, at=220, kind="level", magnitude=3.5)

    splitter = WalkForwardSplit(initial_train=120, horizon=7, step=3, mode="rolling")
    models = {
        "naive": lambda: NaiveForecaster(),
        "seasonal_naive": lambda: SeasonalNaiveForecaster(seasonality=7),
        "drift": lambda: DriftForecaster(),
        "ets": lambda: ExponentialSmoothingForecaster(seasonality=7),
        "theta": lambda: ThetaForecaster(),
        "lag_ridge": lambda: LagRegressionForecaster(
            feature_spec=FeatureSpec(lags=(1, 2, 3, 7, 14), rolling_windows=(7, 14), calendar=True)
        ),
    }
    experiment = Experiment(
        series=series,
        splitter=splitter,
        models=models,
        alpha=0.1,
        seasonality=7,
        conformal=True,
        calibration_folds=10,
    )
    result = experiment.run()
    print_overall(result)
    out = result.save(Path("artifacts/shift"))
    print(f"Artifacts written to {out.resolve()}")


if __name__ == "__main__":
    main()
