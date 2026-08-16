import re


class SentimentAnalyzer:
    POSITIVE = {
        "helpful", "great", "good", "excellent", "thanks", "thank", "happy",
        "resolved", "pleased", "quick", "appreciate", "satisfied"
    }
    NEGATIVE = {
        "bad", "broken", "angry", "terrible", "awful", "late", "damaged",
        "failed", "failure", "unhappy", "frustrated", "refund", "complaint",
        "unacceptable", "wrong", "problem", "issue", "cancel", "charged"
    }

    def __init__(self):
        self._vader = None
        try:
            from nltk.sentiment import SentimentIntensityAnalyzer
            try:
                self._vader = SentimentIntensityAnalyzer()
            except LookupError:
                self._vader = None
        except Exception:
            self._vader = None

    def analyze(self, text: str) -> dict:
        if self._vader is not None:
            score = float(self._vader.polarity_scores(text)["compound"])
            if score >= 0.05:
                label = "positive"
            elif score <= -0.05:
                label = "negative"
            else:
                label = "neutral"
            return {
                "label": label,
                "score": round(score, 4),
                "backend": "vader",
                "cues": self._cues(text),
            }

        words = re.findall(r"[a-z']+", text.lower())
        pos = sum(w in self.POSITIVE for w in words)
        neg = sum(w in self.NEGATIVE for w in words)
        raw = (pos - neg) / max(1, pos + neg)
        label = "positive" if raw > 0.15 else "negative" if raw < -0.15 else "neutral"
        return {
            "label": label,
            "score": round(float(raw), 4),
            "backend": "local_lexicon_fallback",
            "cues": self._cues(text),
        }

    def _cues(self, text: str):
        words = re.findall(r"[a-z']+", text.lower())
        seen = []
        for w in words:
            if w in self.POSITIVE or w in self.NEGATIVE:
                if w not in seen:
                    seen.append(w)
        return seen[:8]
