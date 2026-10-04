SELECT
    run_id,
    rule,
    severity,
    COUNT(*) AS defect_count
FROM defect_evidence
GROUP BY run_id, rule, severity
ORDER BY
    run_id,
    CASE severity
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        ELSE 4
    END,
    defect_count DESC,
    rule;
