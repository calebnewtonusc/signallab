"""Walk-forward (expanding or rolling) validation splits for time series."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator


@dataclass
class WalkForwardSplit:
    initial_train: int
    horizon: int
    step: int = 1
    mode: str = "expanding"
    max_folds: int | None = None

    def __post_init__(self) -> None:
        if self.initial_train < 2:
            raise ValueError("initial_train must be >= 2")
        if self.horizon < 1:
            raise ValueError("horizon must be >= 1")
        if self.step < 1:
            raise ValueError("step must be >= 1")
        if self.mode not in {"expanding", "rolling"}:
            raise ValueError("mode must be 'expanding' or 'rolling'")

    def split(self, n: int) -> Iterator[tuple[slice, slice, int]]:
        start = self.initial_train
        fold = 0
        while start + self.horizon <= n:
            if self.mode == "expanding":
                train = slice(0, start)
            else:
                train_start = max(0, start - self.initial_train)
                train = slice(train_start, start)
            test = slice(start, start + self.horizon)
            yield train, test, fold
            fold += 1
            if self.max_folds is not None and fold >= self.max_folds:
                return
            start += self.step

    def n_folds(self, n: int) -> int:
        return sum(1 for _ in self.split(n))
