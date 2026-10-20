from __future__ import annotations

import numpy as np
import pandas as pd

from near_target_pipeline.data_io import load_yaml
from near_target_pipeline.models import run_raw_primary_analysis


def test_synthetic_model_runs(repo_root):
    data = pd.read_csv(repo_root / "data" / "synthetic" / "synthetic_primary.csv")
    data["toric"] = data["toric"].astype(bool)
    cfg = load_yaml(repo_root / "config" / "analysis.yml")
    pooled, components = run_raw_primary_analysis(data, cfg, seeds=[1, 2])
    assert pooled["m"] == 2
    assert len(components) == 2
    assert np.isfinite(pooled["coefficient"])
    assert np.isfinite(pooled["standard_error"])
    assert components["effective_sample_size"].gt(0).all()
