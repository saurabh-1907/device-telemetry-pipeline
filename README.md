# Device Telemetry Pipeline

A working Python pipeline for device performance and battery telemetry. It ingests normalized CSV records into DuckDB, exposes SQL-backed rollups by device model, OS build and time window, and compares baseline/candidate build distributions using standardized mean difference (Cohen's d) plus a Mann–Whitney U p-value.

## Data contract

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
