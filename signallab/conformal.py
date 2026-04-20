"""Split conformal prediction intervals for multi-step forecasts.

For each training window, hold out the last `calibration_folds` mini-folds,
refit on the remaining data, collect absolute residuals per horizon step,
and take the (1-alpha) empirical quantile. That quantile is the additive
half-width used to replace the model's parametric interval.

This gives marginal (1-alpha) coverage per horizon step under exchangeability
of residuals, without assuming normality.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd

from signallab.models.base import Forecast, Forecaster
from signallab.models.ml import LagRegressionForecaster


ForecasterFactory = Callable[[], Forecaster]


@dataclass
class ConformalResult:
    widths: np.ndarray
    n_calibration_folds: int


def compute_conformal_widths(
    y_train: np.ndarray,
    index: pd.DatetimeIndex,
    factory: ForecasterFactory,
    horizon: int,
    alpha: float = 0.1,
    calibration_folds: int = 10,
) -> ConformalResult:
    """Split-conformal calibration on a single training window.

    Performs up to `calibration_folds` mini walk-forward steps at the tail of
    the training data. Returns one half-width per horizon step based on
    absolute residuals.
    """
    n = len(y_train)
    if n < horizon * 3:
        return ConformalResult(widths=np.zeros(horizon), n_calibration_folds=0)

    max_folds = max(1, min(calibration_folds, n - horizon - 2))
    residuals_by_step: list[list[float]] = [[] for _ in range(horizon)]

    for i in range(max_folds):
        end = n - horizon - i
        if end < 2:
            break
        y_core = y_train[:end]
        y_calib = y_train[end : end + horizon]
        if len(y_calib) < horizon:
            break
        idx_core = index[:end]
        try:
            model = factory()
            if isinstance(model, LagRegressionForecaster):
                model.fit(y_core, index=idx_core)
            else:
                model.fit(y_core)
            forecast = model.predict(horizon, alpha=alpha)
        except Exception:
            continue
        for h in range(horizon):
            residuals_by_step[h].append(abs(y_calib[h] - forecast.mean[h]))

    widths = np.zeros(horizon)
    q = 1.0 - alpha
    for h in range(horizon):
        arr = np.asarray(residuals_by_step[h])
        if arr.size == 0:
            widths[h] = 0.0
            continue
        n_res = arr.size
        rank = np.ceil((n_res + 1) * q) / n_res
        rank = min(max(rank, 0.0), 1.0)
        widths[h] = float(np.quantile(arr, rank, method="higher"))

    actual_folds = sum(1 for arr in residuals_by_step if len(arr) > 0)
    return ConformalResult(widths=widths, n_calibration_folds=actual_folds)


def apply_conformal_widths(forecast: Forecast, widths: np.ndarray) -> Forecast:
    if widths.shape != forecast.mean.shape:
        raise ValueError(
            f"widths shape {widths.shape} != forecast shape {forecast.mean.shape}"
        )
    return Forecast(
        mean=forecast.mean,
        lower=forecast.mean - widths,
        upper=forecast.mean + widths,
        sigma=forecast.sigma,
    )
