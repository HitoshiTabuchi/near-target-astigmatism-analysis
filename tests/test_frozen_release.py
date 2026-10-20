from __future__ import annotations

import pandas as pd

from near_target_pipeline.frozen import verify_frozen_model


def test_frozen_primary_estimate_is_exact(repo_root, expected):
    result = verify_frozen_model(repo_root / "reference")
    assert result["passed"], result["checks"]
    pooled = result["pooled"]
    assert pooled["m"] == 20
    assert abs(pooled["coefficient"] - expected["primary_coefficient_d"]) < 1e-12
    assert abs(pooled["standard_error"] - expected["primary_standard_error"]) < 1e-12
    assert abs(pooled["ci_low"] - expected["primary_ci_low"]) < 1e-12
    assert abs(pooled["ci_high"] - expected["primary_ci_high"]) < 1e-12


def test_frozen_interaction_coefficients(repo_root, expected):
    frame = pd.read_csv(repo_root / "reference" / "model_outputs" / "target_interactions_fast.csv")
    values = frame.set_index("outcome")["coef"].to_dict()
    assert abs(values["UNVA"] - expected["target_interaction_unva"]) < 1e-9
    assert abs(values["UIVA"] - expected["target_interaction_uiva"]) < 1e-9
    assert abs(values["UDVA"] - expected["target_interaction_udva"]) < 1e-9
