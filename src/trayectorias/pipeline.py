"""Construye una versión aislada; sólo publica si todos los controles pasan."""

from __future__ import annotations
import csv
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid
import duckdb
from .ingest import atomic_json, fetch_sources, normalize_sources, sha256
from .context import (
    fetch_context,
    normalize_context,
    source_catalog,
    CONTEXT_COLUMNS,
    SOURCE_COLUMNS,
)

TABLES = [
    "dim_geography",
    "dim_period",
    "dim_indicator",
    "fct_education_rates",
    "mart_continuity",
    "mart_quality",
    "dim_context_indicator",
    "fct_context_indicators",
    "mart_digital_evidence",
    "mart_national_context",
    "mart_source_coverage",
]
COLUMNS = {
    "observation_id": "VARCHAR",
    "year": "INTEGER",
    "year_to": "INTEGER",
    "geo_code": "VARCHAR",
    "geo_name": "VARCHAR",
    "geo_type": "VARCHAR",
    "parent_code": "VARCHAR",
    "structure": "VARCHAR",
    "level": "VARCHAR",
    "grade": "INTEGER",
    "indicator": "VARCHAR",
    "value": "DOUBLE",
    "value_status": "VARCHAR",
    "source_sha256": "VARCHAR",
    "source_url": "VARCHAR",
    "source_member": "VARCHAR",
    "source_sheet": "VARCHAR",
    "source_cell": "VARCHAR",
}


def load_raw(path, records, context_records=None, catalog=None):
    with duckdb.connect(str(path)) as conn:
        conn.execute("create schema raw")
        ddl = ", ".join(f'"{k}" {v}' for k, v in COLUMNS.items())
        conn.execute(f"create table raw.observations ({ddl})")
        marks = ",".join("?" for _ in COLUMNS)
        conn.execute("begin transaction")
        conn.executemany(
            f"insert into raw.observations values ({marks})",
            [[r[k] for k in COLUMNS] for r in records],
        )
        for table, columns, items in [
            ("context_observations", CONTEXT_COLUMNS, context_records or []),
            ("source_catalog", SOURCE_COLUMNS, catalog or []),
        ]:
            definition = ", ".join(f'"{k}" {v}' for k, v in columns.items())
            conn.execute(f"create table raw.{table} ({definition})")
            if items:
                conn.executemany(
                    f"insert into raw.{table} values ({','.join('?' for _ in columns)})",
                    [[r[k] for k in columns] for r in items],
                )
        conn.execute("commit")


def query_records(conn, table):
    result = conn.execute(f"select * from analytics.{table} order by 1,2")
    fields = [c[0] for c in result.description]
    return [dict(zip(fields, row)) for row in result.fetchall()]


def export_release(conn, release):
    exports = release / "exports"
    exports.mkdir()
    all_rows = {}
    for table in TABLES:
        rows = query_records(conn, table)
        all_rows[table] = rows
        with (exports / f"{table}.csv").open(
            "w", encoding="utf-8-sig", newline=""
        ) as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        dest = str(exports / f"{table}.parquet").replace("'", "''")
        conn.execute(
            f"copy (select * from analytics.{table} order by 1,2) to '{dest}' (format parquet)"
        )
    return all_rows


def code_fingerprint(root):
    """Identifica fuentes de código y configuración sin incluir artefactos generados."""
    paths = []
    for folder in ["src", "dbt", "config", "scripts"]:
        for path in (root / folder).rglob("*"):
            relative = path.relative_to(root)
            if any(
                part in {"target", "logs", "__pycache__"} for part in relative.parts
            ):
                continue
            if path.is_file() and path.suffix in {
                ".py",
                ".html",
                ".js",
                ".sql",
                ".yml",
                ".json",
            }:
                paths.append(path)
    return sha256(
        b"".join(
            str(path.relative_to(root)).encode() + b"\0" + path.read_bytes() + b"\0"
            for path in sorted(paths)
        )
    )


def run(root: Path, offline=False):
    root = root.resolve()
    (root / "data").mkdir(exist_ok=True)
    with (root / "data/.pipeline.lock").open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("Ya hay un pipeline en ejecución")
        return _run(root, offline)


