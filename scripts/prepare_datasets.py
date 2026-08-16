from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.ai.datasets import (
    CFPB_PRODUCT_ALIASES,
    CFPB_TEXT_ALIASES,
    TWITTER_REQUIRED,
    prepare_cfpb_dataset,
    prepare_twitter_pairs,
)
import pandas as pd


def find_cfpb_csv(folder: Path) -> Path | None:
    for path in sorted(folder.rglob("*.csv")):
        try:
            cols = {str(c).strip().casefold() for c in pd.read_csv(path, nrows=0).columns}
        except Exception:
            continue
        has_text = any(a.casefold() in cols for a in CFPB_TEXT_ALIASES)
        has_product = any(a.casefold() in cols for a in CFPB_PRODUCT_ALIASES)
        if has_text and has_product:
            return path
    return None


def find_twitter_csv(folder: Path) -> Path | None:
    for path in sorted(folder.rglob("*.csv")):
        try:
            cols = {str(c).strip() for c in pd.read_csv(path, nrows=0).columns}
        except Exception:
            continue
        if TWITTER_REQUIRED.issubset(cols):
            return path
    return None


def main():
    parser = argparse.ArgumentParser(description="Prepare real Kaggle complaint/support datasets.")
    parser.add_argument("--cfpb", type=Path, help="Path to the CFPB CSV; auto-detected if omitted")
    parser.add_argument("--twitter", type=Path, help="Path to twcs.csv; auto-detected if omitted")
    parser.add_argument("--max-per-class", type=int, default=5000)
    parser.add_argument("--max-twitter-pairs", type=int, default=50000)
    parser.add_argument("--skip-twitter", action="store_true")
    args = parser.parse_args()

    cfpb = args.cfpb or find_cfpb_csv(ROOT / "data" / "raw" / "cfpb")
    if not cfpb:
        raise SystemExit(
            "CFPB CSV not found. Run python scripts/download_kaggle_datasets.py or pass --cfpb PATH."
        )

    processed = ROOT / "data" / "processed"
    report = {
        "cfpb": prepare_cfpb_dataset(
            cfpb,
            processed / "cfpb_complaints.csv",
            max_per_class=args.max_per_class,
        )
    }

    if not args.skip_twitter:
        twitter = args.twitter or find_twitter_csv(ROOT / "data" / "raw" / "twitter")
        if twitter:
            report["twitter"] = prepare_twitter_pairs(
                twitter,
                processed / "twitter_support_pairs.csv",
                max_pairs=args.max_twitter_pairs,
            )
        else:
            report["twitter"] = {"warning": "Twitter CSV not found; conversational examples will be unavailable."}

    (processed / "preparation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print("\nNext: python scripts/bootstrap.py")


if __name__ == "__main__":
    main()
