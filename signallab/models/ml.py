"""Lag regression forecaster: recursive multi-step with sklearn regressor."""
from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.linear_model import Ridge

from signallab.features import FeatureSpec, build_features, align_design_matrix
from signallab.models.base import Forecast


def _z(alpha: float) -> float:
    return float(norm.ppf(1.0 - alpha / 2.0))


class LagRegressionForecaster:
    """Recursive forecaster over lag/rolling/calendar features.

    Uses a sklearn-style regressor. Predictions are made one step at a time;
    each new prediction is appended to history so downstream lags update.
    Interval widths come from in-sample residual std scaled by sqrt(h).
    """

    name = "lag_regression"

    def __init__(
        self,
        feature_spec: FeatureSpec | None = None,
        regressor_factory: Callable[[], object] | None = None,
    ) -> None:
        self.feature_spec = feature_spec or FeatureSpec()
        self.regressor_factory = regressor_factory or (lambda: Ridge(alpha=1.0))
        self._regressor = None
        self._history: np.ndarray = np.zeros(0)
        self._index: pd.DatetimeIndex | None = None
        self._freq: str | None = None
        self._sigma = 1.0

    def _freq_str(self, index: pd.DatetimeIndex) -> str:
        inferred = pd.infer_freq(index)
        if inferred is not None:
            return inferred
        delta = index[1] - index[0]
        return pd.tseries.frequencies.to_offset(delta).freqstr

    def fit(self, y_train: np.ndarray, index: pd.DatetimeIndex | None = None) -> "LagRegressionForecaster":
        y = np.asarray(y_train, dtype=float)
        if index is None:
            index = pd.date_range(start="2000-01-01", periods=len(y), freq="D")
        self._index = pd.DatetimeIndex(index)
        self._freq = self._freq_str(self._index)
        series = pd.Series(y, index=self._index)
        df = build_features(series, self.feature_spec)
        X, y_sup, _ = align_design_matrix(df)
        if len(y_sup) < 5:
            raise ValueError("not enough rows after feature generation; reduce lags/windows")
        self._regressor = self.regressor_factory()
        self._regressor.fit(X, y_sup)
        residuals = y_sup - self._regressor.predict(X)
        self._sigma = float(max(np.std(residuals, ddof=1), 1e-9))
        self._history = y.copy()
        return self

    def predict(self, horizon: int, alpha: float = 0.1) -> Forecast:
        assert self._regressor is not None
        assert self._index is not None
        assert self._freq is not None
        history = list(self._history)
        future_index = pd.date_range(
            start=self._index[-1] + pd.tseries.frequencies.to_offset(self._freq),
            periods=horizon,
            freq=self._freq,
        )
        full_index = self._index.append(future_index)
        preds = np.zeros(horizon)
        for h in range(horizon):
            series = pd.Series(history + [np.nan] * (horizon - h), index=full_index)
            df = build_features(series, self.feature_spec)
            target_row = df.iloc[len(history)]
            feats = target_row.drop("y")
            if feats.isna().any():
                preds[h] = history[-1]
            else:
                preds[h] = float(self._regressor.predict(feats.to_numpy().reshape(1, -1))[0])
            history.append(preds[h])
        steps = np.arange(1, horizon + 1)
        sigma = self._sigma * np.sqrt(steps)
        z = _z(alpha)
        return Forecast(mean=preds, lower=preds - z * sigma, upper=preds + z * sigma, sigma=sigma)
