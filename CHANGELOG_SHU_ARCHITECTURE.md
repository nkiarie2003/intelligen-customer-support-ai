# SHU Architecture Changes

This revision changes the earlier Azure-online-endpoint design to match the university lab environment.

## Removed from the live runtime
- `USE_AZURE_CLASSIFIER`
- `AZURE_ML_SCORING_URI`
- `AZURE_ML_API_KEY`
- runtime import of the Azure endpoint client

## Added
- interactive Azure ML compute-instance training script
- model training provenance artifact
- cloud/local architecture status page
- staff complaint re-analysis after model updates
- business analytics page
- obvious sensitive-value minimisation
- retention/purge CLI
- macro precision and macro recall metrics
- updated real-data notebook
- optional endpoint implementation isolated under `azure_optional_endpoint/`

## Default architecture

```text
Azure ML compute instance -> train/evaluate -> artifact/provenance -> local Flask inference -> human review
```
