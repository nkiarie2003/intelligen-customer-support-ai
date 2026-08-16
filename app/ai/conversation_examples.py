from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .text import safe_excerpt


class ConversationExampleRetriever:
    """Retrieve analogous public customer-support conversations for drafting style.

    These examples are explicitly *not* policy evidence because the Twitter corpus spans
    multiple organisations with different policies and historical practices.
    """

    def __init__(self, data_path: Path, max_index_rows: int = 20000):
        self.data_path = Path(data_path)
        self.max_index_rows = max_index_rows
        self._df = None
        self._vectorizer = None
        self._matrix = None

    @property
    def available(self) -> bool:
        return self.data_path.exists()

    def _load(self):
        if self._df is not None:
            return
        if not self.available:
            self._df = pd.DataFrame(columns=["customer_message", "agent_response"])
            return
        df = pd.read_csv(self.data_path).dropna(subset=["customer_message", "agent_response"])
        if len(df) > self.max_index_rows:
            df = df.sample(self.max_index_rows, random_state=42)
        df = df.reset_index(drop=True)
        self._vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=2, max_features=30000)
        self._matrix = self._vectorizer.fit_transform(df["customer_message"].astype(str))
        self._df = df

    def retrieve(self, query: str, top_k: int = 2) -> dict:
        self._load()
        if self._df is None or self._df.empty or self._vectorizer is None:
            return {"backend": "none", "results": [], "policy_authority": False}
        q = self._vectorizer.transform([query])
        scores = cosine_similarity(q, self._matrix).ravel()
        order = np.argsort(scores)[::-1][:top_k]
        results = []
        for i in order:
            score = float(scores[i])
            if score <= 0:
                continue
            row = self._df.iloc[int(i)]
            results.append({
                "score": round(score, 4),
                "customer_message": safe_excerpt(str(row["customer_message"]), 280),
                "agent_response": safe_excerpt(str(row["agent_response"]), 320),
                "agent_author_id": str(row.get("agent_author_id", "")),
            })
        return {
            "backend": "twitter_support_tfidf_examples",
            "results": results,
            "policy_authority": False,
            "warning": "Examples are for tone/structure only and must not be treated as company policy.",
        }
