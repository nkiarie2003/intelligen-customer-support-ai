#!/usr/bin/env bash
set -euo pipefail
mkdir -p exports
zip -j exports/intelligen_model_artifacts.zip \
  artifacts/complaint_classifier.joblib \
  artifacts/metrics.json \
  artifacts/training_provenance.json

echo "Created exports/intelligen_model_artifacts.zip"
