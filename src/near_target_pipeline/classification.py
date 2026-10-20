from __future__ import annotations

from pathlib import Path
import hashlib
import re

import pandas as pd

from .data_io import normalise_iol_model


def _majority_models(inventory: pd.DataFrame, column: str) -> set[str]:
    inv = inventory.copy()
    inv["model_norm"] = inv["IOL model"].map(normalise_iol_model)
    inv["is_yes"] = inv[column].eq("Yes")
    totals = inv.groupby("model_norm", observed=True).apply(
        lambda g: pd.Series(
            {
                "yes": float(g.loc[g["is_yes"], "Eyes"].sum()),
                "no": float(g.loc[~g["is_yes"], "Eyes"].sum()),
            }
        ),
        include_groups=False,
    )
    return set(totals.index[totals["yes"] > totals["no"]])


def record_fingerprint(patient_id: int, eye: str, surgery_date: pd.Timestamp, model: str) -> str:
    payload = f"{int(patient_id)}|{eye}|{pd.Timestamp(surgery_date):%Y-%m-%d}|{normalise_iol_model(model)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def classify_iol_records(
    records: pd.DataFrame,
    inventory_path: str | Path,
    toric_override_hashes: set[str],
) -> pd.DataFrame:
    inventory = pd.read_csv(inventory_path)
    toric_models = _majority_models(inventory, "Toric classification")
    premium_models = _majority_models(inventory, "Procedure-coded premium/EDOF")
    expanded_models = _majority_models(
        inventory, "Expanded nonconventional-optics classification"
    )

    out = records.copy()
    out["iol_model_norm"] = out["iol_model"].map(normalise_iol_model)
    procedure = out["procedure"].fillna("").astype(str)
    out["toric"] = out["iol_model_norm"].isin(toric_models) | procedure.str.contains(
        r"トーリック|toric", case=False, regex=True
    )

    fingerprints = [
        record_fingerprint(pid, eye, date, model)
        for pid, eye, date, model in zip(
            out["patient_id"], out["eye"], out["surgery_date"], out["iol_model_norm"]
        )
    ]
    out["toric_manual_audit"] = pd.Series(fingerprints, index=out.index).isin(
        toric_override_hashes
    )
    out["toric"] = out["toric"] | out["toric_manual_audit"]

    out["premium_proc"] = out["iol_model_norm"].isin(premium_models)
    # Row-level rules used in the final procedure-text audit.
    is_rao = out["iol_model_norm"].eq("RAO200E")
    out.loc[is_rao, "premium_proc"] = procedure[is_rao].str.contains(
        r"自費|自由診療", regex=True
    )
    is_ls_t1 = out["iol_model_norm"].eq("LS-313 MF15T1")
    out.loc[is_ls_t1, "premium_proc"] = procedure[is_ls_t1].str.contains(
        "多焦点トーリック", regex=False
    )
    is_ic8 = out["iol_model_norm"].eq("IC-8")
    out.loc[is_ic8, "premium_proc"] = procedure[is_ic8].str.contains(
        "IC-8", regex=False
    )

    out["nonconventional_expanded"] = out["iol_model_norm"].isin(expanded_models)
    return out
