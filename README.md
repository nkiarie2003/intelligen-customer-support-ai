# IntelliGen AI-Powered Customer Support & Complaint Intelligence Platform

A full Flask MSc demonstration application for the IntelliGen interview scenario. It combines **real consumer complaint data**, traditional ML, NLP, deep learning options, explainable AI, RAG, prompt engineering, cloud model development and human-in-the-loop governance.

## AI/ML areas demonstrated

1. **Natural Language Processing** — complaint cleaning, TF-IDF, semantic retrieval and conversation analysis.
2. **Classification** — real CFPB complaint narratives are classified into stable financial-service categories.
3. **Sentiment Analysis** — VADER baseline with optional transformer sentiment.
4. **Neural Networks / Deep Learning** — optional zero-shot transformer, transformer sentiment, sentence embeddings and FLAN-T5 generation.
5. **Explainable AI (XAI)** — local token/feature contributions from the supervised classifier plus explicit priority reasons.
6. **Prompt Engineering** — response prompts restrict invented policy/outcomes and require human review.
7. **Cloud AI/ML** — model training and experimentation can run interactively on an existing Azure ML compute instance; the resulting model is served locally by Flask.
8. **Advanced element: RAG** — policy evidence is retrieved before a response is drafted; Twitter conversations are used only for style/examples, never as policy authority.



## Data

Primary real dataset:
- CFPB consumer complaint data obtained from a Kaggle mirror.
- Used for supervised complaint classification.

Secondary real dataset:
- Customer Support on Twitter.
- Used to reconstruct customer → support-agent examples for tone/structure retrieval.
- It is **not** treated as policy truth.

The large datasets are not redistributed in this archive. Follow `KAGGLE_DATASET_SETUP.md`.

## Main workflow

```text
Customer message
      |
      v
Sensitive-value minimisation
      |
      +------------------+
      |                  |
      v                  v
Classification       Sentiment
      |                  |
      +--------+---------+
               v
         Priority score
               |
               v
        Explainable AI
               |
               v
         Policy retrieval
               |
               +--> conversation examples (style only)
               |
               v
       Controlled AI draft
               |
               v
          Human review
        approve/edit/reject
               |
               v
            Audit log
```

## Project structure

```text
app/
  ai/
    classifier.py
    training.py
    datasets.py
    sentiment.py
    priority.py
    rag.py
    generator.py
    transformers_service.py
    conversation_examples.py
    safety.py
    provenance.py
  templates/
  static/
  auth.py
  complaints.py
  admin.py
  api.py
  main.py
  system_status.py

data/
  raw/
  processed/
  policies/

artifacts/
notebooks/
scripts/
azure_compute/
azure_optional_endpoint/
tests/
```

## Windows / VS Code setup

From Git Bash or PowerShell in the project folder:

```bash
python -m venv .venv
```

Git Bash:

```bash
source .venv/Scripts/activate
```

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the baseline application:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy the environment template:

```bash
cp .env.example .env
```

On Windows PowerShell you can instead run:

```powershell
Copy-Item .env.example .env
```

The correct SQLite configuration is:

```env
DATABASE_URL=sqlite:///customer_intelligence.db
```


## Download and prepare Kaggle data

Install the data helper:

```bash
pip install -r requirements-data.txt
```

Authenticate to Kaggle, then:

```bash
python scripts/download_kaggle_datasets.py
python scripts/prepare_datasets.py
```

Expected files:

```text
data/processed/cfpb_complaints.csv
data/processed/twitter_support_pairs.csv
```

## Train locally

```bash
python scripts/train_models.py
```

or:

```bash
python -m flask --app run.py train-models
```

Outputs:

```text
artifacts/complaint_classifier.joblib
artifacts/metrics.json
artifacts/training_provenance.json
```

## Advanced AI features

Install:

```bash
pip install -r requirements-advanced.txt
```

Then enable features selectively in `.env`:

