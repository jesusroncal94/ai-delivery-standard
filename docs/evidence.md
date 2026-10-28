# Evidence behind the standard

What the standard rests on, as of 2026-10-28. Each finding names its source, the source type and the date; "abstract only" means the full text was not read. Rules marked **inference** in [STANDARD.md](../STANDARD.md) are syntheses of these findings, not measured results. The research was run as a living-review investigation with graded sources and dated claims; this page is its public summary.

## The short version

1. **Cost follows context per call, not output.** Every agent turn re-sends the whole conversation. Long sessions, not long answers, consume the budget.
2. **Instructions are advisory; checks are not.** Short instruction files with prohibitions help a little; what must hold has to be a hook, a CI check or a ruleset.
3. **Validation needs an oracle and an approval outside the agent.** Agents pass the tests they can see and rarely test what they change.
4. **A standard without an update path drifts.** Only Copier updates repositories that were already generated, and no existing checker covers agent-harness files.
5. **Measure accepted changes, not tokens.**

## A developer's own sessions (internal evidence)

An audit of one developer's portfolio (19 projects, 38 Claude Code sessions from 2026-09-15 to 2026-10-28) measured with `ads usage`. It is a single-developer sample: it shows where to act, not what works in general.

- 9,868 model calls; cache reads were **97.9%** of all input tokens.
- Context per call grew with session length. The 19 sessions that averaged more than 200,000 tokens per call carried **95.5%** of all cache reads; the five longest ran at 400,000–430,000 tokens per call. Short sessions handed off with a written brief stayed between 90,000 and 200,000 tokens per call and each ended in a merged PR.
- A fork of a long session produced a second transcript of almost the same size: a fork copies the parent's history.
- The fixed context before any work was about 76,000 tokens, 21,800 of them MCP tool definitions from connectors loaded into every project.
- Four ways of working had grown independently (a product starter kit, a structured-prompt method, a research library and ad-hoc repositories). The mature ones converged on the same four elements: a short rules file, explicit human gates, a machine-checkable definition of done and a CI check. Shared conventions lived only in the agent's per-user memory.

## Context

