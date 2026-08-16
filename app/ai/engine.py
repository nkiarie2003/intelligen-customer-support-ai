from flask import current_app

from .classifier import ComplaintClassifier
from .conversation_examples import ConversationExampleRetriever
from .generator import ResponseGenerator
from .priority import score_priority
from .rag import PolicyRetriever
from .sentiment import SentimentAnalyzer
from .text import normalise_text
from .transformers_service import TransformerHub


class AIEngine:
    """Hybrid AI engine for the SHU-compatible architecture.

    Training may occur on an Azure ML compute instance, but live Flask inference is local.
    This avoids dependence on Azure online-endpoint resources that may be blocked by lab policy.
    """

    def __init__(self, app):
        cfg = app.config
        self.classifier = ComplaintClassifier(cfg["ARTIFACT_DIR"], cfg["TRAINING_DATA"])
        self.sentiment = SentimentAnalyzer()
        self.transformers = TransformerHub(cfg)
        self.retriever = PolicyRetriever(
            cfg["POLICY_FILE"], cfg["ENABLE_EMBEDDINGS"], cfg["EMBEDDING_MODEL"]
        )
        self.generator = ResponseGenerator(self.transformers, cfg["ENABLE_LOCAL_GENERATOR"])
        self.conversation_examples = ConversationExampleRetriever(cfg["CONVERSATION_DATA"])
        self.cfg = cfg

    def analyze(self, subject: str, message: str, knowledge_documents=None) -> dict:
        text = normalise_text(f"{subject}. {message}")
        supervised = self.classifier.predict(text)
        category = supervised
        category_notes = ["live inference served locally by Flask"]

        if self.cfg["ENABLE_ZERO_SHOT"]:
            try:
                zs = self.transformers.zero_shot(text, self.classifier.classes)
                # Auditable baseline remains dominant; transformer is an advanced enhancement.
                scores = {p["label"]: 0.70 * p["score"] for p in supervised["top_predictions"]}
                for p in zs["top_predictions"]:
                    scores[p["label"]] = scores.get(p["label"], 0) + 0.30 * p["score"]
                ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                category = {
                    "label": ranked[0][0],
                    "confidence": round(float(ranked[0][1]), 4),
                    "top_predictions": [
                        {"label": label, "score": round(float(score), 4)}
                        for label, score in ranked[:3]
                    ],
                    "backend": "ensemble:70%_supervised+30%_zero_shot_transformer",
                }
                category_notes.append("zero-shot transformer ensemble enabled")
            except Exception as exc:
                category_notes.append(f"zero-shot transformer unavailable: {exc}")

        sentiment = self.sentiment.analyze(text)
        if self.cfg["ENABLE_TRANSFORMER_SENTIMENT"]:
            try:
                deep_sentiment = self.transformers.sentiment(text)
                if deep_sentiment.get("confidence", 0) >= 0.70:
                    deep_sentiment["baseline"] = sentiment
                    sentiment = deep_sentiment
            except Exception as exc:
                sentiment["transformer_warning"] = str(exc)

        priority = score_priority(text, category["label"], sentiment)
        explanation = self.classifier.explain(text, supervised["label"])
        explanation["classification_notes"] = category_notes
        explanation["supervised_prediction"] = supervised
        explanation["sentiment_cues"] = sentiment.get("cues", [])
        explanation["priority_reasons"] = priority["reasons"]

        retrieval = self.retriever.retrieve(text, extra_documents=knowledge_documents or [], top_k=3)
        partial = {"category": category, "sentiment": sentiment, "priority": priority}
        conversation_examples = (
            self.conversation_examples.retrieve(text, top_k=2)
            if self.cfg["ENABLE_CONVERSATION_EXAMPLES"]
            else {"backend": "disabled", "results": [], "policy_authority": False}
        )
        generated = self.generator.generate(
            subject, message, partial, retrieval, conversation_examples=conversation_examples
        )

        return {
            "category": category,
            "sentiment": sentiment,
            "priority": priority,
            "explanation": explanation,
            "retrieval": retrieval,
            "suggested_reply": generated,
            "conversation_examples": conversation_examples,
            "backends": {
                "classification": category.get("backend"),
                "sentiment": sentiment.get("backend"),
                "retrieval": retrieval.get("backend"),
                "generation": generated.get("backend"),
                "conversation_examples": conversation_examples.get("backend"),
                "inference_mode": "local_flask",
            },
            "human_approval_required": True,
        }


def get_ai_engine():
    return current_app.extensions["ai_engine"]
