"""Airflow 3: publicar mensualmente una versión completa, sin backfill implícito."""

from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import subprocess
from airflow.sdk import dag, task


@dag(
    dag_id="trayectorias_ar",
    schedule="0 9 1 * *",
    start_date=datetime(2026, 9, 1, tzinfo=timezone.utc),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=3)},
    tags=["portfolio", "educacion", "argentina"],
)
def trayectorias_ar():
    @task
    def preflight():
        root = Path(os.environ.get("TRAYECTORIAS_ROOT", "/opt/trayectorias"))
        if not (root / "config/sources.json").exists():
            raise FileNotFoundError(root)
        if not (root / ".venv/bin/trayectorias").exists():
            raise RuntimeError("Falta entorno del pipeline")
        return str(root)

    @task(execution_timeout=timedelta(minutes=20))
    def build_release(root: str):
        args = [str(Path(root) / ".venv/bin/trayectorias"), "run", "--root", root]
        if os.environ.get("TRAYECTORIAS_OFFLINE", "false").lower() == "true":
            args.append("--offline")
        subprocess.run(args, cwd=root, check=True)
        return str((Path(root) / "reports/current").resolve())

    @task
    def verify_release(release: str):
        import json

        folder = Path(release)
        status = json.loads((folder / "run.json").read_text())
        if status["status"] != "success":
            raise RuntimeError("Versión no validada")
        if not (folder / "dashboard.html").is_file():
            raise RuntimeError("Falta reporte")
        return {
            "run_id": status["run_id"],
            "observations": status["total_observations"],
            "context_observations": status["context_observations"],
        }

    verify_release(build_release(preflight()))


trayectorias_ar()
