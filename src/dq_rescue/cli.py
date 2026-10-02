from __future__ import annotations

import json
import sys

from .core import Transaction, fail_closed, quality_report, sample


def smoke() -> int:
    print(json.dumps(quality_report(sample()), indent=2, sort_keys=True))
    return 0


def reverse_test() -> int:
    cases: list[dict[str, str]] = []

    try:
        fail_closed(
            sample() + [Transaction("T004", "C004", 2, 50, 10, "paid")]
        )
    except ValueError as exc:
        cases.append(
            {"case": "arithmetic-mismatch", "status": "PASS", "error": str(exc)}
        )
    else:
        cases.append(
            {
                "case": "arithmetic-mismatch",
                "status": "FAIL",
                "error": "corruption accepted",
            }
        )

    try:
        rows = sample()
        fail_closed(rows + [rows[0]])
    except ValueError as exc:
        cases.append(
            {"case": "duplicate-key", "status": "PASS", "error": str(exc)}
        )
    else:
        cases.append(
            {"case": "duplicate-key", "status": "FAIL", "error": "corruption accepted"}
        )

    print(json.dumps(cases, indent=2, sort_keys=True))
    return 0 if all(case["status"] == "PASS" for case in cases) else 1


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else "smoke"
    if command == "smoke":
        return smoke()
    if command == "reverse-test":
        return reverse_test()
    print(
        "usage: python -m dq_rescue.cli [smoke|reverse-test]",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
