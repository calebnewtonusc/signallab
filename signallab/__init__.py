"""SignalLab: time-series forecasting and simulation pipeline."""

from signallab.data import generate_synthetic_series, load_airline, inject_shift
from signallab.validation import WalkForwardSplit
from signallab.pipeline import Experiment, ExperimentResult
from signallab.metrics import point_metrics, interval_metrics, pinball_loss
from signallab.calibration import coverage, pit_values, reliability_bins

__version__ = "0.1.0"
__all__ = [
    "generate_synthetic_series",
    "load_airline",
    "inject_shift",
    "WalkForwardSplit",
    "Experiment",
    "ExperimentResult",
    "point_metrics",
    "interval_metrics",
    "pinball_loss",
    "coverage",
    "pit_values",
    "reliability_bins",
]
