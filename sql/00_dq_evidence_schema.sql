CREATE TABLE IF NOT EXISTS dq_runs (
    run_id TEXT PRIMARY KEY,
    source_rows INTEGER NOT NULL,
    accepted_rows INTEGER NOT NULL,
    quarantined_rows INTEGER NOT NULL,
    defect_count INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('PASS', 'BLOCKED'))
);

CREATE TABLE IF NOT EXISTS accepted_rows (
    run_id TEXT NOT NULL,
    row_number INTEGER NOT NULL,
    transaction_json TEXT NOT NULL,
    PRIMARY KEY(run_id, row_number)
);

CREATE TABLE IF NOT EXISTS quarantine_rows (
    run_id TEXT NOT NULL,
    row_number INTEGER NOT NULL,
    transaction_json TEXT NOT NULL,
    PRIMARY KEY(run_id, row_number)
);

CREATE TABLE IF NOT EXISTS defect_evidence (
    run_id TEXT NOT NULL,
    defect_number INTEGER NOT NULL,
    transaction_id TEXT NOT NULL,
    rule TEXT NOT NULL,
    severity TEXT NOT NULL,
    PRIMARY KEY(run_id, defect_number)
);
