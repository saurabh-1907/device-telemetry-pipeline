from __future__ import annotations
import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

METRICS = [
    ("cpu_percent", "%"), ("memory_percent", "%"), ("battery_level", "%"),
    ("battery_temperature_c", "C"), ("disk_read_mb_s", "MB/s")
]


def generate_fixture(path: str | Path, devices: int = 12, samples_per_device: int = 24, seed: int = 7) -> Path:
    if devices < 1 or samples_per_device < 1:
        raise ValueError("devices and samples_per_device must be positive")
    rng = random.Random(seed)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    bases = {"cpu_percent": 35, "memory_percent": 48, "battery_level": 72,
             "battery_temperature_c": 31, "disk_read_mb_s": 18}
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["timestamp", "device_id", "device_model", "os_build", "metric", "value", "unit"])
        writer.writeheader()
        for d in range(devices):
            model = "Atlas-13" if d % 2 == 0 else "Nova-14"
            for s in range(samples_per_device):
                ts = start + timedelta(hours=s)
                build = "2026.01" if s < samples_per_device // 2 else "2026.02"
                for metric, unit in METRICS:
                    value = bases[metric] + rng.gauss(0, 4)
                    if build == "2026.02" and metric == "cpu_percent":
                        value += 6
                    writer.writerow({"timestamp": ts.isoformat(), "device_id": f"device-{d:03d}",
                                     "device_model": model, "os_build": build, "metric": metric,
                                     "value": round(value, 4), "unit": unit})
    return path
