URGENT_TERMS = {
    "urgent", "immediately", "asap", "fraud", "stolen", "identity theft", "security",
    "legal", "locked out", "cannot access", "unauthorised", "unauthorized", "scam",
    "foreclosure", "eviction", "repossession", "harassment", "threat", "double charged",
    "duplicate charge", "missing money"
}

CATEGORY_WEIGHT = {
    "credit_reporting": 12,
    "debt_collection": 16,
    "mortgage": 16,
    "credit_card": 14,
    "bank_account": 14,
    "loan": 12,
    "payments_transfers": 18,
    "other_financial_service": 8,
}


def score_priority(text: str, category: str, sentiment: dict) -> dict:
    lower = text.lower()
    score = 10 + CATEGORY_WEIGHT.get(category, 8)
    reasons = [f"category weight: {category}"]

    if sentiment["label"] == "negative":
        score += 22
        reasons.append("negative sentiment")
    if sentiment.get("score", 0) <= -0.6:
        score += 14
        reasons.append("strong negative sentiment")

    matched = [term for term in URGENT_TERMS if term in lower]
    if matched:
        score += min(34, 12 + 5 * len(matched))
        reasons.append("urgency/financial-risk terms: " + ", ".join(sorted(matched)[:4]))

    if len(text) > 1000:
        score += 4
        reasons.append("long detailed complaint")

    score = max(0, min(100, int(score)))
    if score >= 82:
        label = "critical"
    elif score >= 62:
        label = "high"
    elif score >= 36:
        label = "medium"
    else:
        label = "low"

    return {"label": label, "score": score, "reasons": reasons}
