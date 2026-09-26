"""Carga, dbt, comparación contra DuckDB y publicación web de resultados Snowflake.
La configuración de autenticación vive fuera del repositorio. No imprime secretos.
"""

import argparse, csv, fcntl, json, math, os, shutil, subprocess, sys, tempfile, uuid
from datetime import datetime, timezone
from pathlib import Path
import duckdb
import snowflake.connector
from trayectorias.pipeline import TABLES, export_release
from trayectorias.report import render
from trayectorias.ingest import atomic_json

ALLOWED = {
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_ROLE",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
    "SNOWFLAKE_PRIVATE_KEY_PATH",
    "DBT_ENV_SECRET_SNOWFLAKE_PASSPHRASE",
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--config",
        type=Path,
        default=Path.home() / ".config/trayectorias/snowflake/connection.json",
    )
    a = p.parse_args()
    config = json.loads(a.config.read_text())
    if set(config) - ALLOWED:
        raise ValueError("Configuración contiene campos no admitidos")
    root = Path(__file__).resolve().parents[1]
    baseline = (root / "reports/current").resolve()
    prior = json.loads((baseline / "run.json").read_text())
    env = dict(os.environ, **config, DBT_SEND_ANONYMOUS_USAGE_STATS="false")
    run_id = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        + "_snowflake_"
        + uuid.uuid4().hex[:6]
    )
    release = root / "reports/snowflake/runs" / run_id
    release.mkdir(parents=True)
    status = {
        "run_id": run_id,
        "status": "running",
        "engine": "snowflake",
        "baseline_run": prior["run_id"],
        "steps": [],
    }

    def step(name):
        status["steps"].append(name)
        atomic_json(release / "run.json", status)
        print(name, flush=True)

    try:
        step("load_raw")
        with (release / "load.log").open("w") as log:
            subprocess.run(
                [sys.executable, str(root / "scripts/load_snowflake.py")],
                env=env,
                cwd=root,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True,
            )
        step("dbt_build")
        dbt = str(Path(sys.executable).parent / "dbt")
        with (release / "build.log").open("w") as log:
            subprocess.run(
                [
                    dbt,
                    "build",
                    "--project-dir",
                    str(root / "dbt"),
                    "--profiles-dir",
                    str(root / "dbt"),
                    "--target",
                    "snowflake",
                    "--target-path",
                    str(release / "dbt"),
                    "--log-path",
                    str(release / "logs"),
                ],
                env=env,
                cwd=root,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True,
            )
        step("compare_and_export")
        kwargs = {
            "account": config["SNOWFLAKE_ACCOUNT"],
            "user": config["SNOWFLAKE_USER"],
            "private_key_file": config["SNOWFLAKE_PRIVATE_KEY_PATH"],
            "role": config["SNOWFLAKE_ROLE"],
            "warehouse": config["SNOWFLAKE_WAREHOUSE"],
            "database": config["SNOWFLAKE_DATABASE"],
            "schema": "ANALYTICS",
        }
        if config.get("DBT_ENV_SECRET_SNOWFLAKE_PASSPHRASE"):
            kwargs["private_key_file_pwd"] = config[
                "DBT_ENV_SECRET_SNOWFLAKE_PASSPHRASE"
            ]
        with (
            snowflake.connector.connect(**kwargs) as sf,
            duckdb.connect(str(baseline / "warehouse.duckdb"), read_only=True) as local,
            duckdb.connect(str(release / "warehouse.duckdb")) as mirror,
            tempfile.TemporaryDirectory() as tmp,
        ):
            mirror.execute("create schema analytics")
            cursor = sf.cursor()

            def order(row):
                return tuple(
                    format(float(v), ".8f") if isinstance(v, (int, float)) else str(v)
                    for v in row
                )

            for table in TABLES:
                cursor.execute(f"SELECT * FROM ANALYTICS.{table.upper()}")
                names = [d[0].lower() for d in cursor.description]
                rows = cursor.fetchall()
                expected = local.execute(f"SELECT * FROM analytics.{table}")
                expected_names = [d[0] for d in expected.description]
                expected_rows = expected.fetchall()
                if names != expected_names or len(rows) != len(expected_rows):
                    raise RuntimeError("Contrato diferente: " + table)
                for left, right in zip(
                    sorted(rows, key=order), sorted(expected_rows, key=order)
                ):
                    for actual, want in zip(left, right):
                        if isinstance(actual, (int, float)) and isinstance(
                            want, (int, float)
                        ):
                            if not math.isclose(
                                actual, want, rel_tol=1e-9, abs_tol=1e-9
                            ):
                                raise RuntimeError("Valor diferente: " + table)
                        elif actual != want:
                            raise RuntimeError("Valor diferente: " + table)
                path = Path(tmp) / (table + ".csv")
                with path.open("w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(names)
                    writer.writerows(
                        [
                            [
                                v if v is not None else "__TRAYECTORIAS_NULL__"
                                for v in row
                            ]
                            for row in rows
                        ]
                    )
                types = {
                    r[0]: r[1]
                    for r in local.execute(f"DESCRIBE analytics.{table}").fetchall()
                }
                mirror.execute(
                    f"CREATE TABLE analytics.{table} AS SELECT * FROM read_csv(?,columns=?,header=true,nullstr='__TRAYECTORIAS_NULL__')",
                    [str(path), types],
                )
            tables = export_release(mirror, release)
        for filename in [
            "sources.json",
            "context_sources.json",
            "source_catalog.json",
            "wdi_metadata.json",
            "source_notes.json",
        ]:
            shutil.copy2(baseline / filename, release / filename)
        results = json.loads((release / "dbt/run_results.json").read_text())["results"]
        status.update(
            {
                k: prior[k]
                for k in [
                    "observations",
                    "context_observations",
                    "total_observations",
                    "source_families",
                    "years",
                    "dataset_sha256",
                    "sources_sha256",
                ]
            }
        )
        status.update(
            dbt_results=[
                {"id": x["unique_id"], "status": x["status"]} for x in results
            ],
            comparison="11 tablas iguales a DuckDB; tolerancia numérica 1e-9",
        )
        render(release, tables, status)
        status.update(
            status="success", finished_at=datetime.now(timezone.utc).isoformat()
        )
        atomic_json(release / "run.json", status)
        pointer = root / "reports/snowflake" / (".current_" + run_id)
        pointer.symlink_to(Path("runs") / run_id, target_is_directory=True)
        os.replace(pointer, root / "reports/snowflake/current")
        print("SUCCESS: " + str(release), flush=True)
    except Exception as e:
        status.update(status="failed", error=str(e))
        atomic_json(release / "run.json", status)
        raise


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    with (root / "data/.pipeline.lock").open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("Ya hay un pipeline en ejecución")
        main()
