# Metrics

One record per month, `metrics/YYYY-MM.md`, built from Git and PR history and from agent usage (OpenTelemetry or session transcripts via `ads usage`). Read trends over 8–12 weeks; never rank people by tokens.

| Metric | Definition |
|---|---|
| Cost per accepted change | List-price-equivalent agent spend for the month divided by merged PRs not reverted or hotfixed within 14 days |
| First-pass acceptance | Share of agent PRs merged without a change-request cycle or a follow-up fix before merge |
| Rework rate | Share of accepted changes followed by a revert or hotfix within 14 days |
| Review latency | Median time from PR opened to merge |
| Context health | P50 and P90 context per call; share of sessions averaging over 200k; fixed floor |

## Record template

```
# YYYY-MM

- Accepted changes:
- Agent spend (tokens by type, list-price equivalent):
- Cost per accepted change:
- First-pass acceptance:
- Rework rate:
- Review latency (median):
- Context per call P50 / P90; sessions over 200k:
- What changes next month:
```
