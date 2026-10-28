# Eval report <YYYY-MM-DD>

- Change tested: <prompt, model, schema or validator change>
- Model and prompt version: <...>
- Golden set: <N cases, batches>

## Segmentation

Inputs with the right number of records: <x / N>.

## Type per record

| Type | Precision | Recall | F1 | Support |
|---|---|---|---|---|

Macro-F1: <...>. Confusion matrix attached.

## Fields

| Field | Exact match after normalisation | Notes |
|---|---|---|
| <high-stakes field> | | near-zero tolerance |
| <high-stakes field> | | near-zero tolerance |
| <field> | | |

## Thresholds

Share auto-accepted and precision at that share, per field.

## Decision

Ship | do not ship, and why. Previous report: <link>.
