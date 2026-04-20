import numpy as np
import pandas as pd

from signallab.features import FeatureSpec
from signallab.models import LagRegressionForecaster, NaiveForecaster, SeasonalNaiveForecaster
from signallab.pipeline import Experiment
from signallab.validation import WalkForwardSplit


def _series(n=100, period=7, seed=1):
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    y = 0.02 * t + 2 * np.sin(2 * np.pi * t / period) + rng.normal(0, 0.3, size=n)
    idx = pd.date_range("2021-01-01", periods=n, freq="D")
    return pd.Series(y, index=idx, name="test")


def test_experiment_runs_end_to_end():
    series = _series()
    splitter = WalkForwardSplit(initial_train=60, horizon=3, step=2)
    models = {
        "naive": lambda: NaiveForecaster(),
        "seasonal_naive": lambda: SeasonalNaiveForecaster(seasonality=7),
    }
    exp = Experiment(series=series, splitter=splitter, models=models, alpha=0.2, seasonality=7)
    result = exp.run()
    assert len(result.records) > 0
    assert len(result.overall_summaries) == 2
    overall = {row["model"]: row for row in result.overall_summaries}
    assert overall["seasonal_naive"]["mae"] < overall["naive"]["mae"]


def test_experiment_includes_lag_regression():
    series = _series(n=80, period=7, seed=3)
    splitter = WalkForwardSplit(initial_train=50, horizon=3, step=3)
    models = {
        "lag": lambda: LagRegressionForecaster(
            feature_spec=FeatureSpec(lags=(1, 2, 7), rolling_windows=(7,), calendar=True)
        ),
    }
    exp = Experiment(series=series, splitter=splitter, models=models, alpha=0.2, seasonality=7)
    result = exp.run()
    assert any(row["model"] == "lag" for row in result.overall_summaries)
    for row in result.overall_summaries:
        assert row["coverage"] >= 0.0 and row["coverage"] <= 1.0


def test_save_writes_expected_files(tmp_path):
    series = _series(n=70, period=7)
    splitter = WalkForwardSplit(initial_train=50, horizon=3, step=3)
    exp = Experiment(
        series=series,
        splitter=splitter,
        models={"naive": lambda: NaiveForecaster()},
        alpha=0.2,
        seasonality=7,
    )
    result = exp.run()
    out = result.save(tmp_path / "run")
    for name in ("records.csv", "horizon_summary.csv", "overall_summary.csv", "results.json"):
        assert (out / name).exists()
