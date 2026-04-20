"""Forecaster protocol and shared forecast container."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass
class Forecast:
    mean: np.ndarray
    lower: np.ndarray
    upper: np.ndarray
    sigma: np.ndarray


class Forecaster(Protocol):
    name: str

    def fit(self, y_train: np.ndarray) -> "Forecaster":
        ...

    def predict(self, horizon: int, alpha: float = 0.1) -> Forecast:
        ...
