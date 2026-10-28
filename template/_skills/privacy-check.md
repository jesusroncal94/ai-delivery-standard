---
name: privacy-check
description: Review the product against its privacy records and prepare the documents needed before anyone other than the builders uses it. Use before the first outside user, when adding a data class, processor or AI feature, and when a provider changes its terms.
---

# privacy-check

Research-based checks, not legal advice. The human signs.

1. Read `docs/privacy/record-of-processing.md`, `provider-log.md` and `dpia.md`, and the phase in `docs/product/brief.md`.
2. Trace each data flow in the code: input, storage, models and other third parties, logs, analytics, backups, deletion. Report any flow missing from the record of processing.
3. Check the rules in `AGENTS.md`: minimisation towards the model, no prompts or contents in logs, raw audio deleted, private by default.
4. For each provider, check the current official terms and fill in the provider log: account tier, DPA, training on data, retention, region, transfer basis, date checked. Flag consumer or free tiers.
5. Check special-category handling: consent, how users keep sensitive content away from AI or third parties.
6. Check rights flows: export and account deletion, including shared data and copies at providers.
7. Check transparency: privacy notice, AI notice, and the app-store consent before sending personal data to third-party AI.
8. Draft or update the DPIA risks and measures.
9. Stop. The human reviews, decides the phase and signs the DPIA.
