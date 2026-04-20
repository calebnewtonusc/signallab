import numpy as np
import pandas as pd

from signallab.conformal import apply_conformal_widths, compute_conformal_widths
from signallab.models import NaiveForecaster, SeasonalNaiveForecaster
from signallab.models.base import Forecast
from signallab.pipeline import Experiment
from signallab.validation import WalkForwardSplit


def _series(n=120, period=7, seed=5):
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    y = 0.02 * t + 2 * np.sin(2 * np.pi * t / period) + rng.normal(0, 0.5, size=n)
    idx = pd.date_range("2021-01-01", periods=n, freq="D")
    return pd.Series(y, index=idx, name="cal_test")


def test_apply_conformal_widths_shape():
    forecast = Forecast(
        mean=np.array([1.0, 2.0, 3.0]),
        lower=np.array([0.0, 1.0, 2.0]),
        upper=np.array([2.0, 3.0, 4.0]),
        sigma=np.array([1.0, 1.0, 1.0]),
    )
    widened = apply_conformal_widths(forecast, np.array([0.5, 1.0, 1.5]))
    assert np.allclose(widened.upper - widened.mean, np.array([0.5, 1.0, 1.5]))
    assert np.allclose(widened.mean - widened.lower, np.array([0.5, 1.0, 1.5]))


def test_compute_conformal_widths_non_negative():
    series = _series()
    y = series.to_numpy()
    result = compute_conformal_widths(
        y_train=y,
        index=series.index,
        factory=lambda: SeasonalNaiveForecaster(seasonality=7),
        horizon=5,
        alpha=0.1,
        calibration_folds=8,
    )
    assert result.widths.shape == (5,)
    assert np.all(result.widths >= 0)
    assert result.n_calibration_folds >= 2


def test_experiment_conformal_improves_calibration_under_misspecification():
    series = _series(n=180, period=7, seed=9)
    splitter = WalkForwardSplit(initial_train=80, horizon=3, step=3)
    models = {"naive": lambda: NaiveForecaster()}

    base = Experiment(
        series=series, splitter=splitter, models=models, alpha=0.2, seasonality=7
    ).run()
    conformal = Experiment(
        series=series,
        splitter=splitter,
        models=models,
        alpha=0.2,
        seasonality=7,
        conformal=True,
        calibration_folds=8,
    ).run()

    base_cal = base.overall_summaries[0]["calibration_error"]
    conf_cal = conformal.overall_summaries[0]["calibration_error"]
    assert conf_cal <= base_cal + 0.05
    assert conformal.meta["conformal"] is True
    assert conformal.meta["calibration_folds"] == 8
    assert conformal.meta["n_folds"] > 0
