from __future__ import annotations

import pytest


@pytest.mark.private_data
@pytest.mark.slow
def test_private_raw_cohort_counts(private_analysis, expected):
    count_keys = [
        "eligible_eyes",
        "near_target_eyes",
        "near_target_patients",
        "manifest_refraction_observed_eyes",
        "manifest_refraction_observed_patients",
        "primary_eyes",
        "primary_patients",
        "primary_toric_eyes",
        "primary_nontoric_eyes",
    ]
    assert {k: private_analysis["counts"][k] for k in count_keys} == {
        k: expected[k] for k in count_keys
    }


@pytest.mark.private_data
@pytest.mark.slow
def test_private_raw_estimate_is_computationally_equivalent(private_analysis, expected):
    observed = private_analysis["pooled"]["coefficient"]
    target = expected["primary_coefficient_d"]
    margin = expected["raw_verification_equivalence_margin_d"]
    assert abs(observed - target) <= margin
    assert len(private_analysis["components"]) == 20
