import json
from pathlib import Path


def load_training_provenance(artifact_dir: Path) -> dict:
    artifact_dir = Path(artifact_dir)
    path = artifact_dir / "training_provenance.json"
    if not path.exists():
        return {
            "available": False,
            "training_platform": "unknown",
            "message": "No training provenance file has been generated yet.",
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        data["available"] = True
        return data
    except Exception as exc:
        return {
            "available": False,
            "training_platform": "unknown",
            "message": f"Could not read training provenance: {exc}",
        }
