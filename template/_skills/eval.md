---
name: eval
description: Build, extend or run the golden set for the AI extraction or classification and write an eval report. Use when changing prompts, models, the output schema or validators, before switching provider, when a deprecation is announced, or to turn user corrections into new cases.
---

# eval

1. Read `evals/README.md` and `evals/schema.md`.
2. To extend the golden set: take consented user corrections or new real inputs, pseudonymise them, and add a new batch file in `evals/golden/`. Stratify so rare record types appear. Mark cases for double labelling; the human labels or adjudicates them. Never edit existing batches.
3. To run: execute the model pipeline on every golden case with the version under test, then measure separately:
   - segmentation: right number of records per input;
   - type per record: per-class precision, recall and F1, macro-F1 and the confusion matrix;
   - fields: exact match after normalisation, with the high-stakes fields in `evals/schema.md` reported apart.
4. Derive auto-accept thresholds per field from agreement across samples or from validators, never from the model's stated confidence. Report the share auto-accepted and the precision at that share.
5. Compare with the previous report and write `evals/reports/<YYYY-MM-DD>.md` from `report-template.md`.
6. Stop. The human decides whether the change ships and approves any threshold change.
