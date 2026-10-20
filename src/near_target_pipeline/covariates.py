from __future__ import annotations

from pathlib import Path
import hashlib

import numpy as np
import pandas as pd

from .classification import record_fingerprint
from .data_io import RawFiles


def _record_hashes(frame: pd.DataFrame) -> pd.Series:
    return pd.Series(
        [
            record_fingerprint(pid, eye, date, model)
            for pid, eye, date, model in zip(
                frame["patient_id"],
                frame["eye"],
                frame["surgery_date"],
                frame["iol_model_norm"],
            )
        ],
        index=frame.index,
    )


def attach_preoperative_keratometry(
    primary: pd.DataFrame, raw: RawFiles, cfg: dict
) -> pd.DataFrame:
    source = pd.read_excel(raw.keratometry).rename(
        columns={
            "ID": "patient_id",
            "検査日": "exam_date",
            "右 乱視度数": "R_cylinder",
            "左 乱視度数": "L_cylinder",
            "角膜乱視軸・右": "R_axis",
            "角膜乱視軸・左": "L_axis",
            "乱視軸判断・右": "R_axis_type_jp",
            "乱視軸判断・左": "L_axis_type_jp",
        }
    )
    source["patient_id"] = pd.to_numeric(source["patient_id"], errors="coerce")
    source["exam_date"] = pd.to_datetime(source["exam_date"], errors="coerce")
    source = source.dropna(subset=["patient_id", "exam_date"]).copy()
    source["patient_id"] = source["patient_id"].astype(int)
    source["file_order"] = np.arange(len(source))

    base = primary.reset_index(drop=True).reset_index(names="analysis_row")
    joined = base[
        ["analysis_row", "patient_id", "eye", "surgery_date"]
    ].merge(source, on="patient_id", how="left")
    joined["days_before_surgery"] = (
        joined["surgery_date"] - joined["exam_date"]
    ).dt.days
    joined["preop_cylinder"] = pd.to_numeric(
        np.where(joined["eye"].eq("R"), joined["R_cylinder"], joined["L_cylinder"]),
        errors="coerce",
    )
    joined["preop_axis"] = pd.to_numeric(
        np.where(joined["eye"].eq("R"), joined["R_axis"], joined["L_axis"]),
        errors="coerce",
    )
    joined["axis_type_jp"] = np.where(
        joined["eye"].eq("R"), joined["R_axis_type_jp"], joined["L_axis_type_jp"]
    )

    max_days = int(cfg["cohort"]["keratometry_lookback_days"])
    cyl_min = float(cfg["cohort"]["preoperative_cylinder_min_d"])
    cyl_max = float(cfg["cohort"]["preoperative_cylinder_max_d"])
    joined = joined[
        joined["days_before_surgery"].between(0, max_days)
        & joined["preop_cylinder"].between(cyl_min, cyl_max)
    ]
    selected = (
        joined.sort_values(["analysis_row", "file_order"])
        .drop_duplicates("analysis_row", keep="last")
        [["analysis_row", "preop_cylinder", "preop_axis", "axis_type_jp"]]
    )
    out = base.merge(selected, on="analysis_row", how="left").drop(
        columns="analysis_row"
    )
    out["axis_type"] = out["axis_type_jp"].map(
        {"直乱視": "WTR", "倒乱視": "ATR", "斜乱視": "Oblique"}
    )
    return out


def attach_axial_length(primary: pd.DataFrame, raw: RawFiles, cfg: dict) -> pd.DataFrame:
    pieces: list[pd.DataFrame] = []
    for path in [raw.axial_site_a, raw.axial_site_b]:
        frame = pd.read_excel(path).rename(
            columns={
                "ＩＤ": "patient_id",
                "検査日": "exam_date",
                "L眼軸長": "L_axial_length",
                "R眼軸長": "R_axial_length",
            }
        )
        pieces.append(frame)
    source = pd.concat(pieces, ignore_index=True)
    source["patient_id"] = pd.to_numeric(source["patient_id"], errors="coerce")
    source["exam_date"] = pd.to_datetime(source["exam_date"], errors="coerce")
    source = source.dropna(subset=["patient_id", "exam_date"]).copy()
    source["patient_id"] = source["patient_id"].astype(int)
    source["file_order"] = np.arange(len(source))

    base = primary.reset_index(drop=True).reset_index(names="analysis_row")
    joined = base[
        ["analysis_row", "patient_id", "eye", "surgery_date", "iol_model_norm"]
    ].merge(source, on="patient_id", how="left")
    joined["days_before_surgery"] = (
        joined["surgery_date"] - joined["exam_date"]
    ).dt.days
    joined["axial_length"] = pd.to_numeric(
        np.where(
            joined["eye"].eq("L"),
            joined["L_axial_length"],
            joined["R_axial_length"],
        ),
        errors="coerce",
    )
    max_days = int(cfg["cohort"]["axial_length_lookback_days"])
    lo = float(cfg["cohort"]["axial_length_min_mm"])
    hi = float(cfg["cohort"]["axial_length_max_mm"])
    joined = joined[
        joined["days_before_surgery"].between(0, max_days)
        & joined["axial_length"].between(lo, hi)
    ]
    selected = (
        joined.sort_values(["analysis_row", "file_order"])
        .drop_duplicates("analysis_row", keep="last")
        [["analysis_row", "axial_length"]]
    )
    out = base.merge(selected, on="analysis_row", how="left").drop(
        columns="analysis_row"
    )
    hashes = _record_hashes(out)
    exclusions = set(cfg.get("axial_validity_exclusion_sha256", []))
    out.loc[hashes.isin(exclusions), "axial_length"] = np.nan
    return out


def attach_fellow_eye(primary: pd.DataFrame, eligible: pd.DataFrame) -> pd.DataFrame:
    base = primary.reset_index(drop=True).reset_index(names="analysis_row")
    fellow = eligible[
        ["patient_id", "eye", "surgery_date", "target", "toric"]
    ].rename(
        columns={
            "eye": "fellow_eye",
            "surgery_date": "fellow_surgery_date",
            "target": "fellow_target",
            "toric": "fellow_toric",
        }
    )
    candidates = base[
        ["analysis_row", "patient_id", "eye", "surgery_date"]
    ].merge(fellow, on="patient_id", how="left")
    candidates = candidates[candidates["eye"].ne(candidates["fellow_eye"])].copy()
    candidates["absolute_surgery_gap"] = (
        candidates["fellow_surgery_date"] - candidates["surgery_date"]
    ).dt.days.abs()
    selected = (
        candidates.sort_values(
            ["analysis_row", "absolute_surgery_gap", "fellow_surgery_date"]
        )
        .drop_duplicates("analysis_row", keep="first")
        [["analysis_row", "fellow_target", "fellow_toric"]]
    )
    return base.merge(selected, on="analysis_row", how="left").drop(
        columns="analysis_row"
    )


def derive_primary_covariates(
    primary: pd.DataFrame, eligible: pd.DataFrame, raw: RawFiles, cfg: dict
) -> pd.DataFrame:
    out = attach_preoperative_keratometry(primary, raw, cfg)
    out = attach_axial_length(out, raw, cfg)
    out = attach_fellow_eye(out, eligible)
    out["female"] = out["sex"].astype(str).str.upper().eq("F").astype(float)
    out["fellow_toric"] = out["fellow_toric"].astype(float)
    out["surgeon_code"] = pd.Categorical(
        out["surgeon"].fillna("Missing").astype(str)
    ).codes.astype(float)
    out["axis_code"] = pd.Categorical(
        out["axis_type"].fillna("Missing").astype(str)
    ).codes.astype(float)
    return out
