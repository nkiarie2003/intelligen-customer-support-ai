from flask import current_app

from .classifier import ComplaintClassifier
from .conversation_examples import ConversationExampleRetriever
from .generator import ResponseGenerator
from .intent_classifier import IntentClassifier
from .priority import score_priority
from .rag import PolicyRetriever
from .sentiment import SentimentAnalyzer
from .text import normalise_text
from .transformers_service import TransformerHub


class AIEngine:
    """Hybrid AI engine for the SHU-compatible architecture.

    Training may occur on an Azure ML compute instance, while live Flask
    inference remains local.
    """

    def __init__(self, app):
        cfg = app.config

        self.classifier = ComplaintClassifier(
            cfg["ARTIFACT_DIR"],
            cfg["TRAINING_DATA"],
        )
        self.intent_classifier = IntentClassifier(
            cfg["ARTIFACT_DIR"],
            cfg["INTENT_TRAINING_DATA"],
        )
        self.sentiment = SentimentAnalyzer()
        self.transformers = TransformerHub(cfg)
        self.retriever = PolicyRetriever(
            cfg["POLICY_FILE"],
            cfg["ENABLE_EMBEDDINGS"],
            cfg["EMBEDDING_MODEL"],
        )
        self.generator = ResponseGenerator(
            self.transformers,
            cfg["ENABLE_LOCAL_GENERATOR"],
        )
        self.conversation_examples = ConversationExampleRetriever(
            cfg["CONVERSATION_DATA"]
        )
        self.cfg = cfg

    def analyze(
        self,
        subject: str,
        message: str,
        knowledge_documents=None,
    ) -> dict:
        text = normalise_text(f"{subject}. {message}")

        # Broad CFPB product/category classification.
        supervised = self.classifier.predict(text)
        category = supervised
        category_notes = ["live inference served locally by Flask"]

        if self.cfg["ENABLE_ZERO_SHOT"]:
            try:
                zero_shot = self.transformers.zero_shot(
                    text,
                    self.classifier.classes,
                )

                scores = {
                    prediction["label"]: 0.70 * prediction["score"]
                    for prediction in supervised["top_predictions"]
                }

                for prediction in zero_shot["top_predictions"]:
                    label = prediction["label"]
                    scores[label] = (
                        scores.get(label, 0)
                        + 0.30 * prediction["score"]
                    )

                ranked = sorted(
                    scores.items(),
                    key=lambda item: item[1],
                    reverse=True,
                )

                category = {
                    "label": ranked[0][0],
                    "confidence": round(float(ranked[0][1]), 4),
                    "top_predictions": [
                        {
                            "label": label,
                            "score": round(float(score), 4),
                        }
                        for label, score in ranked[:3]
                    ],
                    "backend": (
                        "ensemble:"
                        "70%_supervised+30%_zero_shot_transformer"
                    ),
                }
                category_notes.append(
                    "zero-shot transformer ensemble enabled"
                )
            except Exception as exc:
                category_notes.append(
                    f"zero-shot transformer unavailable: {exc}"
                )

        # Fine-grained Bitext customer-support intent classification.
        try:
            intent = self.intent_classifier.predict(text)
            confidence = float(intent.get("confidence", 0))

            if confidence >= 0.75:
                confidence_band = "high"
            elif confidence >= 0.50:
                confidence_band = "medium"
            else:
                confidence_band = "low"

            intent["confidence_band"] = confidence_band
            intent["needs_review"] = confidence < 0.50
        except Exception as exc:
            intent = {
                "label": "unavailable",
                "confidence": 0.0,
                "top_predictions": [],
                "confidence_band": "low",
                "needs_review": True,
                "backend": "unavailable",
                "warning": str(exc),
            }

        sentiment = self.sentiment.analyze(text)

        if self.cfg["ENABLE_TRANSFORMER_SENTIMENT"]:
            try:
                deep_sentiment = self.transformers.sentiment(text)

                if deep_sentiment.get("confidence", 0) >= 0.70:
                    deep_sentiment["baseline"] = sentiment
                    sentiment = deep_sentiment
            except Exception as exc:
                sentiment["transformer_warning"] = str(exc)

        priority = score_priority(
            text,
            category["label"],
            sentiment,
        )

        explanation = self.classifier.explain(
            text,
            supervised["label"],
        )
        explanation["classification_notes"] = category_notes
        explanation["supervised_prediction"] = supervised
        explanation["intent_prediction"] = intent
        explanation["sentiment_cues"] = sentiment.get("cues", [])
        explanation["priority_reasons"] = priority["reasons"]

        retrieval = self.retriever.retrieve(
            text,
            extra_documents=knowledge_documents or [],
            top_k=3,
        )

        partial = {
            "category": category,
            "intent": intent,
            "sentiment": sentiment,
            "priority": priority,
        }

        if self.cfg["ENABLE_CONVERSATION_EXAMPLES"]:
            conversation_examples = self.conversation_examples.retrieve(
                text,
                top_k=2,
            )
        else:
            conversation_examples = {
                "backend": "disabled",
                "results": [],
                "policy_authority": False,
            }

        generated = self.generator.generate(
            subject,
            message,
            partial,
            retrieval,
            conversation_examples=conversation_examples,
        )

        return {
            "category": category,
            "intent": intent,
            "sentiment": sentiment,
            "priority": priority,
            "explanation": explanation,
            "retrieval": retrieval,
            "suggested_reply": generated,
            "conversation_examples": conversation_examples,
            "backends": {
                "classification": category.get("backend"),
                "intent": intent.get("backend"),
                "sentiment": sentiment.get("backend"),
                "retrieval": retrieval.get("backend"),
                "generation": generated.get("backend"),
                "conversation_examples": conversation_examples.get(
                    "backend"
                ),
                "inference_mode": "local_flask",
            },
            "human_approval_required": True,
        }


def get_ai_engine():
    return current_app.extensions["ai_engine"]

