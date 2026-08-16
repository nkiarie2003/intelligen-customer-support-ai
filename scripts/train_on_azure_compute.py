"""Run this script *inside the existing Azure ML compute instance terminal*.

It does not create an Azure ML job or online endpoint. It trains interactively on the
already-provisioned compute instance and writes auditable model/provenance artifacts.
"""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.ai.training import train_classifier


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=os.getenv("AZURE_ML_WORKSPACE", "mlworkspace-traning"))
    parser.add_argument("--compute", default=os.getenv("AZURE_ML_COMPUTE", "c50411741-ML"))
    parser.add_argument("--data", default=str(ROOT / "data" / "processed" / "cfpb_complaints.csv"))
    parser.add_argument("--artifacts", default=str(ROOT / "artifacts"))
    args = parser.parse_args()

    os.environ["TRAINING_PLATFORM"] = "azure_ml_compute_instance"
    os.environ["AZURE_ML_WORKSPACE"] = args.workspace
    os.environ["AZURE_ML_COMPUTE"] = args.compute

    metrics = train_classifier(Path(args.data), Path(args.artifacts))
    print("\nAzure-compute training complete")
    print(f"Workspace: {args.workspace}")
    print(f"Compute:   {args.compute}")
    print(f"Rows:      {metrics['dataset_rows']}")
    print(f"Accuracy:  {metrics['accuracy']:.4f}")
    print(f"Macro F1:  {metrics['macro_f1']:.4f}")
    print(f"Model:     {Path(args.artifacts) / 'complaint_classifier.joblib'}")
    print(f"Provenance:{Path(args.artifacts) / 'training_provenance.json'}")


if __name__ == "__main__":
    main()
