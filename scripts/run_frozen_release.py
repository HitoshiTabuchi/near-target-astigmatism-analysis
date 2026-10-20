from pathlib import Path
import json

from near_target_pipeline.figures import regenerate_aggregate_figures
from near_target_pipeline.frozen import run_frozen_release


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    output = root / "outputs" / "frozen_release"
    report = run_frozen_release(root, output)
    report["regenerated_aggregate_figures"] = [
        str(path)
        for path in regenerate_aggregate_figures(
            root / "reference", output / "regenerated_figures"
        )
    ]
    (output / "frozen_release_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["passed"] else 1)
