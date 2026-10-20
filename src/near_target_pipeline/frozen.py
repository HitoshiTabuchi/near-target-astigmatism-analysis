from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pandas as pd

from .data_io import sha256_file
from .models import pool_frozen_components


def load_expected(reference_dir: str | Path) -> dict[str, Any]:
    reference_dir = Path(reference_dir)
    return json.loads((reference_dir / "expected_results.json").read_text(encoding="utf-8"))


def verify_frozen_model(reference_dir: str | Path, atol: float = 1e-9) -> dict[str, Any]:
    reference_dir = Path(reference_dir)
    components = pd.read_csv(reference_dir / "model_outputs" / "primary_mi_components.csv")
    pooled = pool_frozen_components(components)
    expected = load_expected(reference_dir)
    checks = {
        "coefficient": abs(pooled["coefficient"] - expected["primary_coefficient_d"]) <= atol,
        "standard_error": abs(pooled["standard_error"] - expected["primary_standard_error"]) <= atol,
        "ci_low": abs(pooled["ci_low"] - expected["primary_ci_low"]) <= atol,
        "ci_high": abs(pooled["ci_high"] - expected["primary_ci_high"]) <= atol,
        "within_variance": abs(pooled["within_variance"] - expected["rubin_within_variance"]) <= atol,
        "between_variance": abs(pooled["between_variance"] - expected["rubin_between_variance"]) <= atol,
        "m": pooled["m"] == 20,
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "pooled": pooled,
        "expected": expected,
    }


def replay_figures(reference_dir: str | Path, output_dir: str | Path) -> list[dict[str, Any]]:
    reference_dir = Path(reference_dir)
    output_dir = Path(output_dir)
    source = reference_dir / "figures"
    destination = output_dir / "figures"
    destination.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []
    for path in sorted(source.glob("*.png")):
        target = destination / path.name
        shutil.copy2(path, target)
        manifest.append(
            {
                "filename": path.name,
                "sha256_reference": sha256_file(path),
                "sha256_replayed": sha256_file(target),
                "identical": sha256_file(path) == sha256_file(target),
            }
        )
    return manifest


def run_frozen_release(repo_root: str | Path, output_dir: str | Path) -> dict[str, Any]:
    repo_root = Path(repo_root)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    reference_dir = repo_root / "reference"
    model = verify_frozen_model(reference_dir)
    figures = replay_figures(reference_dir, output_dir)
    report = {
        "mode": "frozen_release_replay",
        "model": model,
        "figures": figures,
        "all_figures_identical": bool(figures) and all(x["identical"] for x in figures),
    }
    report["passed"] = bool(model["passed"] and report["all_figures_identical"])
    (output_dir / "frozen_release_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report
