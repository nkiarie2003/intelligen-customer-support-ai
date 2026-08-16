# Kaggle Dataset Setup

## Datasets

1. **Consumer Complaint Dataset** — Kaggle slug: `namigabbasov/consumer-complaint-dataset`
2. **Customer Support on Twitter** — Kaggle slug: `thoughtvector/customer-support-on-twitter`

## Recommended workflow

```bash
pip install -r requirements.txt
pip install -r requirements-data.txt
python scripts/download_kaggle_datasets.py
python scripts/prepare_datasets.py
python scripts/bootstrap.py
```

## Manual-download workflow

If you prefer not to use the Kaggle API, download and unzip the datasets yourself, then place the CSV files inside:

```text
data/raw/cfpb/
data/raw/twitter/
```

The preparation script auto-detects the appropriate CSV from its columns.

You can also pass exact file paths:

```bash
python scripts/prepare_datasets.py --cfpb "C:/path/to/cfpb.csv" --twitter "C:/path/to/twcs.csv"
```

## Generated files

```text
data/processed/cfpb_complaints.csv
data/processed/twitter_support_pairs.csv
data/processed/preparation_report.json
artifacts/complaint_classifier.joblib
artifacts/metrics.json
```

These generated datasets/model artifacts are intentionally excluded from Git by default.
