from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
from typing import Any

import pandas as pd
import yaml


@dataclass(frozen=True)
class RawFiles:
    root: Path
    iol: Path
    refraction: Path
    keratometry: Path
    axial_site_a: Path
    axial_site_b: Path
    casia1: Path
    casia2: Path
    iol_axis_deviation: Path
    va_site_b: Path
    va_site_a: Path


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_raw_files(config_path: str | Path) -> RawFiles:
    cfg = load_yaml(config_path)
    root = Path(cfg["raw_data_root"]).expanduser().resolve()
    files = cfg["files"]
    kwargs = {name: root / filename for name, filename in files.items()}
    missing = [str(p) for p in kwargs.values() if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing private source files:\n" + "\n".join(missing))
    return RawFiles(root=root, **kwargs)


def load_private_audit(config_path: str | Path) -> dict[str, list[str]]:
    """Manual-audit record fingerprints held in the private raw-source configuration."""
    block = (load_yaml(config_path) or {}).get("private_audit") or {}
    out = {}
    for key in ("toric_override_sha256", "axial_validity_exclusion_sha256"):
        if key not in block:
            raise KeyError(
                f"private_audit.{key} is missing from {config_path}; see config/raw_files.example.yml"
            )
        out[key] = list(block[key] or [])
    return out


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_raw_manifest(raw: RawFiles, manifest_path: str | Path) -> dict[str, bool]:
    expected = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    result: dict[str, bool] = {}
    for field in raw.__dataclass_fields__:
        if field == "root":
            continue
        path = getattr(raw, field)
        entry = expected.get(field)
        result[field] = bool(entry and sha256_file(path) == entry["sha256"])
    return result


def normalise_iol_model(value: Any) -> str:
    if pd.isna(value):
        return "Missing"
    text = str(value).strip()
    if text.endswith(".0") and text[:-2].isdigit():
        text = text[:-2]
    return text
