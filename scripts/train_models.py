from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.ai.training import train_classifier

metrics = train_classifier(ROOT / "data" / "processed" / "cfpb_complaints.csv", ROOT / "artifacts")
print(metrics)
