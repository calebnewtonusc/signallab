"""End-to-end airline-passengers benchmark (monthly, seasonality=12)."""
from pathlib import Path

from signallab.cli import _default_models
from signallab.data import load_airline
from signallab.pipeline import Experiment
from signallab.reporting import print_overall, print_horizon_breakdown
from signallab.validation import WalkForwardSplit


def main() -> None:
    series = load_airline()
    splitter = WalkForwardSplit(initial_train=72, horizon=6, step=1, mode="expanding")
    experiment = Experiment(
        series=series,
        splitter=splitter,
        models=_default_models(seasonality=12),
        alpha=0.1,
        seasonality=12,
        conformal=True,
        calibration_folds=10,
    )
    result = experiment.run()
    print_overall(result)
    print_horizon_breakdown(result)
    out = result.save(Path("artifacts/airline"))
    print(f"Artifacts written to {out.resolve()}")


if __name__ == "__main__":
    main()
