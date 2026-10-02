# Architecture

```text
synthetic source / input
        ↓
contract + grain
        ↓
quality / reconciliation
        ↓
metric or model layer
        ↓
decision rule
        ↓
owner + action + follow-up metric
        ↓
measured impact (outside synthetic proof)
```

## Design constraints

- Material defects fail closed.
- Natural grain is explicit before aggregation.
- Ratios are recomputed from additive components.
- Tests cover both nominal and deliberately corrupted states.
- Synthetic outputs prove implementation behaviour, not client ROI.
