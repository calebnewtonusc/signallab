import pytest

from signallab.validation import WalkForwardSplit


def test_expanding_split_shapes():
    splitter = WalkForwardSplit(initial_train=10, horizon=3, step=1, mode="expanding")
    n = 20
    folds = list(splitter.split(n))
    assert len(folds) == (n - 10) - 3 + 1
    for (train, test, _), expected_end in zip(folds, range(10, 18)):
        assert train.start == 0
        assert train.stop == expected_end
        assert test.start == expected_end
        assert test.stop == expected_end + 3


def test_rolling_split_fixed_window():
    splitter = WalkForwardSplit(initial_train=10, horizon=2, step=2, mode="rolling")
    n = 30
    folds = list(splitter.split(n))
    for train, _, _ in folds:
        assert train.stop - train.start == 10


def test_max_folds_limit():
    splitter = WalkForwardSplit(initial_train=5, horizon=1, step=1, max_folds=3)
    folds = list(splitter.split(100))
    assert len(folds) == 3


def test_invalid_params():
    with pytest.raises(ValueError):
        WalkForwardSplit(initial_train=1, horizon=1)
    with pytest.raises(ValueError):
        WalkForwardSplit(initial_train=5, horizon=0)
    with pytest.raises(ValueError):
        WalkForwardSplit(initial_train=5, horizon=1, mode="nope")
