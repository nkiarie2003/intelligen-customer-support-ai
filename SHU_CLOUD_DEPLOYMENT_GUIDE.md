# SHU Cloud Training Guide

## What is supported in this project

The default implementation uses the existing Azure ML compute instance as a remote cloud development/training machine. It does not create a managed online endpoint or Azure ML job resource.

### 1. Connect to the existing compute instance

Use Azure ML Studio or the Azure Machine Learning VS Code remote connection and select the existing compute instance.

### 2. Clone/upload the project

Ensure these are present on the compute instance:

```text
app/
scripts/
data/processed/cfpb_complaints.csv
requirements.txt
```

### 3. Train

```bash
bash azure_compute/setup_compute.sh
python azure_compute/verify_compute.py
bash azure_compute/train_on_compute.sh
```

### 4. Retrieve artifacts

```bash
bash azure_compute/package_artifacts.sh
```

Download/copy:

```text
complaint_classifier.joblib
metrics.json
training_provenance.json
```

into the local project's `artifacts/` folder.

### 5. Run Flask locally

```bash
python run.py
```

The model-status page will identify the classifier as trained on an Azure ML compute instance when the provenance file contains `training_platform=azure_ml_compute_instance`.
