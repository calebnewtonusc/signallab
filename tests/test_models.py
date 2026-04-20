import numpy as np
import pandas as pd
import pytest

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


@pytest.fixture
def y_train():
    rng = np.random.default_rng(0)
    t = np.arange(100)
    return 0.05 * t + 5 * np.sin(2 * np.pi * t / 12) + rng.normal(0, 0.5, size=100)


def test_naive_predict_shape(y_train):
    fc = NaiveForecaster().fit(y_train)
    out = fc.predict(horizon=5, alpha=0.1)
    assert out.mean.shape == (5,)
    assert np.all(out.upper >= out.lower)


def test_seasonal_naive_repeats_season(y_train):
    fc = SeasonalNaiveForecaster(seasonality=12).fit(y_train)
    out = fc.predict(horizon=12)
    assert np.allclose(out.mean, y_train[-12:])


def test_drift_mean_linear(y_train):
    fc = DriftForecaster().fit(y_train)
    out = fc.predict(horizon=3)
    diffs = np.diff(out.mean)
    assert np.allclose(diffs, diffs[0])


def test_moving_average_constant_mean(y_train):
    fc = MovingAverageForecaster(window=10).fit(y_train)
    out = fc.predict(horizon=4)
    assert np.allclose(out.mean, out.mean[0])


def test_ets_and_theta_produce_finite(y_train):
    for model in [ExponentialSmoothingForecaster(seasonality=12), ThetaForecaster()]:
        out = model.fit(y_train).predict(horizon=6)
        assert np.all(np.isfinite(out.mean))
        assert np.all(out.upper > out.lower)


def test_lag_regression_fits_and_predicts():
    rng = np.random.default_rng(42)
    t = np.arange(120)
    y = 0.03 * t + 3 * np.sin(2 * np.pi * t / 7) + rng.normal(0, 0.3, size=120)
    idx = pd.date_range("2021-01-01", periods=120, freq="D")
    fc = LagRegressionForecaster(
        feature_spec=FeatureSpec(lags=(1, 2, 3, 7), rolling_windows=(7,), calendar=True)
    )
    fc.fit(y, index=idx)
    out = fc.predict(horizon=5)
    assert out.mean.shape == (5,)
    assert np.all(np.isfinite(out.mean))
