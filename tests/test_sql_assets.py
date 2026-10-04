import sqlite3
from pathlib import Path

from dq_rescue.core import sample
from dq_rescue.pipeline import process, sample_corrupt

ROOT = Path(__file__).resolve().parents[1]


def _sql(name: str) -> str:
    return (ROOT / "sql" / name).read_text(encoding="utf-8")


def test_release_gate_sql_distinguishes_blocked_and_pass(tmp_path):
    path = tmp_path / "dq.sqlite"
    process(sample_corrupt(), path)
    process(sample(), path)

    with sqlite3.connect(path) as connection:
        rows = connection.execute(_sql("10_release_gate.sql")).fetchall()

    statuses = {row[-1] for row in rows}
    assert statuses == {"PASS", "BLOCKED"}


def test_defect_summary_sql_exposes_material_rules(tmp_path):
    path = tmp_path / "dq.sqlite"
    process(sample_corrupt(), path)

    with sqlite3.connect(path) as connection:
        rows = connection.execute(_sql("20_defect_summary.sql")).fetchall()

    assert rows
    assert {row[1] for row in rows} >= {"arithmetic_mismatch", "missing_customer"}


def test_quarantine_reconciliation_sql_has_zero_delta(tmp_path):
    path = tmp_path / "dq.sqlite"
    process(sample_corrupt(), path)

    with sqlite3.connect(path) as connection:
        rows = connection.execute(_sql("30_quarantine_reconciliation.sql")).fetchall()

    assert rows
    assert all(row[-1] == 0 for row in rows)
