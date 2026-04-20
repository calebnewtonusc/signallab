"""Pretty-print experiment results to terminal."""
from __future__ import annotations

from rich.console import Console
from rich.table import Table

from signallab.pipeline import ExperimentResult


def print_overall(result: ExperimentResult, console: Console | None = None) -> None:
    console = console or Console()
    table = Table(title="Overall benchmark", show_lines=False)
    columns = [
        ("Model", "left"),
        ("MAE", "right"),
        ("RMSE", "right"),
        ("sMAPE", "right"),
        ("MASE", "right"),
        ("Coverage", "right"),
        ("Width", "right"),
        ("CalErr", "right"),
    ]
    for title, justify in columns:
        table.add_column(title, justify=justify)

    sorted_rows = sorted(result.overall_summaries, key=lambda r: r["mae"])
    for row in sorted_rows:
        table.add_row(
            row["model"],
            f"{row['mae']:.3f}",
            f"{row['rmse']:.3f}",
            f"{row['smape']:.2f}%",
            f"{row['mase']:.3f}",
            f"{row['coverage']:.1%}",
            f"{row['avg_width']:.3f}",
            f"{row['calibration_error']:.3f}",
        )
    console.print(table)


def print_horizon_breakdown(result: ExperimentResult, console: Console | None = None) -> None:
    console = console or Console()
    by_model: dict[str, list] = {}
    for s in result.horizon_summaries:
        by_model.setdefault(s.model, []).append(s)

    for model, rows in by_model.items():
        table = Table(title=f"Per-horizon metrics: {model}")
        for title, justify in [
            ("Step", "right"),
            ("MAE", "right"),
            ("RMSE", "right"),
            ("sMAPE", "right"),
            ("Coverage", "right"),
            ("CalErr", "right"),
        ]:
            table.add_column(title, justify=justify)
        for s in sorted(rows, key=lambda r: r.horizon_step):
            table.add_row(
                str(s.horizon_step),
                f"{s.mae:.3f}",
                f"{s.rmse:.3f}",
                f"{s.smape:.2f}%",
                f"{s.coverage:.1%}",
                f"{s.calibration_error:.3f}",
            )
        console.print(table)
