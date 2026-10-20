from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .classification import classify_iol_records
from .data_io import RawFiles


@dataclass
class CohortBundle:
    eligible: pd.DataFrame
    near_target: pd.DataFrame
    manifest_observed: pd.DataFrame
    primary: pd.DataFrame


def load_iol(raw: RawFiles) -> pd.DataFrame:
    frame = pd.read_excel(raw.iol)
    frame = frame.rename(
        columns={
            "ID": "patient_id",
            "術眼": "eye",
            "性": "sex",
            "執刀医・略称": "surgeon",
            "手術術式": "procedure",
            "手術予定日": "surgery_date",
            "年齢": "age",
            "眼内レンズ": "iol_model",
            "眼内レンズターゲット": "target",
        }
    )
    frame["patient_id"] = pd.to_numeric(frame["patient_id"], errors="coerce")
    frame["surgery_date"] = pd.to_datetime(frame["surgery_date"], errors="coerce")
    frame["target"] = pd.to_numeric(frame["target"], errors="coerce")
    frame["age"] = pd.to_numeric(frame["age"], errors="coerce")
    frame = frame[
        frame["patient_id"].notna()
        & frame["eye"].isin(["R", "L"])
        & frame["surgery_date"].notna()
        & frame["target"].notna()
    ].copy()
    frame["patient_id"] = frame["patient_id"].astype(int)
    frame["surgery_year"] = frame["surgery_date"].dt.year.astype(int)
    return frame


def load_refraction_long(raw: RawFiles) -> pd.DataFrame:
    frame = pd.read_excel(raw.refraction).rename(
        columns={"ID": "patient_id", "検査日": "exam_date"}
    )
    frame["patient_id"] = pd.to_numeric(frame["patient_id"], errors="coerce")
    frame["exam_date"] = pd.to_datetime(frame["exam_date"], errors="coerce")
    pieces: list[pd.DataFrame] = []
    for eye, prefix in (("L", "L"), ("R", "R")):
        part = frame[
            [
                "patient_id",
                "exam_date",
                f"{prefix}cylinder",
                f"{prefix}cylinderaxis",
                f"{prefix}sphere",
            ]
        ].copy()
        part.columns = [
            "patient_id",
            "exam_date",
            "manifest_cylinder_signed",
            "manifest_axis",
            "manifest_sphere",
        ]
        part["eye"] = eye
        pieces.append(part)
    long = pd.concat(pieces, ignore_index=True)
    long = long.dropna(subset=["patient_id", "exam_date"])
    long["patient_id"] = long["patient_id"].astype(int)
    for column in ["manifest_cylinder_signed", "manifest_axis", "manifest_sphere"]:
        long[column] = pd.to_numeric(long[column], errors="coerce")
    return long


def derive_cohorts(
    raw: RawFiles,
    inventory_path: str | Path,
    analysis_cfg: dict,
) -> CohortBundle:
    iol = load_iol(raw)
    iol = classify_iol_records(
        iol,
        inventory_path,
        set(analysis_cfg["toric_override_sha256"]),
    )
    near_cut = float(analysis_cfg["cohort"]["near_target_upper_exclusive_d"])
    near = iol[iol["target"] < near_cut].copy()
    near = near.reset_index(drop=False).rename(columns={"index": "surgery_row"})

    refraction = load_refraction_long(raw)
    joined = near.merge(refraction, on=["patient_id", "eye"], how="left")
    joined["days_postoperative"] = (
        joined["exam_date"] - joined["surgery_date"]
    ).dt.days

    day_min = int(analysis_cfg["cohort"]["postoperative_day_min"])
    day_max = int(analysis_cfg["cohort"]["postoperative_day_max"])
    reference_day = int(analysis_cfg["cohort"]["postoperative_reference_day"])

    # The final frozen audit first required a numerical cylinder, then selected
    # the visit nearest day 70 within days 30-180.
    candidates = joined[
        joined["days_postoperative"].between(day_min, day_max)
        & joined["manifest_cylinder_signed"].notna()
    ].copy()
    candidates["distance_to_reference_day"] = (
        candidates["days_postoperative"] - reference_day
    ).abs()
    selected = (
        candidates.sort_values(
            ["surgery_row", "distance_to_reference_day", "exam_date"],
            ascending=[True, True, True],
        )
        .drop_duplicates("surgery_row", keep="first")
        .copy()
    )

    manifest_observed = selected[selected["manifest_sphere"].notna()].copy()
    manifest_observed["residual_cylinder"] = manifest_observed[
        "manifest_cylinder_signed"
    ].abs()
    manifest_observed["achieved_se"] = (
        manifest_observed["manifest_sphere"]
        + manifest_observed["manifest_cylinder_signed"] / 2.0
    )
    manifest_observed["target_error"] = (
        manifest_observed["achieved_se"] - manifest_observed["target"]
    )

    lo = float(analysis_cfg["cohort"]["achieved_se_min_d"])
    hi = float(analysis_cfg["cohort"]["achieved_se_max_d"])
    primary = manifest_observed[
        manifest_observed["achieved_se"].between(lo, hi)
    ].copy()

    return CohortBundle(
        eligible=iol,
        near_target=near,
        manifest_observed=manifest_observed,
        primary=primary,
    )


def cohort_counts(bundle: CohortBundle) -> dict[str, int]:
    primary = bundle.primary
    return {
        "eligible_eyes": int(len(bundle.eligible)),
        "near_target_eyes": int(len(bundle.near_target)),
        "near_target_patients": int(bundle.near_target["patient_id"].nunique()),
        "manifest_refraction_observed_eyes": int(len(bundle.manifest_observed)),
        "manifest_refraction_observed_patients": int(
            bundle.manifest_observed["patient_id"].nunique()
        ),
        "primary_eyes": int(len(primary)),
        "primary_patients": int(primary["patient_id"].nunique()),
        "primary_toric_eyes": int(primary["toric"].sum()),
        "primary_nontoric_eyes": int((~primary["toric"]).sum()),
    }
