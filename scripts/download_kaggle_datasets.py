from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

DATASETS = {
    "cfpb": ("namigabbasov/consumer-complaint-dataset", RAW / "cfpb"),
    "twitter": ("thoughtvector/customer-support-on-twitter", RAW / "twitter"),
}


def main():
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError:
        raise SystemExit("Install data tooling first: pip install -r requirements-data.txt")

    api = KaggleApi()
    try:
        api.authenticate()
    except Exception as exc:
        raise SystemExit(
            "Kaggle authentication failed. Configure your Kaggle API token, then retry. "
            f"Original error: {exc}"
        )

    for name, (slug, destination) in DATASETS.items():
        destination.mkdir(parents=True, exist_ok=True)
        print(f"Downloading {name}: {slug}")
        api.dataset_download_files(slug, path=str(destination), unzip=True, quiet=False)
        print(f"Saved under {destination}")


if __name__ == "__main__":
    main()
