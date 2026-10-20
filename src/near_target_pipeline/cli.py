from __future__ import annotations

import argparse
import json
from pathlib import Path

from .cohort import cohort_counts, derive_cohorts
from .covariates import derive_primary_covariates
from .data_io import load_private_audit, load_yaml, resolve_raw_files, validate_raw_manifest
from .figures import regenerate_aggregate_figures
from .frozen import run_frozen_release
from .models import run_raw_primary_analysis


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def command_frozen(args: argparse.Namespace) -> int:
    root = Path(args.repo_root or _repo_root())
    out = Path(args.output)
    report = run_frozen_release(root, out)
    regenerated = regenerate_aggregate_figures(root / "reference", out / "regenerated_figures")
    report["regenerated_aggregate_figures"] = [str(p) for p in regenerated]
    (out / "frozen_release_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


def command_raw(args: argparse.Namespace) -> int:
    root = Path(args.repo_root or _repo_root())
    cfg = load_yaml(root / "config" / "analysis.yml")
    cfg.update(load_private_audit(args.raw_config))
    raw = resolve_raw_files(args.raw_config)
    manifest = validate_raw_manifest(raw, root / "reference" / "raw_input_manifest.json")
    bundle = derive_cohorts(
        raw, root / "reference" / "model_outputs" / "iol_model_inventory.csv", cfg
    )
    counts = cohort_counts(bundle)
    analysis = derive_primary_covariates(bundle.primary, bundle.eligible, raw, cfg)
    pooled, components = run_raw_primary_analysis(analysis, cfg)
    expected = json.loads((root / "reference" / "expected_results.json").read_text())
    margin = float(expected["raw_verification_equivalence_margin_d"])
    coefficient_difference = pooled["coefficient"] - float(expected["primary_coefficient_d"])
    report = {
        "mode": "raw_source_verification",
        "raw_hashes_match": manifest,
        "all_required_raw_hashes_match": all(manifest.values()),
        "counts": counts,
        "pooled": pooled,
        "frozen_reference_coefficient": expected["primary_coefficient_d"],
        "coefficient_difference": coefficient_difference,
        "equivalence_margin_d": margin,
        "within_equivalence_margin": abs(coefficient_difference) <= margin,
    }
    expected_count_keys = [
        "eligible_eyes", "near_target_eyes", "near_target_patients",
        "manifest_refraction_observed_eyes", "manifest_refraction_observed_patients",
        "primary_eyes", "primary_patients", "primary_toric_eyes", "primary_nontoric_eyes",
    ]
    report["count_checks"] = {k: counts[k] == int(expected[k]) for k in expected_count_keys}
    report["all_counts_match"] = all(report["count_checks"].values())
    report["passed"] = bool(report["all_counts_match"] and report["within_equivalence_margin"])
    out = Path(args.output); out.mkdir(parents=True, exist_ok=True)
    components.to_csv(out / "raw_verification_mi_components.csv", index=False)
    (out / "raw_verification_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="near-target-pipeline")
    parser.add_argument("--repo-root", default=None)
    sub = parser.add_subparsers(dest="command", required=True)
    f = sub.add_parser("frozen", help="Replay and verify the exact archived release")
    f.add_argument("--output", default="outputs/frozen_release")
    f.set_defaults(func=command_frozen)
    r = sub.add_parser("raw", help="Rebuild cohort and independently rerun the model from private raw files")
    r.add_argument("--raw-config", required=True)
    r.add_argument("--output", default="outputs/raw_verification")
    r.set_defaults(func=command_raw)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
