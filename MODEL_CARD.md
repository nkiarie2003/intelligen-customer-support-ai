# Model Card — Complaint Category Classifier

## Model
TF-IDF (unigrams + bigrams) followed by class-weighted multiclass Logistic Regression.

## Training data
A locally processed sample of real CFPB consumer complaint narratives obtained from the Kaggle dataset `namigabbasov/consumer-complaint-dataset`.

## Target
Eight mapped categories derived from the CFPB Product field:

- credit_reporting
- debt_collection
- mortgage
- credit_card
- bank_account
- loan
- payments_transfers
- other_financial_service

## Why retain a classical baseline?
The model is fast, measurable, reproducible and locally explainable through linear feature contributions. This makes it useful for comparison with the optional zero-shot transformer rather than relying only on a less-transparent deep-learning component.

## Evaluation
`python scripts/bootstrap.py` performs a stratified 80/20 train/test split and writes accuracy, macro-F1, weighted-F1, per-class metrics and a confusion matrix to `artifacts/metrics.json`.

No fixed scores are included in this archive because the Kaggle data itself is not redistributed. Report only the metrics generated from the exact processed dataset used in your experiment.

## XAI
For an individual prediction, the application multiplies active TF-IDF feature values by the predicted class's logistic-regression coefficients and displays the strongest positive cues. These are model-attribution cues, **not causal explanations**.

## Optional deep-learning ensemble
When enabled, a zero-shot transformer predicts over the same categories and is blended conservatively with the supervised baseline. The baseline remains dominant so the system retains an auditable reference model.

## Intended use
MSc prototype for complaint triage, routing, prioritisation and response-drafting support with mandatory human oversight.

## Not intended for
- automated financial decisions;
- legal conclusions;
- credit eligibility or underwriting;
- automatic denial of complaints;
- unsupervised customer profiling with material consequences.

## Known risks
Domain shift, class-label simplification, historical/taxonomy bias, linguistic bias, privacy risk, confidence misinterpretation and false reassurance from XAI. Human review is mandatory.
