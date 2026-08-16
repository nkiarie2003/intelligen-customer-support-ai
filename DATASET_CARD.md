# Dataset Card — Real Complaint and Customer-Support Data

## Primary dataset
**CFPB Consumer Complaint Dataset**, downloaded from the Kaggle dataset `namigabbasov/consumer-complaint-dataset`.

### Purpose
Supervised NLP classification of consumer complaint narratives.

### Input
`Consumer complaint narrative` (or equivalent source-column alias).

### Label source
`Product`, mapped into eight stable project categories: credit reporting, debt collection, mortgage, credit card, bank account, loan, payments/transfers and other financial services.

### Additional retained metadata
Where present: `Issue`, complaint ID, company, company response and timely-response field.

### Preparation
The project reads the large source CSV in chunks and uses reproducible reservoir sampling to retain up to a configurable number of records per mapped category. This limits memory use and prevents the earliest rows from automatically dominating the sample.

### Limitations
- US financial-services context; not representative of all industries or countries.
- Complaint narratives represent people who chose/managed to complain, so selection bias is expected.
- Historical product taxonomies change over time; category mapping simplifies this history.
- Public complaints can still carry privacy/re-identification risk when combined with other fields.
- Balancing categories improves training practicality but changes real-world class prevalence.

## Secondary dataset
**Customer Support on Twitter**, Kaggle dataset `thoughtvector/customer-support-on-twitter`.

### Purpose
Retrieve analogous customer-support exchanges as tone/structure examples for the optional drafting component.

### Pair construction
Inbound customer tweets are linked to the first direct outbound company response through tweet IDs and `in_response_to_tweet_id`.

### Critical restriction
Twitter replies are **not policy evidence**. They span multiple organisations, products and historical periods. The RAG policy knowledge base remains the only authorised source for policy-specific statements.

## Redistribution
Raw Kaggle data is not bundled in this project archive. Users download it from the original source and process it locally. Raw/processed CSV files are ignored by Git by default.
