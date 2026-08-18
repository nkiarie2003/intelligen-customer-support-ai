# Architecture — SHU-Compatible IntelliGen Customer Intelligence Platform

## Runtime architecture

```text
Customer / Support Agent
          |
          v
       Flask Web App
          |
          +--> Privacy minimisation / redaction
          |
          +--> Local TF-IDF + Logistic Regression classifier
          |       +--> confidence + top-3 predictions
          |       +--> linear feature-contribution XAI
          |
          +--> VADER sentiment
          |       +--> optional transformer sentiment
          |
          +--> transparent priority-scoring rules
          |
          +--> RAG policy retrieval
          |       +--> TF-IDF baseline
          |       +--> optional Sentence Transformer embeddings
          |
          +--> optional zero-shot transformer ensemble
          |
          +--> controlled response generation / optional FLAN-T5
          |
          +--> historical Twitter conversation examples (style only)
          |
          v
      Human review
      approve / edit / reject
          |
          v
       Audit trail
```

## Cloud model-development architecture

```text
Real CFPB Kaggle dataset
          |
          v
Existing Azure ML compute instance (interactive terminal / VS Code remote)
          |
          v
scripts/train_on_azure_compute.py
          |
          +--> model evaluation
          +--> complaint_classifier.joblib
          +--> metrics.json
          +--> training_provenance.json
          |
          v
Artifacts copied/downloaded to local project
          |
          v
Flask serves local real-time inference
```

This architecture intentionally avoids requiring Azure ML `onlineEndpoints` or Azure ML `jobs` resources. Optional endpoint files are retained in `azure_optional_endpoint/` for production-architecture discussion only.

## Why the hybrid design is academically useful

The project demonstrates a measurable classical baseline, modern transformer enhancements, explainability, retrieval-augmented generation, prompt constraints, human oversight, cloud compute, data governance and reproducibility in one integrated system.
## Role-based access control

```text
Customer
  ├─ Dashboard
  ├─ New complaint
  └─ Own complaint details

Support Agent
  ├─ Operational dashboard
  ├─ Complaint review
  └─ Analytics

Administrator
  ├─ All staff capabilities
  ├─ Model metrics
  ├─ System/model status and training provenance
  ├─ User list
  ├─ RAG knowledge management
  └─ Audit log
```

`Model metrics` and `System status` are enforced with an administrator-only route decorator, so non-admin users cannot reach them by typing the URLs directly.