```env
ENABLE_ZERO_SHOT=true
ENABLE_TRANSFORMER_SENTIMENT=true
ENABLE_EMBEDDINGS=true
ENABLE_LOCAL_GENERATOR=true
```

These are intentionally optional because transformer models require more memory, disk space and computation than the baseline.

## Role-based navigation and access

The web interface follows least-privilege role separation:

- **Customer:** Dashboard, New complaint, own complaint records, sign out.
- **Agent:** Customer-facing operational views plus **Analytics** and case-review actions.
- **Admin:** Agent capabilities plus **Model metrics**, **System status**, **Users**, **Knowledge**, and **Audit**.

Model metrics and system/training status are protected on the server with `admin_required`; hiding the navbar links is not the security control by itself. Customers and agents receive HTTP 403 if they manually request those administrator routes.

## Create administrator / agent accounts

```bash
python -m flask --app run.py create-admin admin
```

Create a support agent:

```bash
python -m flask --app run.py create-admin agent1 --role agent
```

The command asks for a new application password; it is not your Windows, Kaggle or Azure password.

## Run Flask

```bash
python run.py
```

Open:

```text
http://127.0.0.1:5000
```

## Main web features

- customer registration/login
- customer complaint submission
- automatic complaint classification
- confidence and top predictions
- sentiment analysis
- transparent priority score
- XAI explanation cues
- RAG policy evidence
- optional semantic embeddings
- optional transformer models
- controlled AI response drafting
- human approve/edit/reject workflow
- staff re-analysis after model updates
- complaint analytics dashboard
- administrator-only model metrics dashboard
- administrator-only system/model status and training provenance
- model/cloud training provenance dashboard
- knowledge-base management
- audit log
- REST analysis API
- obvious card/PIN/OTP-style secret minimisation
- retention/purge CLI for old closed cases

## Model lifecycle demonstration

After retraining a new classifier and replacing the artifact, restart Flask and use the staff **Re-analyse with current model** action on an existing case. This demonstrates model version lifecycle effects without silently rewriting historic decisions.

## Privacy and human oversight

The prototype:
- masks obvious high-risk card/PIN/OTP-like values before persistence/analysis;
- warns users not to submit secrets;
- does not automatically send AI-generated replies;
- requires a human agent to approve/edit/reject the draft;
- records audit events;
- includes a configurable retention period and destructive purge command.

These controls support discussion of UK GDPR principles such as data minimisation, security, retention and meaningful human oversight. They do not make the prototype production-compliant by themselves.

## Environmental discussion

The baseline TF-IDF + Logistic Regression model is deliberately retained because it is lightweight, measurable and explainable. Transformer features are optional so you can compare the possible performance/semantic benefits against greater memory, compute and energy use.

## Verification

After preparing data and training:

```bash
python scripts/verify_project.py
```

Run unit tests:

```bash
pytest -q
```

## Assignment positioning

This implementation supports discussion of:
- IDE vs command-line development;
- reproducible configuration;
- real-data limitations and domain shift;
- traditional ML vs transformers;
- responsible AI and human oversight;
- cloud governance restrictions;
- business value of automated triage and analytics;
- legal/privacy risk;
- environmental cost of increasingly large models;
- limitations of code-generation tools and the need for review/testing.

## Role-specific interface and information boundaries

The current SHU build deliberately separates customer support information from AI/model diagnostics.

- **Customer:** submit complaints, see own cases, follow simple progress and read only human-approved responses.
- **Support agent:** access the case queue, review complaint text and prepare/approve/reject customer responses. Model diagnostics are not exposed.
- **Administrator:** access complaint intelligence, analytics, model metrics, system status, users, RAG knowledge and audit records.

The administrator-only complaint intelligence route contains classification confidence, sentiment score, priority rationale, XAI cues, RAG evidence and backend diagnostics. Customers and agents receive HTTP 403 if they attempt to open that route directly.
