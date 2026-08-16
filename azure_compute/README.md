# SHU Azure ML Compute-Instance Training

This project deliberately uses **cloud training + local Flask inference** in the Sheffield Hallam lab environment.

The existing Azure ML compute instance is used interactively. The workflow does **not** create an Azure ML job resource or managed online endpoint, because those resource types can be denied by the lab's Allowed Resource Types policy.

## On the Azure ML compute instance

```bash
cd IntelliGen_Customer_Intelligence_Platform_SHU
bash azure_compute/setup_compute.sh
python azure_compute/verify_compute.py
bash azure_compute/train_on_compute.sh
```

The training process writes:

- `artifacts/complaint_classifier.joblib`
- `artifacts/metrics.json`
- `artifacts/training_provenance.json`

Copy/download those artifacts back to the local Flask project before running the web app. The model-status page will display the recorded Azure workspace/compute provenance.
