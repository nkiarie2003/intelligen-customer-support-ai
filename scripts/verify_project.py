from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
checks = {
    "processed CFPB dataset": ROOT / "data/processed/cfpb_complaints.csv",
    "processed Twitter pairs": ROOT / "data/processed/twitter_support_pairs.csv",
    "trained classifier": ROOT / "artifacts/complaint_classifier.joblib",
    "metrics": ROOT / "artifacts/metrics.json",
    "training provenance": ROOT / "artifacts/training_provenance.json",
    "policy knowledge base": ROOT / "data/policies/company_policies.md",
}

print("IntelliGen project readiness")
print("=" * 38)
missing_required = False
for name, path in checks.items():
    exists = path.exists()
    print(f"{'OK' if exists else 'MISSING':8} {name:28} {path.relative_to(ROOT)}")
    if name in {"processed CFPB dataset", "trained classifier", "policy knowledge base"} and not exists:
        missing_required = True

metrics_path = ROOT / "artifacts/metrics.json"
if metrics_path.exists():
    try:
        m = json.loads(metrics_path.read_text(encoding="utf-8"))
        print("\nModel metrics")
        print(f"  accuracy:        {m.get('accuracy')}")
        print(f"  macro precision: {m.get('macro_precision')}")
        print(f"  macro recall:    {m.get('macro_recall')}")
        print(f"  macro F1:        {m.get('macro_f1')}")
    except Exception as exc:
        print("Could not read metrics:", exc)

sys.exit(1 if missing_required else 0)
