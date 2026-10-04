SELECT
    run_id,
    source_rows,
    accepted_rows,
    quarantined_rows,
    defect_count,
    source_rows - accepted_rows - quarantined_rows AS partition_delta,
    CASE
        WHEN source_rows = accepted_rows + quarantined_rows
         AND quarantined_rows = 0
         AND status = 'PASS'
        THEN 'PASS'
        WHEN source_rows = accepted_rows + quarantined_rows
         AND quarantined_rows > 0
         AND status = 'BLOCKED'
        THEN 'BLOCKED'
        ELSE 'INVALID'
    END AS validated_release_status
FROM dq_runs
ORDER BY run_id;
