from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import create_app
from app.ai.training import train_classifier
from app.extensions import db

app = create_app()
with app.app_context():
    if not app.config["TRAINING_DATA"].exists():
        raise SystemExit(
            "Processed CFPB training data is missing. Run:\n"
            "  python scripts/download_kaggle_datasets.py\n"
            "  python scripts/prepare_datasets.py\n"
            "and then run bootstrap again."
        )
    db.create_all()
    metrics = train_classifier(app.config["TRAINING_DATA"], app.config["ARTIFACT_DIR"])
    print("Database initialised and CFPB classifier trained.")
    print(f"Rows={metrics['dataset_rows']}; Accuracy={metrics['accuracy']:.3f}; macro-F1={metrics['macro_f1']:.3f}")
    print("Next: flask --app run.py create-admin admin")
