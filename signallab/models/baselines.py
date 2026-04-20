"""Simple, hard-to-beat baseline forecasters."""
from __future__ import annotations

import numpy as np
from scipy.stats import norm

from signallab.models.base import Forecast


def _residual_sigma(residuals: np.ndarray) -> float:
    if len(residuals) < 2:
        return 1.0
    return float(max(np.std(residuals, ddof=1), 1e-9))


def _z(alpha: float) -> float:
    return float(norm.ppf(1.0 - alpha / 2.0))


class NaiveForecaster:
    name = "naive"

    def __init__(self) -> None:
        self._last: float | None = None
        self._sigma: float = 1.0

    def fit(self, y_train: np.ndarray) -> "NaiveForecaster":
        if len(y_train) == 0:
            raise ValueError("empty training data")
        self._last = float(y_train[-1])
        diffs = np.diff(y_train)
        self._sigma = _residual_sigma(diffs) if len(diffs) else 1.0
        return self

    def predict(self, horizon: int, alpha: float = 0.1) -> Forecast:
        assert self._last is not None
        mean = np.full(horizon, self._last, dtype=float)
        steps = np.arange(1, horizon + 1)
        sigma = self._sigma * np.sqrt(steps)
        z = _z(alpha)
        return Forecast(mean=mean, lower=mean - z * sigma, upper=mean + z * sigma, sigma=sigma)


class SeasonalNaiveForecaster:
    name = "seasonal_naive"

    def __init__(self, seasonality: int) -> None:
        if seasonality < 1:
            raise ValueError("seasonality must be >= 1")
        self.seasonality = seasonality
        self._last_season: np.ndarray | None = None
        self._sigma = 1.0

    def fit(self, y_train: np.ndarray) -> "SeasonalNaiveForecaster":
        s = self.seasonality
        if len(y_train) < s:
            self._last_season = np.array([y_train[-1]] * s, dtype=float)
        else:
            self._last_season = y_train[-s:].astype(float).copy()
        if len(y_train) > s:
            diffs = y_train[s:] - y_train[:-s]
            self._sigma = _residual_sigma(diffs)
        return self

    def predict(self, horizon: int, alpha: float = 0.1) -> Forecast:
        assert self._last_season is not None
        s = self.seasonality
        mean = np.array([self._last_season[i % s] for i in range(horizon)], dtype=float)
        seasons_ahead = np.arange(1, horizon + 1) / max(1, s)
        sigma = self._sigma * np.sqrt(np.ceil(seasons_ahead))
        z = _z(alpha)
        return Forecast(mean=mean, lower=mean - z * sigma, upper=mean + z * sigma, sigma=sigma)


class DriftForecaster:
    name = "drift"

    def __init__(self) -> None:
        self._last = 0.0
        self._slope = 0.0
        self._sigma = 1.0

    def fit(self, y_train: np.ndarray) -> "DriftForecaster":
        if len(y_train) < 2:
            self._last = float(y_train[-1]) if len(y_train) else 0.0
            self._slope = 0.0
            self._sigma = 1.0
            return self
        self._last = float(y_train[-1])
        self._slope = (y_train[-1] - y_train[0]) / (len(y_train) - 1)
        fitted = y_train[0] + self._slope * np.arange(len(y_train))
        self._sigma = _residual_sigma(y_train - fitted)
        return self

    def predict(self, horizon: int, alpha: float = 0.1) -> Forecast:
        steps = np.arange(1, horizon + 1)
        mean = self._last + self._slope * steps
        sigma = self._sigma * np.sqrt(steps)
        z = _z(alpha)
        return Forecast(mean=mean, lower=mean - z * sigma, upper=mean + z * sigma, sigma=sigma)


class MovingAverageForecaster:
    name = "moving_average"

    def __init__(self, window: int = 7) -> None:
        if window < 1:
            raise ValueError("window must be >= 1")
        self.window = window
        self._mean = 0.0
        self._sigma = 1.0

    def fit(self, y_train: np.ndarray) -> "MovingAverageForecaster":
        if len(y_train) == 0:
            raise ValueError("empty training data")
        w = min(self.window, len(y_train))
        self._mean = float(np.mean(y_train[-w:]))
        self._sigma = _residual_sigma(y_train - np.mean(y_train))
        return self

    def predict(self, horizon: int, alpha: float = 0.1) -> Forecast:
        mean = np.full(horizon, self._mean, dtype=float)
        sigma = np.full(horizon, self._sigma, dtype=float)
        z = _z(alpha)
        return Forecast(mean=mean, lower=mean - z * sigma, upper=mean + z * sigma, sigma=sigma)
