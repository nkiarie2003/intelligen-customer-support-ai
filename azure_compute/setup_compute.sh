#!/usr/bin/env bash
set -euo pipefail

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Azure compute environment ready."
echo "Next: python scripts/train_on_azure_compute.py"
