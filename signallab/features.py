"""Lag, rolling, and calendar feature builders for supervised forecasters."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass
class FeatureSpec:
    lags: tuple[int, ...] = (1, 2, 3, 7)
    rolling_windows: tuple[int, ...] = (7, 28)
    rolling_stats: tuple[str, ...] = ("mean", "std")
    calendar: bool = False
    extra: dict[str, object] = field(default_factory=dict)


def build_features(series: pd.Series, spec: FeatureSpec) -> pd.DataFrame:
    df = pd.DataFrame(index=series.index)
    df["y"] = series.values

    for lag in spec.lags:
        if lag <= 0:
            continue
        df[f"lag_{lag}"] = series.shift(lag)

    for window in spec.rolling_windows:
        if window <= 1:
            continue
        shifted = series.shift(1)
        for stat in spec.rolling_stats:
            col = f"roll_{stat}_{window}"
            roll = shifted.rolling(window=window, min_periods=max(2, window // 2))
            if stat == "mean":
                df[col] = roll.mean()
            elif stat == "std":
                df[col] = roll.std()
            elif stat == "min":
                df[col] = roll.min()
            elif stat == "max":
                df[col] = roll.max()
            else:
                raise ValueError(f"unknown rolling stat: {stat}")

    if spec.calendar and isinstance(series.index, pd.DatetimeIndex):
        df["dow"] = series.index.dayofweek.astype(float)
        df["month"] = series.index.month.astype(float)
        df["doy_sin"] = np.sin(2 * np.pi * series.index.dayofyear / 366.0)
        df["doy_cos"] = np.cos(2 * np.pi * series.index.dayofyear / 366.0)

    return df


def align_design_matrix(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, pd.Index]:
    cleaned = df.dropna()
    y = cleaned["y"].to_numpy()
    feature_cols = [c for c in cleaned.columns if c != "y"]
    X = cleaned[feature_cols].to_numpy() if feature_cols else np.zeros((len(cleaned), 0))
    return X, y, cleaned.index


def feature_names(spec: FeatureSpec, is_datetime: bool) -> list[str]:
    names: list[str] = []
    for lag in spec.lags:
        if lag > 0:
            names.append(f"lag_{lag}")
    for window in spec.rolling_windows:
        if window <= 1:
            continue
        for stat in spec.rolling_stats:
            names.append(f"roll_{stat}_{window}")
    if spec.calendar and is_datetime:
        names.extend(["dow", "month", "doy_sin", "doy_cos"])
    return names


def windows_from_range(start: int, stop: int, step: int = 1) -> Iterable[int]:
    return range(start, stop + 1, step)
