from pathlib import Path
from airflow.models import DagBag

root = Path(__file__).resolve().parents[1]
bag = DagBag(dag_folder=str(root / "orchestration"), include_examples=False)
assert not bag.import_errors, bag.import_errors
dag = bag.dags["trayectorias_ar"]
assert len(dag.tasks) == 3
assert dag.catchup is False and dag.max_active_runs == 1
assert dag.get_task("build_release").upstream_task_ids == {"preflight"}
assert dag.get_task("verify_release").upstream_task_ids == {"build_release"}
print(
    "PASS: DAG válido; preflight → build_release → verify_release; sin errores de importación"
)
