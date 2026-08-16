from __future__ import annotations

from pathlib import Path
import random
import re
from typing import Iterable

import pandas as pd


CFPB_TEXT_ALIASES = [
    "Consumer complaint narrative",
    "consumer_complaint_narrative",
    "complaint_what_happened",
    "narrative",
]
CFPB_PRODUCT_ALIASES = ["Product", "product"]
CFPB_ISSUE_ALIASES = ["Issue", "issue"]
CFPB_ID_ALIASES = ["Complaint ID", "complaint_id", "Complaint ID "]
CFPB_COMPANY_ALIASES = ["Company", "company"]
CFPB_RESPONSE_ALIASES = ["Company response to consumer", "company_response_to_consumer"]
CFPB_TIMELY_ALIASES = ["Timely response?", "timely_response"]

TWITTER_REQUIRED = {
    "tweet_id",
    "author_id",
    "inbound",
    "created_at",
    "text",
    "response_tweet_id",
    "in_response_to_tweet_id",
}


def _resolve(columns: Iterable[str], aliases: list[str], required: bool = True) -> str | None:
    lookup = {str(c).strip().casefold(): c for c in columns}
    for alias in aliases:
        hit = lookup.get(alias.strip().casefold())
        if hit is not None:
            return str(hit)
    if required:
        raise ValueError(
            f"Could not find a required column. Tried {aliases}. Available columns: {list(columns)}"
        )
    return None


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).replace("\\n", " ").replace("\n", " ")
    text = re.sub(r"https?://\S+|www\.\S+", " URL ", text)
    text = re.sub(r"@[A-Za-z0-9_]+", " USER ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def map_cfpb_product(product: object) -> str:
    p = str(product or "").strip().lower()
    if "credit reporting" in p or "consumer report" in p or "credit repair" in p:
        return "credit_reporting"
    if "debt collection" in p:
        return "debt_collection"
    if "mortgage" in p:
        return "mortgage"
    if "credit card" in p:
        return "credit_card"
    if "checking" in p or "savings" in p or "bank account" in p:
        return "bank_account"
    if any(term in p for term in [
        "student loan", "consumer loan", "vehicle loan", "payday loan", "title loan", "personal loan"
    ]):
        return "loan"
    if any(term in p for term in [
        "money transfer", "virtual currency", "money service", "prepaid card"
    ]):
        return "payments_transfers"
    return "other_financial_service"


def prepare_cfpb_dataset(
    source: Path,
    output: Path,
    max_per_class: int = 5000,
    min_chars: int = 40,
    chunksize: int = 50000,
    random_state: int = 42,
) -> dict:
    """Stream a large CFPB CSV and create a balanced, reproducible training sample.

    Reservoir sampling prevents the first rows/years of a multi-million-row file from
    dominating the training sample while keeping memory use modest.
    """
    source = Path(source)
    output = Path(output)
    header = pd.read_csv(source, nrows=0)
    columns = list(header.columns)
    text_col = _resolve(columns, CFPB_TEXT_ALIASES)
    product_col = _resolve(columns, CFPB_PRODUCT_ALIASES)
    issue_col = _resolve(columns, CFPB_ISSUE_ALIASES, required=False)
    id_col = _resolve(columns, CFPB_ID_ALIASES, required=False)
    company_col = _resolve(columns, CFPB_COMPANY_ALIASES, required=False)
    response_col = _resolve(columns, CFPB_RESPONSE_ALIASES, required=False)
    timely_col = _resolve(columns, CFPB_TIMELY_ALIASES, required=False)

    usecols = [c for c in [text_col, product_col, issue_col, id_col, company_col, response_col, timely_col] if c]
    rng = random.Random(random_state)
    reservoirs: dict[str, list[dict]] = {}
    seen: dict[str, int] = {}
    accepted = 0

    for chunk in pd.read_csv(source, usecols=usecols, chunksize=chunksize, low_memory=False):
        for row in chunk.to_dict("records"):
            message = clean_text(row.get(text_col))
            if len(message) < min_chars:
                continue
            raw_product = str(row.get(product_col, "")).strip()
            if not raw_product:
                continue
            category = map_cfpb_product(raw_product)
            record = {
                "message": message,
                "category": category,
                "raw_product": raw_product,
                "issue": str(row.get(issue_col, "") or "").strip() if issue_col else "",
                "complaint_id": str(row.get(id_col, "") or "").strip() if id_col else "",
                "company": str(row.get(company_col, "") or "").strip() if company_col else "",
                "company_response": str(row.get(response_col, "") or "").strip() if response_col else "",
                "timely_response": str(row.get(timely_col, "") or "").strip() if timely_col else "",
            }
            accepted += 1
            n = seen.get(category, 0) + 1
            seen[category] = n
            bucket = reservoirs.setdefault(category, [])
            if len(bucket) < max_per_class:
                bucket.append(record)
            else:
                j = rng.randint(1, n)
                if j <= max_per_class:
                    bucket[j - 1] = record

    records = [record for bucket in reservoirs.values() for record in bucket]
    if not records:
        raise ValueError("No usable CFPB narratives were found in the supplied CSV.")
    df = pd.DataFrame(records).sample(frac=1, random_state=random_state).reset_index(drop=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)
    return {
        "source": str(source),
        "output": str(output),
        "usable_rows_seen": int(accepted),
        "processed_rows": int(len(df)),
        "category_counts": {str(k): int(v) for k, v in df["category"].value_counts().sort_index().items()},
        "target": "category",
        "text": "message",
    }


def _parse_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def _id(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0") and text[:-2].isdigit():
        return text[:-2]
    return text


def prepare_twitter_pairs(
    source: Path,
    output: Path,
    max_pairs: int = 50000,
    min_chars: int = 12,
    chunksize: int = 100000,
    random_state: int = 42,
) -> dict:
    """Create direct customer-message -> company-reply pairs from the Twitter corpus.

    The source contains millions of rows, so this uses two streaming passes rather than
    loading the complete file into memory. Pass 1 reservoir-samples candidate outbound
    replies. Pass 2 reads only the inbound customer tweets referenced by those replies.
    """
    source = Path(source)
    output = Path(output)
    header = pd.read_csv(source, nrows=0)
    columns = {str(c).strip() for c in header.columns}
    missing = TWITTER_REQUIRED - columns
    if missing:
        raise ValueError(f"Twitter dataset is missing columns: {sorted(missing)}")

    rng = random.Random(random_state)
    candidate_limit = max(max_pairs * 3, max_pairs)
    candidate_replies: list[dict] = []
    replies_seen = 0
    usecols_reply = [
        "tweet_id", "author_id", "inbound", "created_at", "text", "in_response_to_tweet_id"
    ]

    # Pass 1: sample direct outbound replies without retaining the full corpus.
    for chunk in pd.read_csv(source, usecols=usecols_reply, chunksize=chunksize, low_memory=False):
        for row in chunk.to_dict("records"):
            if _parse_bool(row.get("inbound")):
                continue
            parent_id = _id(row.get("in_response_to_tweet_id"))
            response = clean_text(row.get("text"))
            if not parent_id or len(response) < min_chars:
                continue
            record = {
                "in_response_to_tweet_id": parent_id,
                "agent_tweet_id": _id(row.get("tweet_id")),
                "agent_author_id": str(row.get("author_id", "") or ""),
                "agent_created_at": str(row.get("created_at", "") or ""),
                "agent_response": response,
            }
            replies_seen += 1
            if len(candidate_replies) < candidate_limit:
                candidate_replies.append(record)
            else:
                j = rng.randint(1, replies_seen)
                if j <= candidate_limit:
                    candidate_replies[j - 1] = record

    target_ids = {r["in_response_to_tweet_id"] for r in candidate_replies}
    customers: dict[str, dict] = {}
    usecols_customer = ["tweet_id", "author_id", "inbound", "created_at", "text"]

    # Pass 2: collect only customer tweets referenced by the sampled replies.
    for chunk in pd.read_csv(source, usecols=usecols_customer, chunksize=chunksize, low_memory=False):
        for row in chunk.to_dict("records"):
            if not _parse_bool(row.get("inbound")):
                continue
            tweet_id = _id(row.get("tweet_id"))
            if tweet_id not in target_ids:
                continue
            message = clean_text(row.get("text"))
            if len(message) < min_chars:
                continue
            customers[tweet_id] = {
                "customer_author_id": str(row.get("author_id", "") or ""),
                "customer_created_at": str(row.get("created_at", "") or ""),
                "customer_message": message,
            }

    records = []
    for reply in candidate_replies:
        customer = customers.get(reply["in_response_to_tweet_id"])
        if customer:
            records.append({**reply, **customer})

    if not records:
        raise ValueError("No direct customer-to-support reply pairs could be reconstructed.")
    pairs = pd.DataFrame(records)
    pairs = pairs.sort_values("agent_created_at").drop_duplicates("in_response_to_tweet_id", keep="first")
    if len(pairs) > max_pairs:
        pairs = pairs.sample(n=max_pairs, random_state=random_state)
    pairs = pairs[[
        "in_response_to_tweet_id", "customer_author_id", "customer_created_at", "customer_message",
        "agent_tweet_id", "agent_author_id", "agent_created_at", "agent_response"
    ]].reset_index(drop=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    pairs.to_csv(output, index=False)
    return {
        "source": str(source),
        "output": str(output),
        "outbound_replies_seen": int(replies_seen),
        "sampled_candidate_replies": int(len(candidate_replies)),
        "processed_pairs": int(len(pairs)),
        "purpose": "conversation-style examples only; not a policy knowledge source",
        "method": "two-pass streamed reservoir sampling",
    }


def find_csv_with_columns(folder: Path, required_any: set[str]) -> Path | None:
    for path in sorted(Path(folder).rglob("*.csv")):
        try:
            cols = {str(c).strip() for c in pd.read_csv(path, nrows=0).columns}
        except Exception:
            continue
        if required_any.issubset(cols):
            return path
    return None
