from __future__ import annotations

from dataclasses import dataclass, asdict
from math import sqrt
from scipy.stats import norm
from typing import Iterable

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from statsmodels.genmod.cov_struct import Independence
from statsmodels.genmod.families import Binomial, Gaussian


@dataclass
class ImputationEstimate:
    imputation: int
    seed: int
    coefficient: float
    variance: float
    standard_error: float
    effective_sample_size: float
    toric_effective_sample_size: float
    nontoric_effective_sample_size: float
    weight_p99: float
    weight_max: float


def effective_sample_size(weights: np.ndarray) -> float:
    weights = np.asarray(weights, dtype=float)
    return float(weights.sum() ** 2 / np.square(weights).sum())


def _rubin_pool(estimates: Iterable[ImputationEstimate]) -> dict[str, float]:
    rows = list(estimates)
    q = np.asarray([row.coefficient for row in rows], dtype=float)
    u = np.asarray([row.variance for row in rows], dtype=float)
    m = len(rows)
    q_bar = float(q.mean())
    within = float(u.mean())
    between = float(q.var(ddof=1)) if m > 1 else 0.0
    total = within + (1.0 + 1.0 / m) * between
    se = sqrt(total)
    z = q_bar / se
    p = float(2.0 * norm.sf(abs(z)))
    return {
        "m": m,
        "coefficient": q_bar,
        "within_variance": within,
        "between_variance": between,
        "total_variance": total,
        "standard_error": se,
        "ci_low": q_bar - 1.96 * se,
        "ci_high": q_bar + 1.96 * se,
        "p_value": p,
    }


def run_raw_primary_analysis(
    data: pd.DataFrame, cfg: dict, seeds: list[int] | None = None
) -> tuple[dict[str, float], pd.DataFrame]:
    if seeds is None:
        seeds = list(cfg["release"]["random_seed_manifest"])
    covariates = list(cfg["propensity_score"]["covariates"])
    required = set(covariates) | {"toric", "residual_cylinder", "patient_id"}
    missing = sorted(required - set(data.columns))
    if missing:
        raise KeyError(f"Missing analysis columns: {missing}")

    work = data.copy()
    work["fellow_toric"] = work["fellow_toric"].fillna(
        work["fellow_toric"].mode(dropna=True).iloc[0]
    )
    impute_columns = [
        "age",
        "surgery_year",
        "target",
        "preop_cylinder",
        "axial_length",
        "fellow_target",
        "female",
        "premium_proc",
        "surgeon_code",
        "axis_code",
        "toric",
        "residual_cylinder",
    ]
    impute_frame = work[impute_columns].astype(float)
    rows: list[ImputationEstimate] = []

    for index, seed in enumerate(seeds, start=1):
        imputer = IterativeImputer(
            random_state=int(seed),
            sample_posterior=bool(cfg["imputation"]["sample_posterior"]),
            max_iter=int(cfg["imputation"]["max_iter"]),
            initial_strategy=str(cfg["imputation"]["initial_strategy"]),
            skip_complete=True,
        )
        imputed = pd.DataFrame(
            imputer.fit_transform(impute_frame),
            columns=impute_frame.columns,
            index=work.index,
        )
        completed = work.copy()
        for column in cfg["imputation"]["variables_imputed"]:
            completed[column] = imputed[column]
        completed["preop_cylinder"] = completed["preop_cylinder"].clip(0, 7)
        completed["axial_length"] = completed["axial_length"].clip(18, 35)

        x_ps = sm.add_constant(completed[covariates].astype(float), has_constant="add")
        ps_model = sm.GLM(completed["toric"].astype(int), x_ps, family=Binomial()).fit(
            maxiter=250, disp=0
        )
        propensity = np.clip(ps_model.predict(x_ps), 1e-6, 1.0 - 1e-6)
        treatment = completed["toric"].astype(bool).to_numpy()
        weights = np.where(treatment, 1.0 - propensity, propensity)

        x_outcome = sm.add_constant(
            completed["toric"].astype(float), has_constant="add"
        )
        gee = sm.GEE(
            completed["residual_cylinder"].astype(float),
            x_outcome,
            groups=completed["patient_id"],
            family=Gaussian(),
            cov_struct=Independence(),
            weights=weights,
        ).fit(cov_type=str(cfg["outcome_model"]["covariance"]))
        coefficient = float(gee.params["toric"])
        variance = float(gee.cov_params().loc["toric", "toric"])
        rows.append(
            ImputationEstimate(
                imputation=index,
                seed=int(seed),
                coefficient=coefficient,
                variance=variance,
                standard_error=sqrt(variance),
                effective_sample_size=effective_sample_size(weights),
                toric_effective_sample_size=effective_sample_size(weights[treatment]),
                nontoric_effective_sample_size=effective_sample_size(weights[~treatment]),
                weight_p99=float(np.quantile(weights, 0.99)),
                weight_max=float(weights.max()),
            )
        )

    pooled = _rubin_pool(rows)
    components = pd.DataFrame([asdict(row) for row in rows])
    return pooled, components


def pool_frozen_components(components: pd.DataFrame) -> dict[str, float]:
    """Pool the archived, non-patient-level 20-imputation component estimates."""
    required = {"imputation", "coef", "var", "se", "ess", "toric_ess", "control_ess", "weight_p99", "weight_max"}
    missing = required - set(components.columns)
    if missing:
        raise KeyError(f"Frozen component file is missing columns: {sorted(missing)}")
    rows = [
        ImputationEstimate(
            imputation=int(row["imputation"]),
            seed=int(row["imputation"]),
            coefficient=float(row["coef"]),
            variance=float(row["var"]),
            standard_error=float(row["se"]),
            effective_sample_size=float(row["ess"]),
            toric_effective_sample_size=float(row["toric_ess"]),
            nontoric_effective_sample_size=float(row["control_ess"]),
            weight_p99=float(row["weight_p99"]),
            weight_max=float(row["weight_max"]),
        )
        for _, row in components.iterrows()
    ]
    return _rubin_pool(rows)
