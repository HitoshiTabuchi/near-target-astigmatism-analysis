from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def regenerate_aggregate_figures(reference_dir: str | Path, output_dir: str | Path) -> list[Path]:
    """Regenerate data-equivalent figures from non-patient-level audit outputs.

    These are intentionally separate from the byte-identical archived submission figures.
    They verify that the published aggregate results can be plotted from code without
    exposing patient-level data.
    """
    reference_dir = Path(reference_dir)
    output_dir = Path(output_dir)
    model_dir = reference_dir / "model_outputs"
    created: list[Path] = []

    # Figure R1: 20 MI coefficients and ESS.
    mi = pd.read_csv(model_dir / "primary_mi_components.csv")
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ax.plot(mi["imputation"], mi["coef"], marker="o")
    ax.axhline(mi["coef"].mean(), linestyle="--", linewidth=1.2)
    ax.set_xlabel("Imputation")
    ax.set_ylabel("Toric coefficient for residual cylinder (D)")
    ax.set_title("Twenty frozen multiple-imputation component estimates")
    ax.grid(axis="y", alpha=0.25)
    p = output_dir / "regenerated_MI_component_estimates.png"
    _save(fig, p); created.append(p)

    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ax.plot(mi["imputation"], mi["ess"], marker="o", label="Overall ESS")
    ax.plot(mi["imputation"], mi["toric_ess"], marker="^", label="Toric ESS")
    ax.plot(mi["imputation"], mi["control_ess"], marker="v", label="Non-toric ESS")
    ax.set_xlabel("Imputation")
    ax.set_ylabel("Effective sample size")
    ax.set_title("Overlap-weight effective sample size")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    p = output_dir / "regenerated_overlap_weight_ESS.png"
    _save(fig, p); created.append(p)

    # Figure R2: target interactions.
    inter = pd.read_csv(model_dir / "target_interactions_fast.csv")
    y = np.arange(len(inter))
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    xerr = np.vstack([inter["coef"] - inter["lo"], inter["hi"] - inter["coef"]])
    ax.errorbar(inter["coef"], y, xerr=xerr, fmt="o", capsize=4)
    ax.axvline(0, linewidth=1)
    ax.set_yticks(y, inter["outcome"])
    ax.set_xlabel("Near-minus-distance interaction (logMAR/D)")
    ax.set_title("Residual-cylinder × target-arm interaction")
    ax.grid(axis="x", alpha=0.25)
    p = output_dir / "regenerated_target_interactions.png"
    _save(fig, p); created.append(p)

    # Figure R3: sensitivity estimates.
    sens = pd.read_csv(model_dir / "final_sensitivity_summary.csv")
    sens = sens[sens["estimand"].str.contains("Toric coefficient", na=False)].copy()
    y = np.arange(len(sens))
    fig, ax = plt.subplots(figsize=(10, 6.5))
    xerr = np.vstack([sens["estimate"] - sens["ci_low"], sens["ci_high"] - sens["estimate"]])
    ax.errorbar(sens["estimate"], y, xerr=xerr, fmt="o", capsize=4)
    ax.axvline(0, linewidth=1)
    ax.set_yticks(y, sens["analysis"])
    ax.invert_yaxis()
    ax.set_xlabel("Coefficient for residual cylinder (D)")
    ax.set_title("Primary and sensitivity estimates")
    ax.grid(axis="x", alpha=0.25)
    p = output_dir / "regenerated_sensitivity_forest.png"
    _save(fig, p); created.append(p)
    return created
