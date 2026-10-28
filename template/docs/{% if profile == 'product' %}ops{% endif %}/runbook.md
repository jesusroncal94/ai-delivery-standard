# Runbook

One page. The human runs it; agents may propose changes.

## Pages (only two)

1. External synthetic check fails: <URL checked, from where, how often>.
2. Error rate above <threshold> for <window>.

Everything else goes to a daily digest.

## Incident steps

1. Stop the harm: <feature flags, kill switch, maintenance mode>.
2. Find out whether user data was exposed, lost or altered.
3. If personal data was affected, follow the breach path of the applicable law and record the decision either way (with the `eu-personal-data` module: assess within 72 hours whether to notify the supervisory authority).
4. Restore from backup if needed: see [restore-log.md](restore-log.md).
5. Blameless postmortem for any data loss or any data visible to someone who should not see it.

## Spend limits (paid APIs)

- Provider hard cap: <amount>. Production in its own project or workspace.
- Per-user quotas: <calls per day, payload size>.
- When the cap is hit: degrade gracefully (<e.g. queue the work>); no retry loop.

## Contacts and access

- Who holds production credentials: the human only.
- Where recovery codes are kept: <location>.
