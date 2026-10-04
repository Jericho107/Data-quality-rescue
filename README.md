<div align="center">

# Data Quality Rescue

### Detection · Quarantine · Evidence · Release Gate · Recovery

**Python · SQLite · Data Contracts · Data Quality · CI**

**Pretoria BI — Data · Intelligence · Performance**

</div>

---

## Operational question

> **Can downstream reporting be released safely, or must defective rows be quarantined until the source is corrected?**

This repository implements an auditable rescue workflow for broken analytical feeds.

## Control flow

```text
SOURCE BATCH
    ↓
RULE INSPECTION
    ↓
ACCEPTED ──────┐
QUARANTINE ────┼→ PARTITION RECONCILIATION
DEFECTS ───────┘
    ↓
PERSISTED RUN EVIDENCE
    ↓
PASS / BLOCKED RELEASE GATE
    ↓
CORRECT SOURCE → REPROCESS → RECOVERY
```

Each source state receives a deterministic run identifier. The evidence store persists:

- source row count;
- accepted row count;
- quarantined row count;
- defect count and severity/rule;
- release status;
- accepted and quarantine row payloads.

The invariant is explicit:

`source_rows = accepted_rows + quarantined_rows`.

## Failure and recovery scenario

The synthetic incident contains both an arithmetic mismatch and a missing customer. The run must be **BLOCKED** and the affected rows quarantined. A corrected clean source is then processed and must return **PASS**, while the previous incident remains available as historical evidence.

## Evidence report

```bash
python -m dq_rescue.cli report
```

Produces:

- `output/dq_evidence.sqlite`
- `output/data_quality_rescue.html`

## Run locally

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest -q
python -m dq_rescue.cli smoke
python -m dq_rescue.cli report
python -m dq_rescue.cli reverse-test
```

All data are synthetic. Production alerting, orchestration, lineage platforms and incident integrations are outside the current implementation.

---

**Pretoria BI — Understand · Decide · Act · Measure**