def _run(root, offline):
    run_id = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        + "_"
        + uuid.uuid4().hex[:8]
    )
    release = root / "reports/runs" / run_id
    release.mkdir(parents=True)
    started = time.monotonic()
    status = {
        "run_id": run_id,
        "status": "running",
        "offline": offline,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "steps": [],
    }

    def event(step):
        status["steps"].append(step)
        atomic_json(release / "run.json", status)
        print(
            json.dumps({"run_id": run_id, "step": step}, ensure_ascii=False), flush=True
        )

    try:
        event("fetch")
        manifest = fetch_sources(root, offline)
        atomic_json(release / "sources.json", manifest)
        event("fetch_context")
        context_manifest = fetch_context(root, offline)
        atomic_json(release / "context_sources.json", context_manifest)
        event("normalize")
        records = normalize_sources(root, manifest)
        event("normalize_context")
        context_records = normalize_context(root, context_manifest)
        catalog = source_catalog(manifest, context_manifest)
        atomic_json(release / "source_catalog.json", catalog)
        shutil.copy2(
            root / "data/normalized/wdi_metadata.json", release / "wdi_metadata.json"
        )
        shutil.copy2(
            root / "data/normalized/source_notes.json", release / "source_notes.json"
        )
        db = release / "warehouse.duckdb"
        event("load")
        load_raw(db, records, context_records, catalog)
        event("dbt_build")
        env = dict(
            os.environ, DBT_WAREHOUSE=str(db), DBT_SEND_ANONYMOUS_USAGE_STATS="false"
        )
        dbt = str(Path(sys.executable).parent / "dbt")
        common = [
            "--project-dir",
            str(root / "dbt"),
            "--profiles-dir",
            str(root / "dbt"),
            "--target-path",
            str(release / "dbt"),
            "--log-path",
            str(release / "logs"),
        ]
        for command in ["build", "docs generate"]:
            with (release / (command.replace(" ", "_") + ".log")).open("w") as log:
                subprocess.run(
                    [dbt, *command.split(), *common],
                    env=env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    check=True,
                )
                if command == "build":
                    shutil.copy2(
                        release / "dbt/run_results.json",
                        release / "dbt/build_results.json",
                    )
        event("export")
        with duckdb.connect(str(db), read_only=True) as conn:
            tables = export_release(conn, release)
        result = json.loads((release / "dbt/build_results.json").read_text())
        status.update(
            observations=len(records),
            context_observations=len(context_records),
            total_observations=len(records) + len(context_records),
            source_families=len({s["family"] for s in catalog}),
            years=sorted({r["year"] for r in records}),
            education_sha256=sha256(
                json.dumps(records, sort_keys=True, ensure_ascii=False).encode()
            ),
            dataset_sha256=sha256(
                json.dumps(
                    {"education": records, "context": context_records},
                    sort_keys=True,
                    ensure_ascii=False,
                ).encode()
            ),
            code_sha256=code_fingerprint(root),
            sources_sha256={s["source_id"]: s["sha256"] for s in catalog},
            dbt_results=[
                {"id": x["unique_id"], "status": x["status"]}
                for x in result.get("results", [])
            ],
        )
        from .report import render

        render(release, tables, status)
        status.update(
            status="success",
            duration_seconds=round(time.monotonic() - started, 2),
            finished_at=datetime.now(timezone.utc).isoformat(),
        )
        atomic_json(release / "run.json", status)
        # Un único cambio de puntero publica juntos warehouse, dashboard y exports.
        pointer = root / "reports" / f".current_{run_id}"
        pointer.symlink_to(Path("runs") / run_id, target_is_directory=True)
        os.replace(pointer, root / "reports/current")
        warehouse = root / "data/warehouse.duckdb"
        if not warehouse.exists() and not warehouse.is_symlink():
            warehouse.symlink_to("../reports/current/warehouse.duckdb")
        print(json.dumps(status, ensure_ascii=False), flush=True)
        return release
    except Exception as exc:
        status.update(
            status="failed",
            error=f"{type(exc).__name__}: {exc}",
            duration_seconds=round(time.monotonic() - started, 2),
        )
        atomic_json(release / "run.json", status)
        raise