| Finding | Source |
|---|---|
| Context files raise cost by more than 20% and help only with minimal, non-inferable content. | Gloaguen et al., [arXiv 2602.11988](https://arxiv.org/abs/2602.11988), preprint, 2026-02-12 |
| In more than 5,000 Claude Code runs, random rules helped as much as curated ones; only negative constraints helped individually. | "Guardrails Beat Guidance", [arXiv 2604.11088](https://arxiv.org/abs/2604.11088), preprint, 2026-04-13, abstract only |
| An AGENTS.md went with 28.6% lower runtime and 16.6% fewer output tokens at comparable completion (10 repos, 124 PRs). | Lulla et al., [arXiv 2601.20404](https://arxiv.org/abs/2601.20404), preprint, 2026-01-28, abstract only |
| Claude Code: target under 200 lines per CLAUDE.md; imports do not reduce context; ignored rules belong in hooks. | [Claude Code: memory](https://code.claude.com/docs/en/memory), vendor docs, read 2026-10-28 |
| Codex concatenates AGENTS.md files up to `project_doc_max_bytes`, 32 KiB by default. | [Codex: AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md), vendor docs, read 2026-10-28 |
| Agent Skills: about 100 tokens of metadata per skill, body under 5,000 tokens and 500 lines, description at most 1,024 characters. AGENTS.md sets no size or version. | [Agent Skills specification](https://agentskills.io/specification); [agents.md](https://agents.md), read 2026-10-28 |
| After compaction Claude Code re-reads up to five recent files but returns files over 5,000 tokens as a bare path; skills are re-attached up to 5,000 tokens each. | [Claude Code: context window](https://code.claude.com/docs/en/context-window), vendor docs, read 2026-10-28 |
| Five MCP servers with 58 tools cost about 55,000 tokens of definitions; tool search cut that by 85%. Defer beyond 10,000 tokens or 10 tools. | [Anthropic: advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use), vendor engineering post, 2025-11-24 (internal evals) |
| Every one of 18 models scored better on focused ~300-token prompts than on ~113,000-token ones. | [Chroma: Context Rot](https://www.trychroma.com/research/context-rot), technical report, 2025-07-14 |
| Agent memory is per user: Claude loads 200 lines or 25 KB of MEMORY.md; Codex memories are off by default; Copilot memories expire after 28 days. | [Claude Code: memory](https://code.claude.com/docs/en/memory); [Codex: memories](https://learn.chatgpt.com/docs/customization/memories); [Copilot Memory](https://docs.github.com/en/copilot/concepts/agents/copilot-memory), read 2026-10-28 |

## Sessions and cost

| Finding | Source |
|---|---|
| Claude Code re-sends the full context with every request, cached as a prefix; a model switch, a tool change, `/compact` or an idle gap past the cache lifetime rebuilds it. The cache lasts about one hour on a subscription and five minutes on an API key or for subagents. | [Claude Code: prompt caching](https://code.claude.com/docs/en/prompt-caching.md), vendor docs, read 2026-10-28 |
| `/clear` between unrelated tasks; restart after two failed corrections; a fresh session costs less when the history is not needed. Codex: one chat per coherent unit of work. | [Claude Code: best practices](https://code.claude.com/docs/en/best-practices); [Codex: best practices](https://learn.chatgpt.com/guides/best-practices), read 2026-10-28 |
| Average Claude Code spend about $13 per developer per active day; high spend traced to long uncleared sessions and the top model left as default. The built-in Explore subagent inherits the main model. | [Claude Code: costs](https://code.claude.com/docs/en/costs); [subagents](https://code.claude.com/docs/en/sub-agents), read 2026-10-28 (statistic undated) |
| Compression cut tool-output tokens 38.4% but raised billed cost 6.8%; harnesses differed up to 40-fold in tokens per solved task at similar pass rates. | [arXiv 2607.12161](https://arxiv.org/abs/2607.12161); [arXiv 2607.22585](https://arxiv.org/abs/2607.22585), preprints, 2026, abstracts only |
| Agents use about 4× the tokens of chat and multi-agent systems about 15×; Claude Code agent teams about 7×. | [Anthropic: multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system), 2025-06-13; [Claude Code: costs](https://code.claude.com/docs/en/costs) |
| Parallel agent PRs conflicted textually in 19.8% (same agent) to 41.7% (different agents) of replayed merges. | [arXiv 2607.04697](https://arxiv.org/abs/2607.04697), preprint, 2026-07-07, abstract only |
| The 50% time horizon of a frontier model was about 320 minutes in early 2026, doubling every ~131 days; test-passing agent PRs still needed human work to be mergeable. | [METR: Time Horizon 1.1](https://metr.org/blog/2026-01-29-time-horizon-1-1/), 2026-01-29; [METR research update](https://metr.org/blog/2025-08-12-research-update-towards-reconciling-slowdown-with-time-horizons/), 2025-08-13 |
| Unattended agents: read-only agent jobs with safe outputs; agent-prefixed branches; trigger payloads are untrusted; turn limits and timeouts. | [GitHub Agentic Workflows](https://github.github.com/gh-aw/introduction/architecture/); [Claude Code: scheduled tasks](https://code.claude.com/docs/en/routines); [Claude Code: GitHub Actions](https://code.claude.com/docs/en/github-actions), read 2026-10-28 |

## Validation

| Finding | Source |
|---|---|
| Only 49.6% of agent PRs that change code under test also change tests; in 64.8% of Python PRs no changed line is executed by any test. | [arXiv 2607.18057](https://arxiv.org/html/2607.18057), preprint, 2026-07-20 |
| Agents pass visible tests while failing held-out ones, a gap that grows with code size. | SpecBench, [arXiv 2605.21384](https://arxiv.org/abs/2605.21384), preprint, 2026-05-20, abstract only |
| TDD-style instructions raised regressions; a code-to-test dependency map cut them. Telling agents to write more tests did not change outcomes. | [arXiv 2603.17973](https://arxiv.org/abs/2603.17973); [arXiv 2602.07900](https://arxiv.org/abs/2602.07900), preprints, 2026, abstracts only |
| Spec-driven development raised planning and review costs; specs decayed; no tool publishes outcome data. | [arXiv 2608.25202](https://arxiv.org/abs/2608.25202), preprint, 2026-08-25, abstract only; [github/spec-kit](https://github.com/github/spec-kit) |
| LLMs invent package names in 5.2% (commercial) to 21.7% (open) of cases. | Spracklen et al., [arXiv 2406.10279](https://arxiv.org/abs/2406.10279), peer-reviewed at USENIX Security 2025 |
| A requester's approval of a Copilot PR does not count towards required reviews; rulesets can require checks, scanning, path restrictions and coverage. | [GitHub Docs: review Copilot PRs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/review-copilot-prs); [available rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets), read 2026-10-28 |
| AI code review: 38.7% of comments led to changes in a 12-month industrial deployment. | [arXiv 2601.01129](https://arxiv.org/abs/2601.01129), industry preprint, 2026-01-03, abstract only |
| AI-generated code is not a shortcut around review, testing and static analysis. | [OpenSSF guide for AI code assistants](https://best.openssf.org/Security-Focused-Guide-for-AI-Code-Assistant-Instructions), 2025-08-01 |

## Packaging and governance

| Finding | Source |
|---|---|
| `copier update` replays the template diff on generated projects; `copier check-update` exits 2 when an update exists; migrations run on update. | [Copier: updating](https://copier.readthedocs.io/en/stable/updating/); [configuring](https://copier.readthedocs.io/en/stable/configuring/), read 2026-10-28 |
| GitHub template repositories and Backstage templates generate once; cruft adds updates to Cookiecutter. | [GitHub Docs](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository); [Backstage](https://backstage.io/docs/features/software-templates/); [cruft](https://cruft.github.io/cruft/) |
| OpenSSF Scorecard and Allstar do not check agent-harness files; Repolinter was archived on 2026-02-06. | [Scorecard checks](https://github.com/ossf/scorecard/blob/main/docs/checks.md); [Allstar](https://github.com/ossf/allstar); [Repolinter](https://github.com/todogroup/repolinter) |
| Cumulative levels: OpenSSF badge (passing, silver, gold), SLSA tracks and levels, OSPS Baseline MUST-only releases. | [bestpractices.dev](https://www.bestpractices.dev/en/criteria); [slsa.dev](https://slsa.dev/spec/v1.0/levels); [baseline.openssf.org](https://baseline.openssf.org/) |
| MCP versions by date with a 12-month (or 90-day expedited) deprecation window; AGENTS.md and Agent Skills publish no version. | [MCP: versioning](https://modelcontextprotocol.io/specification/versioning), 2026-07-28 |
| No skills directory is read by every agent: `.agents/skills` by Codex, Copilot, Cursor and Gemini CLI; `.claude/skills` by Claude Code, Copilot and Cursor. Claude Code imports `@AGENTS.md` and recommends that over symlinks on Windows. | Vendor docs for [Codex](https://learn.chatgpt.com/docs/build-skills), [Copilot](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills), [Cursor](https://cursor.com/docs/context/skills), [Claude Code](https://code.claude.com/docs/en/skills), read 2026-10-28 |
| Golden paths went stale without fleet-wide change management; layered instruction files drift and go stale. | [Spotify, 2020-08-17](https://engineering.atspotify.com/2020/8/how-we-use-golden-paths-to-solve-fragmentation-in-our-software-ecosystem); [Spotify, 2023-04-18](https://engineering.atspotify.com/2023/4/spotifys-shift-to-a-fleet-first-mindset-part-1); [Claude Code: large codebases](https://code.claude.com/docs/en/large-codebases.md) |
| Harness = guides plus sensors with a steering loop; shared templates drift from upstream. | Böckeler, [Harness engineering](https://martinfowler.com/articles/harness-engineering.html), 2026-04-02 |

## Metrics

| Finding | Source |
|---|---|
| DORA's five metrics include deployment rework rate. | [DORA metrics guide](https://dora.dev/guides/dora-metrics/), updated 2026-01-05 |
| Do not rank developers by tokens; measure cost per accepted change and rework. | [DORA: finding balance in the era of tokenmaxxing](https://dora.dev/insights/finding-balance-in-the-era-of-tokenmaxxing/), 2026-06-02 |
| Coding throughput as a productivity measure is on Caution; use first-pass acceptance rate. | [Thoughtworks Technology Radar](https://www.thoughtworks.com/radar/techniques/coding-throughput-as-a-measure-of-productivity), 2026-04-15 |
| Claude Code exports token usage by type, model and repository through OpenTelemetry; cost figures are client-side estimates. | [Claude Code: monitoring](https://code.claude.com/docs/en/monitoring-usage), read 2026-10-28 |

## What remains open

- Whether handing off at 200,000 tokens per call lowers cost per accepted change for tightly coupled work.
- Whether a mid-tier default model holds first-pass acceptance for typical product, site and research work.
- Whether a fresh-context review plus required CI substitutes for a second human reviewer when working alone.
- No peer-reviewed study measures instruction-file length, session length or spec-driven development against outcomes; most 2026 studies above were read at abstract level.
- Numeric plan allowances for subscription plans are not published.

## Review triggers

The standard is reviewed, and a new version released if needed, when:

- AGENTS.md or Agent Skills publish a version, a conformance specification or a deprecation policy, or one skills directory becomes readable by every major agent;
- a vendor changes how instruction files, skills, memory, subagents or tools load into context, or publishes plan allowances;
- a controlled study measures token cost per task across harness designs, session lengths, or spec-driven and test-driven development with agents;
- METR publishes a new time-horizon measurement;
- and in any case on 2027-01-28, three months after the first adoption.
