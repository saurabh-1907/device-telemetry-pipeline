from __future__ import annotations
import argparse
import json
import sys
from .aggregate import rollup
from .errors import TelemetryError
from .fixtures import generate_fixture
from .io import ingest_csv
from .regression import compare_builds


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="telemetry")
    sub = parser.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate-fixture"); g.add_argument("path"); g.add_argument("--devices", type=int, default=12); g.add_argument("--samples", type=int, default=24); g.add_argument("--seed", type=int, default=7)
    i = sub.add_parser("ingest"); i.add_argument("csv"); i.add_argument("db")
    a = sub.add_parser("rollup"); a.add_argument("db"); a.add_argument("--window", default="1 hour")
    r = sub.add_parser("regress"); r.add_argument("db"); r.add_argument("baseline"); r.add_argument("candidate"); r.add_argument("--threshold", type=float, default=0.2); r.add_argument("--model")
    try:
        args = parser.parse_args(argv)
        if args.cmd == "generate-fixture":
            generate_fixture(args.path, args.devices, args.samples, args.seed)
        elif args.cmd == "ingest":
            ingest_csv(args.csv, args.db)
        elif args.cmd == "rollup":
            print(json.dumps(rollup(args.db, args.window), default=str, indent=2))
        elif args.cmd == "regress":
            print(json.dumps(compare_builds(args.db, args.baseline, args.candidate, args.threshold, args.model), indent=2))
        return 0
    except (TelemetryError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
