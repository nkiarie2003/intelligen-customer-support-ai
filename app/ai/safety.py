import re

_CARD_LIKE = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")
_PASSWORD = re.compile(r"(?i)\b(password|passcode|pin)\s*[:=]\s*\S+")
_OTP = re.compile(r"(?i)\b(one[- ]?time (?:passcode|password)|otp)\s*[:=]?\s*\d{4,8}\b")


def minimise_sensitive_text(text: str) -> tuple[str, list[str]]:
    """Redact obvious high-risk secrets before persistence or AI processing.

    This is deliberately conservative: it is a safety aid, not a complete DLP system.
    """
    warnings: list[str] = []
    cleaned = text

    if _CARD_LIKE.search(cleaned):
        cleaned = _CARD_LIKE.sub("[REDACTED_POSSIBLE_CARD_NUMBER]", cleaned)
        warnings.append("possible payment-card/account number redacted")
    if _PASSWORD.search(cleaned):
        cleaned = _PASSWORD.sub(lambda m: f"{m.group(1)}=[REDACTED_SECRET]", cleaned)
        warnings.append("password/PIN-like secret redacted")
    if _OTP.search(cleaned):
        cleaned = _OTP.sub("[REDACTED_ONE_TIME_CODE]", cleaned)
        warnings.append("one-time code redacted")

    return cleaned, warnings
