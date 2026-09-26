"""Empaqueta únicamente los productos públicos de una ejecución validada."""

import argparse
import json
from pathlib import Path
import shutil

from trayectorias.pipeline import TABLES

RUN_FIELDS = (
    "run_id",
    "status",
    "started_at",
    "finished_at",
    "duration_seconds",
    "total_observations",
    "observations",
    "context_observations",
    "source_families",
    "years",
    "dataset_sha256",
    "education_sha256",
    "code_sha256",
    "sources_sha256",
    "dbt_results",
)
SOURCE_FIELDS = (
    "source_id",
    "indicator",
    "family",
    "producer",
    "format",
    "url",
    "sha256",
    "retrieved_at",
    "bytes",
)


def build_pages(release, destination):
    release = Path(release).resolve()
    destination = Path(destination)
    run = json.loads((release / "run.json").read_text())
    if run.get("status") != "success" or not run.get("dbt_results"):
        raise ValueError("Sólo se publica una ejecución validada")
    if any(r["status"] not in ("pass", "success") for r in run["dbt_results"]):
        raise ValueError("La ejecución contiene controles fallidos")
    files = ["dashboard.html"] + [
        f"exports/{table}.{extension}"
        for table in TABLES
        for extension in ("csv", "parquet")
    ]
    for name in files:
        source = release / name
        if (
            not source.is_file()
            or source.is_symlink()
            or not source.resolve().is_relative_to(release)
        ):
            raise ValueError("Artefacto ausente o fuera del release: " + name)
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "exports").mkdir()
    for name in files:
        shutil.copyfile(release / name, destination / name)
    shutil.copyfile(destination / "dashboard.html", destination / "index.html")
    (destination / ".nojekyll").touch()
    (destination / "run.json").write_text(
        json.dumps(
            {key: run[key] for key in RUN_FIELDS if key in run},
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )
    for name in ("sources.json", "source_catalog.json"):
        sources = json.loads((release / name).read_text())
        public = [
            {key: row[key] for key in SOURCE_FIELDS if key in row} for row in sources
        ]
        (destination / name).write_text(
            json.dumps(public, ensure_ascii=False, indent=2) + "\n"
        )
    print(f"Sitio público preparado: {destination}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", type=Path, default=Path("reports/current"))
    parser.add_argument("--output", type=Path, default=Path("reports/pages"))
    args = parser.parse_args()
    build_pages(args.release, args.output)
