# Lightweight DPIA

Research-based template, not legal advice. Done before the first outside user; signed by the human.

## Why a DPIA

Criteria met (two or more generally require one): <e.g. highly personal or financial data; innovative technology such as LLM processing; special-category data; large scale; vulnerable people>.

## Description

What is processed, how, by whom, and the data flow from input to storage, models, third parties and deletion.

## Necessity and proportionality

- Minimisation: what the model receives and what it never receives.
- Retention per data class.
- Rights: access, export, erasure, including shared data.

## Risks and measures

| Risk | Likelihood | Severity | Measure | Residual |
|---|---|---|---|---|
| One user sees another user.s data | | high | authorisation matrix tests, RLS | |
| Provider retains or reuses content | | | API tier, DPA, short retention, EU region | |
| Sensitive data sent to the model without consent | | high | consent, opt-out per item, excluded categories | |
| Data loss | | high | PITR, off-account copy, monthly restore test | |
| AI output wrong on a high-stakes field | | medium | confirmation step, eval thresholds | |

## Decision

- Approved by: <name> on <YYYY-MM-DD>
- Review when: a new data class, processor, AI feature or user group is added.
