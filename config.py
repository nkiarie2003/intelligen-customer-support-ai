import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _bool(name: str, default: bool = False) -> bool:
    """Read a Boolean environment variable."""
    return os.getenv(name, str(default)).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _path(name: str, default: Path) -> Path:
    """Read and resolve a filesystem path from an environment variable."""
    value = os.getenv(name)
    path = Path(value) if value else Path(default)
    return path if path.is_absolute() else BASE_DIR / path


class Config:
    # Flask and database
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-this-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///customer_intelligence.db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _bool("SESSION_COOKIE_SECURE", False)

    # Data and model paths
    ARTIFACT_DIR = _path(
        "ARTIFACT_DIR",
        BASE_DIR / "artifacts",
    )
    TRAINING_DATA = _path(
        "TRAINING_DATA",
        BASE_DIR / "data" / "processed" / "cfpb_complaints.csv",
    )
    INTENT_TRAINING_DATA = _path(
        "INTENT_TRAINING_DATA",
        BASE_DIR / "data" / "raw" / "bitext" / "bitext.csv",
    )
    CONVERSATION_DATA = _path(
        "CONVERSATION_DATA",
        BASE_DIR / "data" / "processed" / "twitter_support_pairs.csv",
    )
    POLICY_FILE = _path(
        "POLICY_FILE",
        BASE_DIR / "data" / "policies" / "company_policies.md",
    )

    # Optional advanced AI features
    ENABLE_ZERO_SHOT = _bool("ENABLE_ZERO_SHOT", False)
    ENABLE_TRANSFORMER_SENTIMENT = _bool(
        "ENABLE_TRANSFORMER_SENTIMENT",
        False,
    )
    ENABLE_EMBEDDINGS = _bool("ENABLE_EMBEDDINGS", False)
    ENABLE_LOCAL_GENERATOR = _bool("ENABLE_LOCAL_GENERATOR", False)
    ENABLE_CONVERSATION_EXAMPLES = _bool(
        "ENABLE_CONVERSATION_EXAMPLES",
        True,
    )

    # Transformer models
    ZERO_SHOT_MODEL = os.getenv(
        "ZERO_SHOT_MODEL",
        "facebook/bart-large-mnli",
    )
    SENTIMENT_MODEL = os.getenv(
        "SENTIMENT_MODEL",
        "distilbert-base-uncased-finetuned-sst-2-english",
    )
    EMBEDDING_MODEL = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    )
    GENERATOR_MODEL = os.getenv(
        "GENERATOR_MODEL",
        "google/flan-t5-small",
    )

    # SHU-compatible cloud architecture:
    # training can run on Azure ML while Flask inference remains local.
    INFERENCE_MODE = os.getenv("INFERENCE_MODE", "local").strip().lower()
    TRAINING_PLATFORM = os.getenv("TRAINING_PLATFORM", "local")

    AZURE_ML_SUBSCRIPTION = os.getenv("AZURE_ML_SUBSCRIPTION", "")
    AZURE_ML_RESOURCE_GROUP = os.getenv("AZURE_ML_RESOURCE_GROUP", "")
    AZURE_ML_WORKSPACE = os.getenv("AZURE_ML_WORKSPACE", "")
    AZURE_ML_COMPUTE = os.getenv("AZURE_ML_COMPUTE", "")

    # Application settings
    API_DEMO_KEY = os.getenv(
        "API_DEMO_KEY",
        "dev-api-key-change-me",
    )
    DATA_RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", "90"))