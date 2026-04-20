import numpy as np
import pytest

from signallab.metrics import (
    interval_metrics,
    mae,
    mape,
    mase,
    pinball_loss,
    point_metrics,
    rmse,
    smape,
)


def test_mae_zero_on_perfect_prediction():
    y = np.array([1.0, 2.0, 3.0])
    assert mae(y, y) == 0.0


def test_rmse_matches_formula():
    y_true = np.array([0.0, 0.0])
    y_pred = np.array([3.0, 4.0])
    assert rmse(y_true, y_pred) == pytest.approx(np.sqrt((9 + 16) / 2))


def test_mape_and_smape_non_negative():
    y_true = np.array([1.0, 2.0, 3.0, 4.0])
    y_pred = np.array([0.9, 2.1, 2.8, 4.2])
    assert mape(y_true, y_pred) > 0
    assert smape(y_true, y_pred) > 0


def test_mase_beats_naive_on_trend():
    y_train = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y_true = np.array([6.0, 7.0, 8.0])
    good = mase(y_true, np.array([6.0, 7.0, 8.0]), y_train, seasonality=1)
    bad = mase(y_true, np.array([1.0, 1.0, 1.0]), y_train, seasonality=1)
    assert good < bad


def test_pinball_symmetry_at_median():
    y_true = np.array([0.0, 0.0, 0.0])
    y_pred = np.array([1.0, -1.0, 0.5])
    loss = pinball_loss(y_true, y_pred, q=0.5)
    assert loss == pytest.approx(np.mean(0.5 * np.abs(y_true - y_pred)))


def test_interval_coverage_bounds():
    y = np.array([1.0, 2.0, 3.0, 4.0])
    lo = np.array([0.0, 0.0, 0.0, 5.0])
    up = np.array([5.0, 5.0, 5.0, 6.0])
    ir = interval_metrics(y, lo, up, alpha=0.1)
    assert 0.0 <= ir.coverage <= 1.0
    assert ir.avg_width > 0


def test_point_report_fields():
    y_true = np.array([1.0, 2.0, 3.0])
    y_pred = np.array([1.1, 2.2, 2.9])
    y_train = np.array([0.5, 1.0, 1.5, 2.0, 2.5])
    r = point_metrics(y_true, y_pred, y_train, seasonality=1)
    for val in (r.mae, r.rmse, r.smape, r.mase):
        assert val >= 0
