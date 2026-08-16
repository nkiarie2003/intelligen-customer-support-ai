#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate
export TRAINING_PLATFORM=azure_ml_compute_instance
export AZURE_ML_WORKSPACE="${AZURE_ML_WORKSPACE:-mlworkspace-traning}"
export AZURE_ML_COMPUTE="${AZURE_ML_COMPUTE:-c50411741-ML}"
python scripts/train_on_azure_compute.py --workspace "$AZURE_ML_WORKSPACE" --compute "$AZURE_ML_COMPUTE"
