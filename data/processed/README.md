# Processed real datasets

The real Kaggle datasets are intentionally **not bundled** in this project archive because of their size and redistribution considerations.

After downloading the source datasets, run:

```bash
python scripts/prepare_datasets.py
```

Expected outputs:

- `cfpb_complaints.csv` — supervised complaint-classification data derived from the CFPB complaint corpus.
- `twitter_support_pairs.csv` — customer → support-agent conversation pairs derived from Customer Support on Twitter.

The CFPB data is the model-training source. Twitter replies are used only as non-authoritative style/examples for response drafting.
