from dataclasses import dataclass
from pathlib import Path
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .text import safe_excerpt


@dataclass
class Chunk:
    source: str
    text: str


def chunk_markdown(source: str, content: str, max_chars: int = 900) -> list[Chunk]:
    # Preserve Markdown heading sections so retrieval evidence remains policy-specific.
    sections = re.split(r"(?m)(?=^#{1,3}\s+)", content)
    chunks: list[Chunk] = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        heading_match = re.match(r"^#{1,3}\s+(.+)$", section.splitlines()[0])
        heading = heading_match.group(1).strip() if heading_match else source
        if len(section) <= max_chars:
            chunks.append(Chunk(source=heading, text=section))
            continue
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", section) if p.strip()]
        buffer = ""
        for paragraph in paragraphs:
            if len(buffer) + len(paragraph) + 2 <= max_chars:
                buffer = f"{buffer}\n\n{paragraph}".strip()
            else:
                if buffer:
                    chunks.append(Chunk(source=heading, text=buffer))
                buffer = paragraph
        if buffer:
            chunks.append(Chunk(source=heading, text=buffer))
    return chunks


class PolicyRetriever:
    def __init__(self, policy_file: Path, enable_embeddings: bool, embedding_model: str):
        self.policy_file = Path(policy_file)
        self.enable_embeddings = enable_embeddings
        self.embedding_model = embedding_model
        self._embedder = None

    def _base_chunks(self):
        if not self.policy_file.exists():
            return []
        content = self.policy_file.read_text(encoding="utf-8")
        return chunk_markdown(self.policy_file.stem, content)

    def retrieve(self, query: str, extra_documents=None, top_k: int = 3) -> dict:
        chunks = self._base_chunks()
        for doc in extra_documents or []:
            chunks.extend(chunk_markdown(doc["title"], doc["content"]))

        if not chunks:
            return {"backend": "none", "results": []}

        texts = [c.text for c in chunks]
        if self.enable_embeddings:
            try:
                if self._embedder is None:
                    from sentence_transformers import SentenceTransformer
                    self._embedder = SentenceTransformer(self.embedding_model)
                corpus = self._embedder.encode(texts, normalize_embeddings=True)
                q = self._embedder.encode([query], normalize_embeddings=True)[0]
                scores = corpus @ q
                backend = f"sentence_transformers:{self.embedding_model}"
            except Exception:
                scores, backend = self._tfidf_scores(query, texts)
        else:
            scores, backend = self._tfidf_scores(query, texts)

        order = np.argsort(scores)[::-1][:top_k]
        results = [
            {
                "source": chunks[i].source,
                "score": round(float(scores[i]), 4),
                "text": safe_excerpt(chunks[i].text, 650),
            }
            for i in order
            if float(scores[i]) > 0
        ]
        return {"backend": backend, "results": results}

    @staticmethod
    def _tfidf_scores(query: str, texts: list[str]):
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        matrix = vectorizer.fit_transform(texts + [query])
        scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
        return scores, "tfidf_cosine_retrieval"
