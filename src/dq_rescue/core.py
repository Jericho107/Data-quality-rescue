from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import asdict, dataclass

VALID_STATUS = {"paid", "pending", "refunded"}


@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    customer_id: str
    quantity: int
    unit_price: float
    reported_total: float
    status: str


@dataclass(frozen=True)
class Defect:
    transaction_id: str
    rule: str
    severity: str


def inspect(rows: Iterable[Transaction]) -> list[Defect]:
    defects: list[Defect] = []
    seen: set[str] = set()
    for row in rows:
        identifier = row.transaction_id or "<missing>"
        if not row.transaction_id:
            defects.append(
                Defect(identifier, "missing_transaction_id", "critical")
            )
            continue
        if row.transaction_id in seen:
            defects.append(
                Defect(identifier, "duplicate_business_key", "critical")
            )
        seen.add(row.transaction_id)
        if not row.customer_id:
            defects.append(Defect(identifier, "missing_customer", "high"))
        if row.quantity <= 0:
            defects.append(Defect(identifier, "invalid_quantity", "high"))
        if row.unit_price < 0:
            defects.append(Defect(identifier, "negative_unit_price", "critical"))
        if abs(row.quantity * row.unit_price - row.reported_total) > 0.01:
            defects.append(Defect(identifier, "arithmetic_mismatch", "critical"))
        if row.status not in VALID_STATUS:
            defects.append(Defect(identifier, "invalid_status", "high"))
    return defects


def fail_closed(rows: Iterable[Transaction]) -> None:
    defects = inspect(rows)
    material = [
        defect
        for defect in defects
        if defect.severity in {"critical", "high"}
    ]
    if material:
        raise ValueError(f"material data-quality defects: {len(material)}")


def quality_report(rows: Iterable[Transaction]) -> dict[str, object]:
    items = list(rows)
    defects = inspect(items)
    severity = Counter(defect.severity for defect in defects)
    rules = Counter(defect.rule for defect in defects)
    return {
        "rows": len(items),
        "defects": len(defects),
        "severity": dict(sorted(severity.items())),
        "rules": dict(sorted(rules.items())),
        "clean": not defects,
        "detail": [asdict(defect) for defect in defects],
    }


def sample() -> list[Transaction]:
    return [
        Transaction("T001", "C001", 2, 40.0, 80.0, "paid"),
        Transaction("T002", "C002", 1, 125.0, 125.0, "pending"),
        Transaction("T003", "C003", 3, 10.0, 30.0, "paid"),
    ]
