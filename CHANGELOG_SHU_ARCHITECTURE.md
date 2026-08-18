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
## RBAC navigation and model-governance update
- Restricted **Model metrics** to administrator accounts at both navigation and route levels.
- Restricted **System & model status** to administrator accounts at both navigation and route levels.
- Added **Users** to the administrator navigation because the route already existed and was admin-protected.
- Customers now see only customer-facing navigation; agents retain operational Analytics, while model/infrastructure governance remains admin-only.
- Added route tests to prevent future regressions that could expose model or system information to non-admin users.


## Customer-safe interface and admin-only intelligence

- Rebuilt the customer dashboard around case progress and approved responses only.
- Removed category, sentiment, priority, model confidence, XAI, RAG, backend and draft-response details from customer pages.
- Added a dedicated administrator-only Complaint Intelligence page.
- Removed Analytics from the agent role and restricted it to administrators.
- Restricted model re-analysis to administrators.
- Kept a staff response workspace for agents without exposing model diagnostics.
- Added customer case progress tracking and response-availability states.
- Added dashboard search/status filters without exposing AI fields to customers.
- Redesigned landing, authentication, submission, complaint, staff and admin interfaces.
- Added regression tests for customer/agent/admin information boundaries.
