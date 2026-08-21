# Device Telemetry Pipeline

A working Python pipeline for device performance and battery telemetry. It ingests normalized CSV records into DuckDB, exposes SQL-backed rollups by device model, OS build and time window, and compares baseline/candidate build distributions using standardized mean difference (Cohen's d) plus a Mann–Whitney U p-value.

## Domain model: dual-message authorization and clearing

Modelled on the publicly documented ISO 8583 dual-message authorization/clearing flow used by card networks. Not affiliated with, endorsed by, or connected to Mastercard. No Mastercard code, data, or branding is used.

The implementation separates an authorization hold from later clearing/capture. `messages.py` provides a deliberately limited ISO-8583-style MTI plus field-map serializer/parser: `0100` authorization request, `0110` authorization response, and `0220` clearing. `reconcile.py` provides a reconciliation view that matches authorization and clearing records by transaction ID and reports matched, amount mismatch, missing clearing, and orphan clearing records.

This is an educational/domain model, not a private card-network protocol implementation.

## Telemetry data contract

Input CSV columns: `timestamp, device_id, device_model, os_build, metric, value, unit`.

Supported fixture metrics include CPU, memory, battery level/temperature and disk read throughput. Unknown metric names are retained; known metrics have unit validation.

## Usage

```bash
pip install -e '.[test]'
telemetry generate-fixture data/telemetry.csv
telemetry ingest data/telemetry.csv data/telemetry.duckdb
telemetry rollup data/telemetry.duckdb --window '1 hour'
telemetry regress data/telemetry.duckdb 2026.01 2026.02 --threshold 0.2
pytest
```

Regression ranking uses absolute Cohen's d. `regression=true` means the absolute effect size meets the supplied threshold; the pipeline does not assume whether higher or lower values are intrinsically bad because metric direction is domain-specific.

## Architecture

CSV → validation/normalisation → DuckDB `telemetry` table → SQL rollups or per-metric baseline/candidate extraction → effect-size ranking.

The fixture generator creates deterministic synthetic data solely for tests and demonstrations. No production telemetry, users, or usage claims are included.

## Error handling

CLI commands return exit code 2 for expected input/configuration failures and print a concise error to stderr. Library functions raise typed `TelemetryError` subclasses for invalid telemetry input.

## Scope and branding

No logos, brand assets, or proprietary network implementation are included. The message model uses generic card-network terminology and publicly documented ISO 8583 concepts only.
