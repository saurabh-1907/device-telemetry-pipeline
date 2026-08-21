from __future__ import annotations
import csv
from pathlib import Path
from typing import Iterable
import duckdb
from .errors import InputValidationError
from .schema import REQUIRED_COLUMNS, ALLOWED_UNITS


def _validate_rows(rows: Iterable[dict]) -> list[dict]:
    rows = list(rows)
    if not rows:
        raise InputValidationError("Telemetry input contains no rows")
    missing = set(REQUIRED_COLUMNS) - set(rows[0])
    if missing:
        raise InputValidationError(f"Missing required columns: {', '.join(sorted(missing))}")
    out = []
    for i, row in enumerate(rows, 2):
        try:
            if not all(str(row[k]).strip() for k in REQUIRED_COLUMNS):
                raise ValueError("empty required field")
            metric = str(row["metric"]).strip()
            value = float(row["value"])
            unit = str(row["unit"]).strip()
            if metric in ALLOWED_UNITS and unit != ALLOWED_UNITS[metric]:
                raise ValueError(f"unit {unit!r} does not match expected {ALLOWED_UNITS[metric]!r}")
            out.append({**row, "timestamp": str(row["timestamp"]).strip(), "device_id": str(row["device_id"]).strip(),
                        "device_model": str(row["device_model"]).strip(), "os_build": str(row["os_build"]).strip(),
                        "metric": metric, "value": value, "unit": unit})
        except (TypeError, ValueError) as exc:
            raise InputValidationError(f"Invalid telemetry row {i}: {exc}") from exc
    return out


def ingest_csv(csv_path: str | Path, db_path: str | Path) -> None:
    path = Path(csv_path)
    if not path.exists():
        raise InputValidationError(f"Input file does not exist: {path}")
    try:
        with path.open(newline="", encoding="utf-8") as fh:
            rows = _validate_rows(csv.DictReader(fh))
    except csv.Error as exc:
        raise InputValidationError(f"Invalid CSV: {exc}") from exc

    con = duckdb.connect(str(db_path))
    try:
        con.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                timestamp TIMESTAMP NOT NULL, device_id VARCHAR NOT NULL,
                device_model VARCHAR NOT NULL, os_build VARCHAR NOT NULL,
                metric VARCHAR NOT NULL, value DOUBLE NOT NULL, unit VARCHAR NOT NULL
            )
        """)
        con.executemany(
            "INSERT INTO telemetry VALUES (CAST(? AS TIMESTAMP), ?, ?, ?, ?, ?, ?)",
            [(r["timestamp"], r["device_id"], r["device_model"], r["os_build"], r["metric"], r["value"], r["unit"]) for r in rows],
        )
    finally:
        con.close()
