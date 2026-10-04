from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

from .core import Transaction, fail_closed, quality_report, sample
from .pipeline import process, sample_corrupt
from .reporting import write_rescue_report


def smoke() -> int:
    payload = quality_report(sample())
    payload["persisted_clean_run"] = process(sample(), ":memory:")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def report() -> int:
    path = Path("output/dq_evidence.sqlite")
    path.parent.mkdir(parents=True, exist_ok=True)
    report_path = write_rescue_report(path, "output/data_quality_rescue.html")
    print(report_path.as_posix())
    return 0


def reverse_test() -> int:
    cases: list[dict[str, str]] = []

    try:
        fail_closed(sample() + [Transaction("T004", "C004", 2, 50, 10, "paid")])
    except ValueError as exc:
        cases.append({"case": "arithmetic-mismatch", "status": "PASS", "error": str(exc)})
    else:
        cases.append({"case": "arithmetic-mismatch", "status": "FAIL", "error": "corruption accepted"})

    path = Path("output/reverse_dq.sqlite")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    blocked = process(sample_corrupt(), path)
    recovered = process(sample(), path)

    cases.append(
        {
            "case": "quarantine-release-gate",
            "status": "PASS" if blocked["status"] == "BLOCKED" and blocked["quarantined_rows"] == 2 else "FAIL",
            "error": "material rows quarantined" if blocked["status"] == "BLOCKED" else "unsafe release",
        }
    )
    cases.append(
        {
            "case": "clean-recovery",
            "status": "PASS" if recovered["status"] == "PASS" and recovered["quarantined_rows"] == 0 else "FAIL",
            "error": "clean source released" if recovered["status"] == "PASS" else "clean recovery failed",
        }
    )

    with sqlite3.connect(path) as connection:
        run_count = connection.execute("SELECT COUNT(*) FROM dq_runs").fetchone()[0]
    cases.append(
        {
            "case": "evidence-history",
            "status": "PASS" if run_count == 2 else "FAIL",
            "error": f"{run_count} distinct source states persisted",
        }
    )

    print(json.dumps(cases, indent=2, sort_keys=True))
    return 0 if all(case["status"] == "PASS" for case in cases) else 1


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else "smoke"
    if command == "smoke":
        return smoke()
    if command == "report":
        return report()
    if command == "reverse-test":
        return reverse_test()
    print("usage: python -m dq_rescue.cli [smoke|report|reverse-test]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
