# Validation Matrix

| Claim | Executable evidence | Failure path | Status |
|---|---|---|---|
| Critical data rules are explicit | `core.inspect` | arithmetic, key, customer, quantity, price, status defects | implemented |
| Unsafe rows are quarantined | `core.partition` | material defect injection | implemented |
| Source partition reconciles exactly | accepted + quarantine = source | reconciliation assertion | implemented |
| Release status is fail-closed | `pipeline.process` | corrupt batch returns BLOCKED | implemented |
| Evidence is persisted by deterministic source state | SQLite run/evidence tables | identical rerun | implemented |
| Incident history survives recovery | separate deterministic run IDs | corrupt then clean source | implemented |
| Corrected source can recover to PASS | reprocess clean sample | recovery reverse test | implemented |
| Human-readable incident evidence is generated | `reporting.rescue_report_html` | CI artefact check | implemented |
| CI validates detection, quarantine and recovery | GitHub Actions + reverse-test CLI | controlled corrupt batch | implemented |
| Production incident response | no external orchestration/integration | not applicable | not claimed |

## Review principle

Rows are never silently dropped. Every source row must be accounted for as either accepted or quarantined, with the reason for quarantine persisted.
