"""Orchestration: run models under walk-forward validation and aggregate results."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

from signallab.calibration import calibration_error, pit_values, rolling_coverage
from signallab.conformal import apply_conformal_widths, compute_conformal_widths
from signallab.metrics import interval_metrics, point_metrics
from signallab.models.base import Forecaster
from signallab.models.ml import LagRegressionForecaster
from signallab.validation import WalkForwardSplit


ModelFactory = Callable[[], Forecaster]


@dataclass
class FoldRecord:
    model: str
    fold: int
    horizon_step: int
    train_end: str
    test_time: str
    y_true: float
    y_pred: float
    lower: float
    upper: float
    sigma: float


@dataclass
class HorizonSummary:
    model: str
    horizon_step: int
    mae: float
    rmse: float
    mape: float
    smape: float
    mase: float
    coverage: float
    avg_width: float
    calibration_error: float


@dataclass
class ExperimentResult:
    records: list[FoldRecord] = field(default_factory=list)
    horizon_summaries: list[HorizonSummary] = field(default_factory=list)
    overall_summaries: list[dict] = field(default_factory=list)
    rolling_coverage: dict[str, list[float]] = field(default_factory=dict)
    meta: dict = field(default_factory=dict)

    def records_df(self) -> pd.DataFrame:
        return pd.DataFrame([asdict(r) for r in self.records])

    def horizon_df(self) -> pd.DataFrame:
        return pd.DataFrame([asdict(s) for s in self.horizon_summaries])

    def overall_df(self) -> pd.DataFrame:
        return pd.DataFrame(self.overall_summaries)

    def save(self, outdir: str | Path) -> Path:
        outdir = Path(outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        self.records_df().to_csv(outdir / "records.csv", index=False)
        self.horizon_df().to_csv(outdir / "horizon_summary.csv", index=False)
        self.overall_df().to_csv(outdir / "overall_summary.csv", index=False)
        summary = {
            "meta": self.meta,
            "overall": self.overall_summaries,
            "horizons": [asdict(s) for s in self.horizon_summaries],
            "rolling_coverage": self.rolling_coverage,
        }
        (outdir / "results.json").write_text(json.dumps(summary, indent=2, default=str))
        return outdir


@dataclass
class Experiment:
    series: pd.Series
    splitter: WalkForwardSplit
    models: dict[str, ModelFactory]
    alpha: float = 0.1
    seasonality: int = 1
    coverage_window: int = 30
    conformal: bool = False
    calibration_folds: int = 10

    def run(self) -> ExperimentResult:
        if not isinstance(self.series.index, pd.DatetimeIndex):
            raise ValueError("series must have a DatetimeIndex")
        values = self.series.to_numpy(dtype=float)
        index = self.series.index
        n = len(values)

        result = ExperimentResult()
        result.meta = {
            "series_name": str(self.series.name),
            "n_obs": int(n),
            "horizon": int(self.splitter.horizon),
            "initial_train": int(self.splitter.initial_train),
            "step": int(self.splitter.step),
            "mode": self.splitter.mode,
            "alpha": float(self.alpha),
            "seasonality": int(self.seasonality),
            "models": list(self.models.keys()),
            "n_folds": int(self.splitter.n_folds(n)),
            "conformal": bool(self.conformal),
            "calibration_folds": int(self.calibration_folds) if self.conformal else 0,
        }

        per_model_rows: dict[str, list[FoldRecord]] = {name: [] for name in self.models}
        for train_slice, test_slice, fold in self.splitter.split(n):
            y_train = values[train_slice]
            y_test = values[test_slice]
            train_index = index[train_slice]
            test_index = index[test_slice]

            for name, factory in self.models.items():
                model = factory()
                if isinstance(model, LagRegressionForecaster):
                    model.fit(y_train, index=train_index)
                else:
                    model.fit(y_train)
                forecast = model.predict(self.splitter.horizon, alpha=self.alpha)
                if self.conformal:
                    calib = compute_conformal_widths(
                        y_train=y_train,
                        index=train_index,
                        factory=factory,
                        horizon=self.splitter.horizon,
                        alpha=self.alpha,
                        calibration_folds=self.calibration_folds,
                    )
                    if calib.n_calibration_folds >= 2:
                        forecast = apply_conformal_widths(forecast, calib.widths)
                for step in range(self.splitter.horizon):
                    rec = FoldRecord(
                        model=name,
                        fold=fold,
                        horizon_step=step + 1,
                        train_end=str(train_index[-1]),
                        test_time=str(test_index[step]),
                        y_true=float(y_test[step]),
                        y_pred=float(forecast.mean[step]),
                        lower=float(forecast.lower[step]),
                        upper=float(forecast.upper[step]),
                        sigma=float(forecast.sigma[step]),
                    )
                    per_model_rows[name].append(rec)
                    result.records.append(rec)

        for name, rows in per_model_rows.items():
            if not rows:
                continue
            df = pd.DataFrame([asdict(r) for r in rows])
            y_train_full = values[: self.splitter.initial_train]
            for h in sorted(df["horizon_step"].unique()):
                sub = df[df["horizon_step"] == h]
                y_true = sub["y_true"].to_numpy()
                y_pred = sub["y_pred"].to_numpy()
                lower = sub["lower"].to_numpy()
                upper = sub["upper"].to_numpy()
                sigma = sub["sigma"].to_numpy()
                pr = point_metrics(y_true, y_pred, y_train_full, seasonality=self.seasonality)
                ir = interval_metrics(y_true, lower, upper, alpha=self.alpha)
                pit = pit_values(y_true, y_pred, sigma)
                ce = calibration_error(pit)
                result.horizon_summaries.append(
                    HorizonSummary(
                        model=name,
                        horizon_step=int(h),
                        mae=pr.mae,
                        rmse=pr.rmse,
                        mape=pr.mape,
                        smape=pr.smape,
                        mase=pr.mase,
                        coverage=ir.coverage,
                        avg_width=ir.avg_width,
                        calibration_error=ce,
                    )
                )

            y_true_all = df["y_true"].to_numpy()
            y_pred_all = df["y_pred"].to_numpy()
            lower_all = df["lower"].to_numpy()
            upper_all = df["upper"].to_numpy()
            sigma_all = df["sigma"].to_numpy()
            pr = point_metrics(y_true_all, y_pred_all, y_train_full, seasonality=self.seasonality)
            ir = interval_metrics(y_true_all, lower_all, upper_all, alpha=self.alpha)
            pit = pit_values(y_true_all, y_pred_all, sigma_all)
            ce = calibration_error(pit)
            result.overall_summaries.append(
                {
                    "model": name,
                    "mae": pr.mae,
                    "rmse": pr.rmse,
                    "mape": pr.mape,
                    "smape": pr.smape,
                    "mase": pr.mase,
                    "coverage": ir.coverage,
                    "avg_width": ir.avg_width,
                    "pinball_lower": ir.pinball_lower,
                    "pinball_upper": ir.pinball_upper,
                    "calibration_error": ce,
                }
            )

            h1 = df[df["horizon_step"] == 1].sort_values("test_time")
            if len(h1):
                rc = rolling_coverage(
                    h1["y_true"].to_numpy(),
                    h1["lower"].to_numpy(),
                    h1["upper"].to_numpy(),
                    window=self.coverage_window,
                )
                result.rolling_coverage[name] = [
                    None if np.isnan(v) else float(v) for v in rc
                ]

        return result


def tune_feature_window(
    series: pd.Series,
    splitter: WalkForwardSplit,
    lag_grid: list[int],
    factory_template: Callable[[int], ModelFactory],
    alpha: float = 0.1,
    seasonality: int = 1,
) -> pd.DataFrame:
    rows = []
    for max_lag in lag_grid:
        models = {f"lag_{max_lag}": factory_template(max_lag)}
        exp = Experiment(
            series=series,
            splitter=splitter,
            models=models,
            alpha=alpha,
            seasonality=seasonality,
        )
        result = exp.run()
        if result.overall_summaries:
            row = dict(result.overall_summaries[0])
            row["max_lag"] = max_lag
            rows.append(row)
    return pd.DataFrame(rows)
