# Output schema

Guarded file. The model returns `{"<items>": [...]}`; one input can yield several items. Each item is one of the types below, with every field present and `null` when unknown.

| Type | Fields |
|---|---|
| <type> | <field>, <field> |

## Validated in code, not by the schema

- <e.g. amounts are positive; currency is a valid ISO 4217 code; dates are real and in a sensible window>
- Enum values are compared case-insensitively.
- Refusals, truncated output or anything that fails validation becomes "needs confirmation", never saved data.

## High-stakes fields

Fields with near-zero error tolerance, reported separately in every eval: <e.g. amount, recipient, visibility>.
