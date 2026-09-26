import json
from pathlib import Path
from trayectorias.pipeline import run

root = Path(__file__).resolve().parents[1]
before = json.loads((root / "reports/current/run.json").read_text())
release = run(root, offline=True)
after = json.loads((release / "run.json").read_text())
assert before["dataset_sha256"] == after["dataset_sha256"]
assert before["total_observations"] == after["total_observations"]
assert before["sources_sha256"] == after["sources_sha256"]
print("PASS: mismos snapshots → mismo hash de dataset y cantidad de observaciones")
