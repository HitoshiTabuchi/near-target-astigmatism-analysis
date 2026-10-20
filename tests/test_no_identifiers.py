from __future__ import annotations

import os
import re
from pathlib import Path

import pytest
import yaml

TEXT_SUFFIXES = {".py", ".md", ".yml", ".yaml", ".json", ".toml", ".txt", ".csv", ".cff"}


def test_public_tree_contains_no_source_workbooks(repo_root):
    forbidden_suffixes = {".xlsx", ".xls", ".pkl"}
    offenders = [p for p in repo_root.rglob("*") if p.is_file() and p.suffix.lower() in forbidden_suffixes]
    assert not offenders, offenders


def test_public_config_holds_no_record_fingerprints(repo_root):
    cfg = yaml.safe_load((repo_root / "config" / "analysis.yml").read_text(encoding="utf-8"))
    assert "toric_override_sha256" not in cfg
    assert "axial_validity_exclusion_sha256" not in cfg
    assert "private_audit" not in cfg
    hexes = re.findall(r"\b[0-9a-f]{64}\b", (repo_root / "config" / "analysis.yml").read_text(encoding="utf-8"))
    assert not hexes, hexes


def test_private_identifiers_are_absent(repo_root):
    """Checks the public tree against identifiers held only by the authors.

    Set NEAR_TARGET_PRIVATE_TOKENS to a private text file with one token per line.
    The tokens themselves are never stored in this repository.
    """
    value = os.environ.get("NEAR_TARGET_PRIVATE_TOKENS")
    if not value or not Path(value).exists():
        pytest.skip("NEAR_TARGET_PRIVATE_TOKENS not set; private identifier check skipped")
    tokens = {t.strip() for t in Path(value).read_text(encoding="utf-8").splitlines() if t.strip()}
    hits = []
    for path in repo_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        hits += [(str(path.relative_to(repo_root)), "<private token>") for t in tokens if t in text]
    assert not hits, hits
