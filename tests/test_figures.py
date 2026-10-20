from __future__ import annotations

from near_target_pipeline.data_io import sha256_file
from near_target_pipeline.frozen import replay_figures


def test_final_figures_replay_byte_identically(repo_root, tmp_path):
    manifest = replay_figures(repo_root / "reference", tmp_path)
    assert len(manifest) == 8
    assert all(row["identical"] for row in manifest)
    for row in manifest:
        assert row["sha256_reference"] == row["sha256_replayed"]
        assert sha256_file(tmp_path / "figures" / row["filename"]) == row["sha256_reference"]
