import numpy as np

from signallab.calibration import calibration_error, pit_values, reliability_bins, rolling_coverage


def test_pit_values_uniform_under_correct_model():
    rng = np.random.default_rng(0)
    mu = np.zeros(2000)
    sigma = np.ones(2000)
    y = rng.normal(0, 1, size=2000)
    pit = pit_values(y, mu, sigma)
    assert 0.45 < pit.mean() < 0.55
    assert pit.min() >= 0 and pit.max() <= 1


def test_calibration_error_smaller_when_correct():
    rng = np.random.default_rng(1)
    y = rng.normal(0, 1, size=500)
    correct = pit_values(y, np.zeros(500), np.ones(500))
    wrong = pit_values(y, np.zeros(500), 3 * np.ones(500))
    assert calibration_error(correct) < calibration_error(wrong)


def test_reliability_bin_counts_sum():
    rng = np.random.default_rng(2)
    pit = rng.uniform(0, 1, size=100)
    bins = reliability_bins(pit, n_bins=10)
    assert sum(b.count for b in bins) == 100


def test_rolling_coverage_approaches_target():
    y = np.zeros(200)
    lo = np.full(200, -1.0)
    up = np.full(200, 1.0)
    rc = rolling_coverage(y, lo, up, window=30)
    tail = rc[-30:]
    assert np.nanmean(tail) == 1.0
