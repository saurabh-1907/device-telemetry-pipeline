from __future__ import annotations
import math
import duckdb
from scipy.stats import mannwhitneyu


def _values(con, build: str, metric: str, model: str | None = None):
    sql = "SELECT value FROM telemetry WHERE os_build = ? AND metric = ?"
    args = [build, metric]
    if model:
        sql += " AND device_model = ?"
        args.append(model)
    return [r[0] for r in con.execute(sql, args).fetchall()]


def _variance(values):
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return sum((x - mean) ** 2 for x in values) / (len(values) - 1)


def compare_builds(db_path: str, baseline: str, candidate: str, threshold: float = 0.2, model: str | None = None) -> list[dict]:
    if threshold < 0:
        raise ValueError("threshold must be >= 0")
    con = duckdb.connect(db_path, read_only=True)
    try:
        metrics = [r[0] for r in con.execute(
            "SELECT DISTINCT metric FROM telemetry WHERE os_build IN (?, ?) ORDER BY metric", [baseline, candidate]
        ).fetchall()]
        results = []
        for metric in metrics:
            base = _values(con, baseline, metric, model)
            cand = _values(con, candidate, metric, model)
            if not base or not cand:
                continue
            base_mean, cand_mean = sum(base) / len(base), sum(cand) / len(cand)
            denominator = len(base) + len(cand) - 2
            pooled = math.sqrt(((len(base) - 1) * _variance(base) + (len(cand) - 1) * _variance(cand)) / denominator) if denominator > 0 else 0.0
            effect = (cand_mean - base_mean) / pooled if pooled else (0.0 if cand_mean == base_mean else math.inf)
            stat = mannwhitneyu(cand, base, alternative="two-sided")
            results.append({"metric": metric, "baseline_n": len(base), "candidate_n": len(cand),
                            "baseline_mean": base_mean, "candidate_mean": cand_mean,
                            "cohens_d": effect, "p_value": float(stat.pvalue),
                            "regression": abs(effect) >= threshold})
        return sorted(results, key=lambda r: abs(r["cohens_d"]), reverse=True)
    finally:
        con.close()
