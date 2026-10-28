# Evals

The model pipeline is judged on our own data, never on public benchmarks or the model's stated confidence.

## Layout

- [`schema.md`](schema.md): the records schema the model must return (guarded).
- `golden/`: labelled cases from real, consented inputs, one file per batch (append-only).
- `reports/`: one report per run, from [`report-template.md`](report-template.md).

## Golden cases

Each case is one JSON line: `{"id", "input_type", "input", "expected": {"records": [...]}, "labelled_by", "labelled_on"}`. Inputs are pseudonymised. Start with 20–50 cases from real failures and grow from user corrections. Stratify so rare record types appear, and double-label a subset to check agreement.

## When to run

- Every change to prompts, models, the schema or the validators.
- Before switching model or provider, and when a deprecation is announced.
