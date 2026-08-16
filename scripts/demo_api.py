import os
import requests

url = os.getenv("API_URL", "http://127.0.0.1:5000/api/v1/analyze")
key = os.getenv("API_DEMO_KEY", "dev-api-key-change-me")
payload = {
    "subject": "Duplicate charge and no response",
    "message": "I was charged twice for my subscription and support has not replied. Please fix this urgently."
}
r = requests.post(url, json=payload, headers={"X-API-Key": key}, timeout=60)
print(r.status_code)
print(r.json())
