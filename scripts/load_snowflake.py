"""Carga transaccional de las tres tablas raw en Snowflake."""

import argparse
import json
import os
from pathlib import Path
import re
import snowflake.connector
from trayectorias.ingest import fetch_sources, normalize_sources
from trayectorias.context import (
    fetch_context,
    normalize_context,
    source_catalog,
    CONTEXT_COLUMNS,
    SOURCE_COLUMNS,
)
from trayectorias.pipeline import COLUMNS


def identifier(value):
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        raise ValueError("Identificador Snowflake inválido")
    return value.upper()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    root = parser.parse_args().root
    education = fetch_sources(root, offline=True)
    context = fetch_context(root, offline=True)
    tables = [
        ("observations", COLUMNS, normalize_sources(root, education), "observation_id"),
        (
            "context_observations",
            CONTEXT_COLUMNS,
            normalize_context(root, context),
            "observation_id",
        ),
        (
            "source_catalog",
            SOURCE_COLUMNS,
            source_catalog(education, context),
            "source_id",
        ),
    ]
    options = dict(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        private_key_file=os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"],
        role=os.environ.get("SNOWFLAKE_ROLE", "TRAYECTORIAS_ROLE"),
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "TRAYECTORIAS_WH"),
        database=os.environ.get("SNOWFLAKE_DATABASE", "TRAYECTORIAS_AR"),
    )
    passphrase = os.environ.get("DBT_ENV_SECRET_SNOWFLAKE_PASSPHRASE")
    if passphrase:
        options["private_key_file_pwd"] = passphrase
    database = identifier(options["database"])
    with snowflake.connector.connect(**options) as connection:
        with connection.cursor() as cursor:
            # DDL fuera de la transacción: las tres sustituciones DML se confirman juntas.
            for table, columns, rows, key in tables:
                ddl = ", ".join(
                    f"{identifier(k)} {'FLOAT' if v == 'DOUBLE' else v}"
                    for k, v in columns.items()
                )
                cursor.execute(
                    f"CREATE TABLE IF NOT EXISTS {database}.RAW.{identifier(table)} ({ddl})"
                )
            cursor.execute("BEGIN")
            try:
                for table, columns, rows, key in tables:
                    target = f"{database}.RAW.{identifier(table)}"
                    cursor.execute(f"DELETE FROM {target}")
                    fields = ",".join(identifier(k) for k in columns)
                    marks = ",".join("%s" for _ in columns)
                    cursor.executemany(
                        f"INSERT INTO {target} ({fields}) VALUES ({marks})",
                        [[r[k] for k in columns] for r in rows],
                    )
                    cursor.execute(
                        f"SELECT COUNT(*),COUNT(DISTINCT {identifier(key)}) FROM {target}"
                    )
                    if cursor.fetchone() != (len(rows), len(rows)):
                        raise RuntimeError("Carga incompleta: " + table)
                cursor.execute("COMMIT")
            except Exception:
                cursor.execute("ROLLBACK")
                raise
    print(
        json.dumps(
            {
                "status": "raw_loaded",
                "rows": {t: len(rows) for t, c, rows, k in tables},
                "next": "dbt build --target snowflake",
            }
        )
    )


if __name__ == "__main__":
    main()
