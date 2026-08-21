from __future__ import annotations
import duckdb


def rollup(db_path: str, window: str = "1 hour") -> list[dict]:
    if not window or not window.strip():
        raise ValueError("window must be non-empty, e.g. '1 hour' or '1 day'")
    con = duckdb.connect(db_path, read_only=True)
    try:
        q = """
        SELECT device_model, os_build,
               time_bucket(CAST(? AS INTERVAL), timestamp) AS window_start,
               metric, COUNT(*) AS samples, AVG(value) AS mean,
               STDDEV_SAMP(value) AS stddev, MIN(value) AS min, MAX(value) AS max
        FROM telemetry
        GROUP BY 1,2,3,4 ORDER BY 1,2,3,4
        """
        return [dict(zip([d[0] for d in con.description], row)) for row in con.execute(q, [window]).fetchall()]
    finally:
        con.close()
