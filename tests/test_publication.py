import fcntl
import json
import pytest
from trayectorias import pipeline
from trayectorias.ingest import ContractError


def test_failed_source_does_not_replace_last_good_release(tmp_path, monkeypatch):
    (tmp_path / "reports/old").mkdir(parents=True)
    (tmp_path / "reports/current").symlink_to("old", target_is_directory=True)
    sentinel = tmp_path / "reports/current/dashboard.html"
    sentinel.write_text("last valid")

    def fail(*args):
        raise ContractError("Fuente corrupta")

    monkeypatch.setattr(pipeline, "fetch_sources", fail)
    with pytest.raises(ContractError):
        pipeline.run(tmp_path)
    assert sentinel.read_text() == "last valid"
    assert (tmp_path / "reports/current").resolve() == tmp_path / "reports/old"
    log = next((tmp_path / "reports/runs").glob("*/run.json"))
    assert json.loads(log.read_text())["status"] == "failed"


def test_concurrent_writer_rejected(tmp_path):
    (tmp_path / "data").mkdir()
    with (tmp_path / "data/.pipeline.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(RuntimeError, match="ejecución"):
            pipeline.run(tmp_path)


def test_code_fingerprint_excludes_generated_artifacts_and_tracks_renames(tmp_path):
    (tmp_path / "dbt/models").mkdir(parents=True)
    source = tmp_path / "dbt/models/example.sql"
    source.write_text("select 1")
    original = pipeline.code_fingerprint(tmp_path)
    (tmp_path / "dbt/target").mkdir()
    (tmp_path / "dbt/target/manifest.json").write_text('{"generated": true}')
    assert pipeline.code_fingerprint(tmp_path) == original
    source.rename(source.with_name("renamed.sql"))
    assert pipeline.code_fingerprint(tmp_path) != original
