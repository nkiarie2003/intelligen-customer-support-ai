import pandas as pd
import pytest

from app import create_app
from app.extensions import db


class TestConfig:
    TESTING = True
    SECRET_KEY = "test"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    ARTIFACT_DIR = None
    TRAINING_DATA = None
    CONVERSATION_DATA = None
    POLICY_FILE = None
    ENABLE_ZERO_SHOT = False
    ENABLE_TRANSFORMER_SENTIMENT = False
    ENABLE_EMBEDDINGS = False
    ENABLE_LOCAL_GENERATOR = False
    ENABLE_CONVERSATION_EXAMPLES = False
    ZERO_SHOT_MODEL = "facebook/bart-large-mnli"
    SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    GENERATOR_MODEL = "google/flan-t5-small"
    INFERENCE_MODE = "local"
    TRAINING_PLATFORM = "test"
    DATA_RETENTION_DAYS = 90
    API_DEMO_KEY = "test-key"


@pytest.fixture()
def app(tmp_path):
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    rows = []
    examples = {
        "credit_card": ["There is an unauthorised charge on my credit card account", "My card was charged twice for one purchase"],
        "debt_collection": ["A debt collector keeps calling me about a debt I dispute", "The collection company is contacting me repeatedly"],
        "mortgage": ["My mortgage payment was applied incorrectly by the servicer", "I have a problem with my mortgage escrow account"],
    }
    for label, texts in examples.items():
        for i in range(6):
            rows.append({"message": f"{texts[i % len(texts)]} example {i}", "category": label})
    training = tmp_path / "cfpb_test_fixture.csv"
    pd.DataFrame(rows).to_csv(training, index=False)

    TestConfig.ARTIFACT_DIR = tmp_path / "artifacts"
    TestConfig.TRAINING_DATA = training
    TestConfig.CONVERSATION_DATA = tmp_path / "twitter_pairs.csv"
    TestConfig.POLICY_FILE = root / "data" / "policies" / "company_policies.md"
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
