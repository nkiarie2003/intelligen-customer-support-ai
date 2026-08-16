import os
import platform
from pathlib import Path

print("Cloud training environment check")
print("=" * 34)
print("Hostname:", platform.node())
print("OS:", platform.platform())
print("Python:", platform.python_version())
print("Workspace:", os.getenv("AZURE_ML_WORKSPACE", "mlworkspace-traning"))
print("Compute:", os.getenv("AZURE_ML_COMPUTE", "c50411741-ML"))
path = Path("data/processed/cfpb_complaints.csv")
print("Processed CFPB dataset:", "FOUND" if path.exists() else "MISSING", path)
