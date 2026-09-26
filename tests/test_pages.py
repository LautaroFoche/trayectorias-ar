"""El paquete público excluye material operativo y rechaza releases fallidos."""

import json
from pathlib import Path
import runpy

import pytest
from trayectorias.pipeline import TABLES

build_pages = runpy.run_path(str(Path(__file__).parents[1] / "scripts/build_pages.py"))[
    "build_pages"
]


def test_pages_only_publishes_allowed_artifacts(tmp_path):
    release = tmp_path / "release"
    (release / "exports").mkdir(parents=True)
    (release / "dashboard.html").write_text("<html>reporte</html>")
    (release / "run.json").write_text(
        json.dumps(
            {
                "status": "success",
                "dbt_results": [{"status": "pass"}],
                "private_config": "not-public",
            }
        )
    )
    for name in ("sources.json", "source_catalog.json"):
        (release / name).write_text(
            json.dumps([{"sha256": "abc", "path": "/private/path"}])
        )
    (release / "connection.json").write_text("not-public")
    (release / "build.log").write_text("not-public")
    for table in TABLES:
        for extension in ("csv", "parquet"):
            (release / "exports" / f"{table}.{extension}").write_bytes(b"fixture")
    out = tmp_path / "site"
    build_pages(release, out)
    assert (out / "index.html").read_text() == "<html>reporte</html>"
    assert not (out / "connection.json").exists()
    assert not (out / "build.log").exists()
    assert "private_config" not in json.loads((out / "run.json").read_text())
    assert "path" not in json.loads((out / "sources.json").read_text())[0]
    assert len(list(out.rglob("*"))) == 29


def test_pages_rejects_failed_release(tmp_path):
    (tmp_path / "run.json").write_text('{"status":"failed"}')
    with pytest.raises(ValueError, match="validada"):
        build_pages(tmp_path, tmp_path / "site")
    assert not (tmp_path / "site").exists()
