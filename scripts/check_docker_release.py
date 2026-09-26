"""Compara una ejecución Docker con un run.json local guardado previamente."""

import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("baseline", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
before = json.loads(args.baseline.read_text())
after = json.loads((root / "reports/current/run.json").read_text())
assert after["status"] in ("success", "pass")
assert before["run_id"] != after["run_id"], "No se publicó una nueva ejecución"
for field in ["dataset_sha256", "sources_sha256", "total_observations"]:
    assert before[field] == after[field], field
assert all(r["status"] in ("success", "pass") for r in after["dbt_results"])
print(
    json.dumps(
        {
            "status": "PASS",
            "run_id": after["run_id"],
            "rows": after["total_observations"],
            "dataset_sha256": after["dataset_sha256"],
            "message": "Docker coincide con el dataset local",
        },
        ensure_ascii=False,
    )
)
