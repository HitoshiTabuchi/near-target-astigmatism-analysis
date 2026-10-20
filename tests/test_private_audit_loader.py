from __future__ import annotations

import pytest

from near_target_pipeline.data_io import load_private_audit


def test_private_audit_block_is_read_from_private_config(tmp_path):
    cfg = tmp_path / "raw_files.yml"
    cfg.write_text(
        "raw_data_root: /private\n"
        "files: {}\n"
        "private_audit:\n"
        "  toric_override_sha256: ['" + "a" * 64 + "']\n"
        "  axial_validity_exclusion_sha256: []\n",
        encoding="utf-8",
    )
    assert load_private_audit(cfg) == {
        "toric_override_sha256": ["a" * 64],
        "axial_validity_exclusion_sha256": [],
    }


def test_missing_private_audit_block_stops_the_raw_run(tmp_path):
    cfg = tmp_path / "raw_files.yml"
    cfg.write_text("raw_data_root: /private\nfiles: {}\n", encoding="utf-8")
    with pytest.raises(KeyError):
        load_private_audit(cfg)
