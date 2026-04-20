"""Data sources: synthetic series generators and bundled real datasets."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd


@dataclass
class SeriesSpec:
    name: str
    n: int
    freq: str = "D"
    trend: float = 0.0
    seasonal_period: int = 0
    seasonal_amp: float = 0.0
    noise: float = 1.0
    ar1: float = 0.0
    drift_break: tuple[int, float] | None = None
    variance_break: tuple[int, float] | None = None


def generate_synthetic_series(spec: SeriesSpec, seed: int = 0) -> pd.Series:
    rng = np.random.default_rng(seed)
    t = np.arange(spec.n, dtype=float)

    level = spec.trend * t
    if spec.drift_break is not None:
        start, extra_slope = spec.drift_break
        level = level + np.where(t >= start, extra_slope * (t - start), 0.0)

    season = np.zeros_like(t)
    if spec.seasonal_period > 1 and spec.seasonal_amp > 0:
        season = spec.seasonal_amp * np.sin(2 * np.pi * t / spec.seasonal_period)

    noise_scale = np.full_like(t, spec.noise)
    if spec.variance_break is not None:
        start, mult = spec.variance_break
        noise_scale = np.where(t >= start, spec.noise * mult, spec.noise)

    innovations = rng.normal(0.0, 1.0, size=spec.n) * noise_scale
    if spec.ar1 != 0.0:
        eps = np.zeros(spec.n)
        for i in range(spec.n):
            eps[i] = spec.ar1 * (eps[i - 1] if i else 0.0) + innovations[i]
        innovations = eps

    values = level + season + innovations
    idx = pd.date_range(start="2020-01-01", periods=spec.n, freq=spec.freq)
    return pd.Series(values, index=idx, name=spec.name)


def inject_shift(
    series: pd.Series,
    at: int,
    kind: Literal["level", "variance", "trend"] = "level",
    magnitude: float = 3.0,
) -> pd.Series:
    out = series.copy()
    n = len(out)
    if at >= n:
        return out

    arr = out.to_numpy().copy()
    if kind == "level":
        arr[at:] = arr[at:] + magnitude * np.std(arr[:at])
    elif kind == "variance":
        rng = np.random.default_rng(42)
        noise = rng.normal(0.0, 1.0, size=n - at) * (magnitude - 1.0) * np.std(arr[:at])
        arr[at:] = arr[at:] + noise
    elif kind == "trend":
        steps = np.arange(n - at, dtype=float)
        arr[at:] = arr[at:] + magnitude * steps * (np.std(arr[:at]) / max(1, n - at))
    else:
        raise ValueError(f"unknown shift kind: {kind}")

    return pd.Series(arr, index=out.index, name=out.name)


def load_airline() -> pd.Series:
    """Box-Jenkins airline passengers (monthly, 1949-1960)."""
    values = [
        112, 118, 132, 129, 121, 135, 148, 148, 136, 119, 104, 118,
        115, 126, 141, 135, 125, 149, 170, 170, 158, 133, 114, 140,
        145, 150, 178, 163, 172, 178, 199, 199, 184, 162, 146, 166,
        171, 180, 193, 181, 183, 218, 230, 242, 209, 191, 172, 194,
        196, 196, 236, 235, 229, 243, 264, 272, 237, 211, 180, 201,
        204, 188, 235, 227, 234, 264, 302, 293, 259, 229, 203, 229,
        242, 233, 267, 269, 270, 315, 364, 347, 312, 274, 237, 278,
        284, 277, 317, 313, 318, 374, 413, 405, 355, 306, 271, 306,
        315, 301, 356, 348, 355, 422, 465, 467, 404, 347, 305, 336,
        340, 318, 362, 348, 363, 435, 491, 505, 404, 359, 310, 337,
        360, 342, 406, 396, 420, 472, 548, 559, 463, 407, 362, 405,
        417, 391, 419, 461, 472, 535, 622, 606, 508, 461, 390, 432,
    ]
    idx = pd.date_range(start="1949-01-01", periods=len(values), freq="MS")
    return pd.Series(values, index=idx, name="airline_passengers", dtype=float)
