"""Lightweight statistical forecasters: Holt-Winters style ETS and Theta."""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm

from signallab.models.base import Forecast


def _z(alpha: float) -> float:
    return float(norm.ppf(1.0 - alpha / 2.0))


class ExponentialSmoothingForecaster:
    """Additive Holt-Winters (level + trend + optional seasonality)."""

    name = "ets"

    def __init__(self, seasonality: int = 0, damped: bool = True) -> None:
        if seasonality < 0:
            raise ValueError("seasonality must be >= 0")
        self.seasonality = seasonality
        self.damped = damped
        self.alpha = 0.5
        self.beta = 0.1
        self.gamma = 0.1
        self.phi = 0.98 if damped else 1.0
        self._level = 0.0
        self._trend = 0.0
        self._season: np.ndarray = np.zeros(0)
        self._sigma = 1.0

    def _state_iter(
        self,
        y: np.ndarray,
        alpha: float,
        beta: float,
        gamma: float,
        phi: float,
    ) -> tuple[float, float, np.ndarray, float]:
        s = self.seasonality
        if s > 0 and len(y) >= 2 * s:
            season0 = y[:s] - np.mean(y[:s])
        elif s > 0:
            season0 = np.zeros(s)
        else:
            season0 = np.zeros(0)
        level = float(y[0] if s == 0 else np.mean(y[: max(1, s)]))
        trend = 0.0
        season = season0.astype(float)
        sse = 0.0
        for t, val in enumerate(y):
            season_component = season[t % s] if s > 0 else 0.0
            fitted = level + phi * trend + season_component
            err = val - fitted
            sse += err * err
            new_level = level + phi * trend + alpha * err
            new_trend = phi * trend + beta * err
            if s > 0:
                season[t % s] = season_component + gamma * err
            level, trend = new_level, new_trend
        return level, trend, season, float(sse)

    def fit(self, y_train: np.ndarray) -> "ExponentialSmoothingForecaster":
        y = np.asarray(y_train, dtype=float)
        if len(y) < 3:
            self._level = float(y[-1]) if len(y) else 0.0
            self._trend = 0.0
            self._season = np.zeros(max(self.seasonality, 0))
            self._sigma = 1.0
            return self

        def _sigmoid(x: np.ndarray) -> np.ndarray:
            return 1.0 / (1.0 + np.exp(-np.clip(x, -30.0, 30.0)))

        def loss(params: np.ndarray) -> float:
            a, b, g = _sigmoid(params[:3])
            phi = self.phi
            _, _, _, sse = self._state_iter(y, float(a), float(b), float(g), phi)
            return sse / max(1, len(y))

        x0 = np.array([0.0, -1.0, -1.0])
        res = minimize(loss, x0, method="Nelder-Mead", options={"xatol": 1e-4, "fatol": 1e-4})
        params = res.x
        a, b, g = _sigmoid(params[:3]).tolist()
        self.alpha, self.beta, self.gamma = float(a), float(b), float(g)
        level, trend, season, sse = self._state_iter(
            y, self.alpha, self.beta, self.gamma, self.phi
        )
        self._level = level
        self._trend = trend
        self._season = season
        self._sigma = float(np.sqrt(sse / max(1, len(y) - 2)))
        return self

    def predict(self, horizon: int, alpha: float = 0.1) -> Forecast:
        h = horizon
        s = self.seasonality
        phi = self.phi
        trends = np.zeros(h)
        for i in range(h):
            trends[i] = (phi ** (i + 1) - phi) / (phi - 1.0) if phi != 1.0 else (i + 1)
        means = self._level + trends * self._trend
        if s > 0:
            means = means + np.array([self._season[i % s] for i in range(h)])
        steps = np.arange(1, h + 1)
        sigma = self._sigma * np.sqrt(steps)
        z = _z(alpha)
        return Forecast(mean=means, lower=means - z * sigma, upper=means + z * sigma, sigma=sigma)


class ThetaForecaster:
    """Theta(2) method: average of linear trend + SES on theta-line."""

    name = "theta"

    def __init__(self) -> None:
        self._b = 0.0
        self._a = 0.0
        self._n = 0
        self._ses_level = 0.0
        self._alpha = 0.5
        self._sigma = 1.0

    def fit(self, y_train: np.ndarray) -> "ThetaForecaster":
        y = np.asarray(y_train, dtype=float)
        n = len(y)
        self._n = n
        if n < 2:
            self._a = float(y[-1]) if n else 0.0
            self._b = 0.0
            self._ses_level = self._a
            self._sigma = 1.0
            return self

        t = np.arange(n)
        tbar = t.mean()
        ybar = y.mean()
        num = np.sum((t - tbar) * (y - ybar))
        den = np.sum((t - tbar) ** 2) or 1.0
        self._b = float(num / den)
        self._a = float(ybar - self._b * tbar)

        theta_line = 2 * y - (self._a + self._b * t)

        def ses_loss(a_param: float) -> float:
            level = theta_line[0]
            sse = 0.0
            for val in theta_line[1:]:
                err = val - level
                sse += err * err
                level = level + a_param * err
            return float(sse)

        best = minimize(lambda p: ses_loss(1 / (1 + np.exp(-p[0]))), x0=[0.0], method="Nelder-Mead")
        a = 1 / (1 + np.exp(-best.x[0]))
        self._alpha = float(a)
        level = theta_line[0]
        sse = 0.0
        for val in theta_line[1:]:
            err = val - level
            sse += err * err
            level = level + self._alpha * err
        self._ses_level = float(level)
        self._sigma = float(np.sqrt(sse / max(1, n - 1)))
        return self

    def predict(self, horizon: int, alpha: float = 0.1) -> Forecast:
        h = horizon
        n = self._n
        steps = np.arange(1, h + 1)
        linear = self._a + self._b * (n + steps - 1)
        ses = np.full(h, self._ses_level, dtype=float)
        mean = 0.5 * linear + 0.5 * ses
        sigma = self._sigma * np.sqrt(steps)
        z = _z(alpha)
        return Forecast(mean=mean, lower=mean - z * sigma, upper=mean + z * sigma, sigma=sigma)
