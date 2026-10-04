from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import asdict
from pathlib import Path

from .core import Transaction, partition


def canonical_source(rows: list[Transaction]) -> str:
    payload = [asdict(row) for row in rows]
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def run_id(rows: list[Transaction]) -> str:
    return hashlib.sha256(canonical_source(rows).encode("utf-8")).hexdigest()[:16]


def process(rows: list[Transaction], database_path: str | Path) -> dict[str, object]:
    accepted, quarantined, defects = partition(rows)
    identifier = run_id(rows)

    connection = sqlite3.connect(database_path)
    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS dq_runs(
                run_id TEXT PRIMARY KEY,
                source_rows INTEGER NOT NULL,
                accepted_rows INTEGER NOT NULL,
                quarantined_rows INTEGER NOT NULL,
                defect_count INTEGER NOT NULL,
                status TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS accepted_rows(
                run_id TEXT NOT NULL,
                row_number INTEGER NOT NULL,
                transaction_json TEXT NOT NULL,
                PRIMARY KEY(run_id, row_number)
            );
            CREATE TABLE IF NOT EXISTS quarantine_rows(
                run_id TEXT NOT NULL,
                row_number INTEGER NOT NULL,
                transaction_json TEXT NOT NULL,
                PRIMARY KEY(run_id, row_number)
            );
            CREATE TABLE IF NOT EXISTS defect_evidence(
                run_id TEXT NOT NULL,
                defect_number INTEGER NOT NULL,
                transaction_id TEXT NOT NULL,
                rule TEXT NOT NULL,
                severity TEXT NOT NULL,
                PRIMARY KEY(run_id, defect_number)
            );
            """
        )
        connection.execute("DELETE FROM accepted_rows WHERE run_id = ?", (identifier,))
        connection.execute("DELETE FROM quarantine_rows WHERE run_id = ?", (identifier,))
        connection.execute("DELETE FROM defect_evidence WHERE run_id = ?", (identifier,))

        connection.executemany(
            "INSERT INTO accepted_rows VALUES (?, ?, ?)",
            [
                (identifier, index, json.dumps(asdict(row), sort_keys=True))
                for index, row in enumerate(accepted)
            ],
        )
        connection.executemany(
            "INSERT INTO quarantine_rows VALUES (?, ?, ?)",
            [
                (identifier, index, json.dumps(asdict(row), sort_keys=True))
                for index, row in enumerate(quarantined)
            ],
        )
        connection.executemany(
            "INSERT INTO defect_evidence VALUES (?, ?, ?, ?, ?)",
            [
                (identifier, index, defect.transaction_id, defect.rule, defect.severity)
                for index, defect in enumerate(defects)
            ],
        )

        status = "PASS" if not quarantined else "BLOCKED"
        connection.execute(
            """
            INSERT INTO dq_runs VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(run_id) DO UPDATE SET
                source_rows=excluded.source_rows,
                accepted_rows=excluded.accepted_rows,
                quarantined_rows=excluded.quarantined_rows,
                defect_count=excluded.defect_count,
                status=excluded.status
            """,
            (identifier, len(rows), len(accepted), len(quarantined), len(defects), status),
        )
        connection.commit()

        persisted = connection.execute(
            """
            SELECT source_rows, accepted_rows, quarantined_rows, defect_count, status
            FROM dq_runs WHERE run_id = ?
            """,
            (identifier,),
        ).fetchone()
        if persisted[0] != persisted[1] + persisted[2]:
            raise ValueError("persisted partition reconciliation failed")

        return {
            "run_id": identifier,
            "source_rows": persisted[0],
            "accepted_rows": persisted[1],
            "quarantined_rows": persisted[2],
            "defect_count": persisted[3],
            "status": persisted[4],
            "defects": [asdict(defect) for defect in defects],
        }
    finally:
        connection.close()


def sample_corrupt() -> list[Transaction]:
    return [
        Transaction("T001", "C001", 2, 40.0, 80.0, "paid"),
        Transaction("T002", "C002", 2, 50.0, 20.0, "paid"),
        Transaction("T003", "", 1, 10.0, 10.0, "pending"),
    ]
