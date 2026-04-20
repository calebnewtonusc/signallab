"""Point and probabilistic forecast metrics."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


EPS = 1e-12


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    denom = np.where(np.abs(y_true) < EPS, EPS, np.abs(y_true))
    return float(np.mean(np.abs((y_true - y_pred) / denom)) * 100.0)


def smape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    denom = (np.abs(y_true) + np.abs(y_pred)) / 2.0
    denom = np.where(denom < EPS, EPS, denom)
    return float(np.mean(np.abs(y_true - y_pred) / denom) * 100.0)


def mase(y_true: np.ndarray, y_pred: np.ndarray, y_train: np.ndarray, seasonality: int = 1) -> float:
    if len(y_train) <= seasonality:
        scale = np.mean(np.abs(np.diff(y_train))) if len(y_train) > 1 else EPS
    else:
        scale = float(np.mean(np.abs(y_train[seasonality:] - y_train[:-seasonality])))
    scale = max(scale, EPS)
    return float(np.mean(np.abs(y_true - y_pred)) / scale)


def pinball_loss(y_true: np.ndarray, y_pred_quantile: np.ndarray, q: float) -> float:
    diff = y_true - y_pred_quantile
    return float(np.mean(np.maximum(q * diff, (q - 1.0) * diff)))


@dataclass
class PointReport:
    mae: float
    rmse: float
    mape: float
    smape: float
    mase: float


def point_metrics(
    y_true: np.ndarray, y_pred: np.ndarray, y_train: np.ndarray, seasonality: int = 1
) -> PointReport:
    return PointReport(
        mae=mae(y_true, y_pred),
        rmse=rmse(y_true, y_pred),
        mape=mape(y_true, y_pred),
        smape=smape(y_true, y_pred),
        mase=mase(y_true, y_pred, y_train, seasonality=seasonality),
    )


@dataclass
class IntervalReport:
    coverage: float
    avg_width: float
    pinball_lower: float
    pinball_upper: float


def interval_metrics(
    y_true: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    alpha: float = 0.1,
) -> IntervalReport:
    inside = (y_true >= lower) & (y_true <= upper)
    q_lo = alpha / 2.0
    q_hi = 1.0 - alpha / 2.0
    return IntervalReport(
        coverage=float(np.mean(inside)),
        avg_width=float(np.mean(upper - lower)),
        pinball_lower=pinball_loss(y_true, lower, q_lo),
        pinball_upper=pinball_loss(y_true, upper, q_hi),
    )
