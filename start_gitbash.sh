#!/usr/bin/env bash
set -e
if [ -f .venv/Scripts/activate ]; then source .venv/Scripts/activate; fi
python run.py
