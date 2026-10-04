import sqlite3

from dq_rescue.core import sample
from dq_rescue.pipeline import process, sample_corrupt


def test_corrupt_run_is_quarantined_and_reconciled(tmp_path):
    path = tmp_path / "dq.sqlite"
    result = process(sample_corrupt(), path)
    assert result["status"] == "BLOCKED"
    assert result["source_rows"] == result["accepted_rows"] + result["quarantined_rows"]
    assert result["quarantined_rows"] == 2


def test_clean_run_releases_and_is_idempotent(tmp_path):
    path = tmp_path / "dq.sqlite"
    first = process(sample(), path)
    second = process(sample(), path)
    assert first == second
    assert first["status"] == "PASS"
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM dq_runs").fetchone()[0] == 1
