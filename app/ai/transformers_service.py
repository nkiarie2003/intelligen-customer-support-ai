class TransformerHub:
    def __init__(self, config):
        self.config = config
        self._zero_shot = None
        self._sentiment = None
        self._generator = None

    def _pipeline(self, task, model):
        try:
            from transformers import pipeline
        except ImportError as exc:
            raise RuntimeError(
                "Transformers are not installed. Install requirements-advanced.txt."
            ) from exc
        return pipeline(task, model=model)

    def zero_shot(self, text: str, labels: list[str]) -> dict:
        if self._zero_shot is None:
            self._zero_shot = self._pipeline(
                "zero-shot-classification", self.config["ZERO_SHOT_MODEL"]
            )
        result = self._zero_shot(text, candidate_labels=labels, multi_label=False)
        return {
            "label": result["labels"][0],
            "confidence": round(float(result["scores"][0]), 4),
            "top_predictions": [
                {"label": l, "score": round(float(s), 4)}
                for l, s in zip(result["labels"][:3], result["scores"][:3])
            ],
            "backend": f"transformer_zero_shot:{self.config['ZERO_SHOT_MODEL']}",
        }

    def sentiment(self, text: str) -> dict:
        if self._sentiment is None:
            self._sentiment = self._pipeline(
                "sentiment-analysis", self.config["SENTIMENT_MODEL"]
            )
        result = self._sentiment(text[:2000])[0]
        label = str(result["label"]).lower()
        if "neg" in label:
            mapped = "negative"
            signed = -float(result["score"])
        elif "pos" in label:
            mapped = "positive"
            signed = float(result["score"])
        else:
            mapped = "neutral"
            signed = 0.0
        return {
            "label": mapped,
            "score": round(signed, 4),
            "confidence": round(float(result["score"]), 4),
            "backend": f"transformer_sentiment:{self.config['SENTIMENT_MODEL']}",
        }

    def generate(self, prompt: str) -> str:
        if self._generator is None:
            self._generator = self._pipeline(
                "text2text-generation", self.config["GENERATOR_MODEL"]
            )
        output = self._generator(
            prompt,
            max_new_tokens=180,
            do_sample=False,
            truncation=True,
        )[0]["generated_text"]
        return output.strip()
