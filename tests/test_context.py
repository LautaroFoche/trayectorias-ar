import json
from pathlib import Path
import pytest
from trayectorias.context import parse_wdi, pisa_number, observation, fetch_context
from trayectorias.ingest import ContractError, sha256

SOURCE = {"id": "wdi_data", "sha256": "a" * 64, "url": "https://example.test/data"}
SPEC = [
    {
        "code": "SE.SEC.ENRR",
        "label": "Matrícula bruta",
        "unit": "% de población en edad teórica",
        "note": "Puede superar 100%",
    }
]


def fixture(value=105):
    rows = [
        {
            "countryiso3code": c,
            "indicator": {"id": "SE.SEC.ENRR"},
            "date": str(y),
            "value": value,
        }
        for c in ["ARG", "BRA", "CHL", "URY"]
        for y in range(2000, 2026)
    ]
    return [{"page": 1, "pages": 1, "total": len(rows)}, rows]


def test_wdi_gross_over_100_and_null_are_distinct():
    body = fixture()
    body[1][0]["value"] = None
    rows = parse_wdi(json.dumps(body), SOURCE, SPEC)
    assert len(rows) == 104
    assert rows[0]["value"] is None and rows[0]["value_status"] == "sin_dato"
    assert rows[1]["value"] == 105 and rows[1]["value_status"] == "observado"


@pytest.mark.parametrize(
    "failure", ["pagination", "missing", "duplicate", "country", "negative"]
)
def test_wdi_rejects_incomplete_or_invalid_contract(failure):
    body = fixture()
    if failure == "pagination":
        body[0]["pages"] = 2
    elif failure == "missing":
        body[1].pop()
        body[0]["total"] -= 1
    elif failure == "duplicate":
        body[1][0] = body[1][1]
    elif failure == "country":
        body[1][0]["countryiso3code"] = "USA"
    elif failure == "negative":
        body[1][0]["value"] = -1
    with pytest.raises(ContractError):
        parse_wdi(json.dumps(body), SOURCE, SPEC)


@pytest.mark.parametrize("value", ["unknown", float("inf"), True])
def test_pisa_unknown_numeric_flags_fail(value):
    with pytest.raises(ContractError):
        pisa_number(value)


def test_observation_rejects_negative_uncertainty():
    with pytest.raises(ContractError):
        observation(SOURCE, country_code="ARG", value=50, standard_error=-1)


def test_offline_snapshot_tampering_fails(tmp_path):
    (tmp_path / "config").mkdir()
    (tmp_path / "data/raw").mkdir(parents=True)
    (tmp_path / "config/context_sources.json").write_text(
        json.dumps([{"id": "a", "url": "https://example.test"}])
    )
    (tmp_path / "snapshot").write_text("changed")
    (tmp_path / "data/raw/context_manifest.json").write_text(
        json.dumps(
            [
                {
                    "id": "a",
                    "url": "https://example.test",
                    "sha256": sha256(b"original"),
                    "path": "snapshot",
                }
            ]
        )
    )
    with pytest.raises(ContractError, match="Hash"):
        fetch_context(tmp_path, True)


def test_reviewed_pdf_denominators_are_explicit():
    registry = json.loads(
        (Path(__file__).resolve().parents[1] / "config/kids_reviewed.json").read_text()
    )
    rows = {r["indicator"]: r for r in registry["observations"]}
    assert "Sólo quienes" in rows["menor_rendimiento"]["denominator"]
    assert rows["menor_rendimiento"]["sample_n"] is None
    assert rows["chatgpt_tarea"]["sample_n"] == 3416
    assert registry["fieldwork_year"] == 2024 and registry["publication_year"] == 2025
