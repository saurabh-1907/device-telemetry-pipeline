import pytest
pytest.importorskip("duckdb")
from telemetry_pipeline.aggregate import rollup
from telemetry_pipeline.fixtures import generate_fixture
from telemetry_pipeline.io import ingest_csv
from telemetry_pipeline.regression import compare_builds


def test_fixture_ingest_and_rollup(tmp_path):
    csv_path = generate_fixture(tmp_path / "telemetry.csv", devices=2, samples_per_device=4)
    db = tmp_path / "telemetry.duckdb"
    ingest_csv(csv_path, db)
    rows = rollup(str(db), "1 hour")
    assert rows
    assert {r["device_model"] for r in rows} == {"Atlas-13", "Nova-14"}
    assert all(r["samples"] == 1 for r in rows)


def test_regression_ranks_effect_size(tmp_path):
    csv_path = generate_fixture(tmp_path / "telemetry.csv", devices=4, samples_per_device=8, seed=4)
    db = tmp_path / "telemetry.duckdb"
    ingest_csv(csv_path, db)
    results = compare_builds(str(db), "2026.01", "2026.02", threshold=0.2)
    assert results
    assert results[0]["metric"] == "cpu_percent"
    assert results[0]["regression"] is True


def test_bad_input_is_rejected(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("timestamp,device_id\n2026-01-01T00:00:00Z,d1\n", encoding="utf-8")
    with pytest.raises(Exception, match="Missing required columns"):
        ingest_csv(path, tmp_path / "x.duckdb")
