<div align="center">

# Data Quality Rescue

### Fail-closed triage, quarantine and reconciliation for broken analytical feeds.

**Pretoria BI — Data · Intelligence · Performance**

</div>

---

## Management question

> **Can downstream reporting remain open, or must the feed be quarantined before a wrong decision reaches management?**

**All data and entities are synthetic. No client result or realised ROI is claimed.**

---

## What this repository proves

- Duplicate-key control
- Missing-key/domain checks
- Arithmetic reconciliation
- Severity classification
- Fail-closed release gate

The objective is not to inflate a portfolio with screenshots. The repository has an executable happy path and deliberately corrupted states that must be rejected.

## Evidence chain

```text
SIGNAL → CONTRACT → VALIDATION → ANALYSIS → DECISION RULE → ACTION OWNER → FOLLOW-UP
```

## Run locally

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest -q
python -m dq_rescue.cli smoke
python -m dq_rescue.cli reverse-test
```

## Repository map

```text
data-quality-rescue/
├── .github/workflows/ci.yml
├── config/
├── docs/
├── sql/
├── src/dq_rescue/
├── tests/
├── Dockerfile
├── Makefile
├── pyproject.toml
└── README.md
```

## Proof boundary

Implemented evidence is separated from future production claims. See `docs/proof_matrix.md` and `docs/limitations.md`. Thresholds in this synthetic case are examples to demonstrate governance and must be calibrated before real deployment.

---

<div align="center">

**Pretoria BI**  
**Understand · Decide · Act · Measure**

</div>
