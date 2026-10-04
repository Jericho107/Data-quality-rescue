WITH accepted AS (
    SELECT run_id, COUNT(*) AS accepted_rows
    FROM accepted_rows
    GROUP BY run_id
),
quarantined AS (
    SELECT run_id, COUNT(*) AS quarantined_rows
    FROM quarantine_rows
    GROUP BY run_id
)
SELECT
    r.run_id,
    r.source_rows,
    COALESCE(a.accepted_rows, 0) AS persisted_accepted_rows,
    COALESCE(q.quarantined_rows, 0) AS persisted_quarantined_rows,
    r.source_rows
        - COALESCE(a.accepted_rows, 0)
        - COALESCE(q.quarantined_rows, 0) AS row_delta
FROM dq_runs r
LEFT JOIN accepted a USING (run_id)
LEFT JOIN quarantined q USING (run_id)
ORDER BY r.run_id;
