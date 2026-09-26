import io
import json
import zipfile
import pytest
from openpyxl import Workbook
from trayectorias.ingest import (
    ContractError,
    GEOGRAPHIES,
    parse_workbook,
    sha256,
    fetch_sources,
    normalize_label,
)

SOURCE = {
    "indicator": "abandono",
    "sha256": "a" * 64,
    "url": "https://example.invalid/source.zip",
}


def fixture_zip(change=None):
    """Datos sintéticos sólo para probar contratos; nunca alimentan el reporte."""
    book = Workbook()
    sheet = book.active
    sheet.title = "2024-2025"
    sheet.append(
        ["División", "Estructura Educativa", "Primaria"]
        + [None] * 7
        + ["Secundaria"]
        + [None] * 6
    )
    sheet.append(
        [None, None, "Total"]
        + [f"{i}° Año" for i in range(1, 8)]
        + ["Total"]
        + [f"{i}° Año" for i in range(7, 13)]
    )
    for code, name, kind, parent in GEOGRAPHIES:
        values = [6.5] * 15
        structure = None if code == "00" else "6-6"
        if structure:
            values[7] = None
        sheet.append([name, structure] + values)
    if change:
        change(book)
    content = io.BytesIO()
    book.save(content)
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as z:
        z.writestr("Tasa según división político-territorial.xlsx", content.getvalue())
    return output.getvalue()


def test_preserves_negative_published_value_and_lineage():
    rows, _ = parse_workbook(
        fixture_zip(lambda b: setattr(b.active["C3"], "value", -0.5)), SOURCE
    )
    row = next(r for r in rows if r["source_cell"] == "C3")
    assert row["value"] == -0.5 and row["value_status"] == "fuera_rango_teorico"
    assert row["source_sheet"] == "2024-2025" and row["year_to"] == 2025
    assert row["source_sha256"] == SOURCE["sha256"]


def test_separates_missing_from_structural_null():
    rows, _ = parse_workbook(
        fixture_zip(lambda b: setattr(b.active["C4"], "value", None)), SOURCE
    )
    assert (
        next(r for r in rows if r["source_cell"] == "C4")["value_status"] == "faltante"
    )
    assert (
        next(r for r in rows if r["source_cell"] == "J4")["value_status"] == "no_aplica"
    )
    assert len(rows) == 27 * 15


@pytest.mark.parametrize(
    "cell,value",
    [
        ("C4", "s/d"),
        ("A4", "Jurisdicción desconocida"),
        ("C1", "Otro nivel"),
        ("D2", "Primer grado"),
        ("J4", 1),
    ],
)
def test_schema_and_values_fail_closed(cell, value):
    with pytest.raises(ContractError):
        parse_workbook(
            fixture_zip(lambda b: setattr(b.active[cell], "value", value)), SOURCE
        )


def test_missing_geography_fails():
    with pytest.raises(ContractError):
        parse_workbook(fixture_zip(lambda b: b.active.delete_rows(29)), SOURCE)


def test_nonconsecutive_transition_fails():
    with pytest.raises(ContractError):
        parse_workbook(
            fixture_zip(lambda b: setattr(b.active, "title", "2024-2026")), SOURCE
        )


def test_duplicate_geography_fails():
    with pytest.raises(ContractError):
        parse_workbook(
            fixture_zip(lambda b: setattr(b.active["A4"], "value", "Total País")),
            SOURCE,
        )


def test_unknown_sheet_fails():
    with pytest.raises(ContractError):
        parse_workbook(fixture_zip(lambda b: b.create_sheet("Otra tabla")), SOURCE)


def test_label_normalization():
    assert normalize_label("  CÓRDOBA  ") == normalize_label("Cordoba")


def test_hash_tampering_fails_offline(tmp_path):
    (tmp_path / "config").mkdir()
    (tmp_path / "data/raw").mkdir(parents=True)
    source = dict(SOURCE, path="data/raw/file.zip", sha256=sha256(b"original"))
    (tmp_path / "config/sources.json").write_text(json.dumps([SOURCE]))
    (tmp_path / "data/raw/manifest.json").write_text(json.dumps([source]))
    (tmp_path / "data/raw/file.zip").write_bytes(b"tampered")
    with pytest.raises(ContractError, match="Hash"):
        fetch_sources(tmp_path, offline=True)


def test_keys_stable_between_replays():
    content = fixture_zip()
    a, _ = parse_workbook(content, SOURCE)
    b, _ = parse_workbook(content, SOURCE)
    assert a == b and len({r["observation_id"] for r in a}) == len(a)
