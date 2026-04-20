"""Calibration tracking: PIT, coverage drift, reliability diagrams."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import norm


def pit_values(y_true: np.ndarray, mu: np.ndarray, sigma: np.ndarray) -> np.ndarray:
    sigma = np.where(sigma <= 0, 1e-9, sigma)
    return norm.cdf(y_true, loc=mu, scale=sigma)


def coverage(y_true: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> float:
    return float(np.mean((y_true >= lower) & (y_true <= upper)))


@dataclass
class ReliabilityBin:
    nominal: float
    empirical: float
    count: int


def reliability_bins(pit: np.ndarray, n_bins: int = 10) -> list[ReliabilityBin]:
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    bins: list[ReliabilityBin] = []
    for i in range(n_bins):
        lo, hi = edges[i], edges[i + 1]
        mask = (pit >= lo) & (pit < hi) if i < n_bins - 1 else (pit >= lo) & (pit <= hi)
        count = int(mask.sum())
        nominal = (lo + hi) / 2.0
        empirical = float(np.mean(pit <= hi))
        bins.append(ReliabilityBin(nominal=nominal, empirical=empirical, count=count))
    return bins


def calibration_error(pit: np.ndarray, n_bins: int = 10) -> float:
    bins = reliability_bins(pit, n_bins=n_bins)
    total = sum(b.count for b in bins) or 1
    weighted = 0.0
    for b in bins:
        weight = b.count / total
        weighted += weight * abs(b.nominal - b.empirical)
    return float(weighted)


def rolling_coverage(
    y_true: np.ndarray, lower: np.ndarray, upper: np.ndarray, window: int = 30
) -> np.ndarray:
    inside = ((y_true >= lower) & (y_true <= upper)).astype(float)
    n = len(inside)
    out = np.full(n, np.nan)
    for i in range(n):
        lo = max(0, i - window + 1)
        chunk = inside[lo : i + 1]
        if len(chunk) >= max(5, window // 3):
            out[i] = float(np.mean(chunk))
    return out
