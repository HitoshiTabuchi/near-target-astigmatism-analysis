from __future__ import annotations

import json
import os
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def expected(repo_root: Path) -> dict:
    return json.loads((repo_root / "reference" / "expected_results.json").read_text())


@pytest.fixture(scope="session")
def raw_config_path() -> Path:
    value = os.environ.get("NEAR_TARGET_RAW_CONFIG")
    if not value:
        pytest.skip("NEAR_TARGET_RAW_CONFIG is not set; private-data test skipped")
    path = Path(value)
    if not path.exists():
        pytest.skip(f"Private raw config not found: {path}")
    return path


@pytest.fixture(scope="session")
def private_analysis(repo_root: Path, raw_config_path: Path):
    from near_target_pipeline.cohort import cohort_counts, derive_cohorts
    from near_target_pipeline.covariates import derive_primary_covariates
    from near_target_pipeline.data_io import load_private_audit, load_yaml, resolve_raw_files
    from near_target_pipeline.models import run_raw_primary_analysis

    cfg = load_yaml(repo_root / "config" / "analysis.yml")
    cfg.update(load_private_audit(raw_config_path))
    raw = resolve_raw_files(raw_config_path)
    bundle = derive_cohorts(
        raw,
        repo_root / "reference" / "model_outputs" / "iol_model_inventory.csv",
        cfg,
    )
    analysis = derive_primary_covariates(bundle.primary, bundle.eligible, raw, cfg)
    pooled, components = run_raw_primary_analysis(analysis, cfg)
    return {
        "counts": cohort_counts(bundle),
        "pooled": pooled,
        "components": components,
        "analysis": analysis,
    }
