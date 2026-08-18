from pathlib import Path

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
    INTENT_TRAINING_DATA = None
    CONVERSATION_DATA = None
    POLICY_FILE = None

    ENABLE_ZERO_SHOT = False
    ENABLE_TRANSFORMER_SENTIMENT = False
    ENABLE_EMBEDDINGS = False
    ENABLE_LOCAL_GENERATOR = False
    ENABLE_CONVERSATION_EXAMPLES = False

    ZERO_SHOT_MODEL = "facebook/bart-large-mnli"
    SENTIMENT_MODEL = (
        "distilbert-base-uncased-finetuned-sst-2-english"
    )
    EMBEDDING_MODEL = (
        "sentence-transformers/all-MiniLM-L6-v2"
    )
    GENERATOR_MODEL = "google/flan-t5-small"

    INFERENCE_MODE = "local"
    TRAINING_PLATFORM = "test"
    DATA_RETENTION_DAYS = 90
    API_DEMO_KEY = "test-key"


def _create_category_fixture(tmp_path: Path) -> Path:
    examples = {
        "credit_card": [
            "There is an unauthorised charge on my credit card account",
            "My card was charged twice for one purchase",
        ],
        "debt_collection": [
            "A debt collector keeps calling me about a debt I dispute",
            "The collection company is contacting me repeatedly",
        ],
        "mortgage": [
            "My mortgage payment was applied incorrectly by the servicer",
            "I have a problem with my mortgage escrow account",
        ],
    }

    rows = []

    for label, texts in examples.items():
        for index in range(6):
            rows.append(
                {
                    "message": (
                        f"{texts[index % len(texts)]} example {index}"
                    ),
                    "category": label,
                }
            )

    path = tmp_path / "cfpb_test_fixture.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def _create_intent_fixture(tmp_path: Path) -> Path:
    examples = {
        "cancel_order": [
            "Please cancel my duplicate order before it ships",
            "I need help cancelling an order I placed by mistake",
        ],
        "track_refund": [
            "Where is the refund for my cancelled order",
            "I am still waiting for my refund to arrive",
        ],
    }

    rows = []

    for label, texts in examples.items():
        for index in range(8):
            rows.append(
                {
                    "instruction": (
                        f"{texts[index % len(texts)]} example {index}"
                    ),
                    "intent": label,
                }
            )

    path = tmp_path / "bitext_test_fixture.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


@pytest.fixture()
def app(tmp_path):
    root = Path(__file__).resolve().parents[1]

    TestConfig.ARTIFACT_DIR = tmp_path / "artifacts"
    TestConfig.TRAINING_DATA = _create_category_fixture(tmp_path)
    TestConfig.INTENT_TRAINING_DATA = _create_intent_fixture(
        tmp_path
    )
    TestConfig.CONVERSATION_DATA = (
        tmp_path / "twitter_pairs.csv"
    )
    TestConfig.POLICY_FILE = (
        root / "data" / "policies" / "company_policies.md"
    )

    application = create_app(TestConfig)

    with application.app_context():
        db.create_all()

    yield application


@pytest.fixture()
def client(app):
    return app.test_client()