import requests


class AzureMLClassifierClient:
    def __init__(self, scoring_uri: str, api_key: str):
        self.scoring_uri = scoring_uri
        self.api_key = api_key

    @property
    def configured(self) -> bool:
        return bool(self.scoring_uri and self.api_key)

    def predict(self, text: str) -> dict:
        if not self.configured:
            raise RuntimeError("Azure ML endpoint is not configured.")
        response = requests.post(
            self.scoring_uri,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={"text": text},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        if isinstance(data, str):
            import json
            data = json.loads(data)
        data["backend"] = data.get("backend", "azure_ml_online_endpoint")
        return data
