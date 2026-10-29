# AI delivery standard — version 1.1.0

This document is normative. **MUST** and **MUST NOT** are checked by `ads check` (the rule ID is given) or by a human gate; **SHOULD** is expected unless the project records why not. Numeric limits are policy defaults dated 2026-10-28, chosen from vendor limits and measurements listed in [docs/evidence.md](docs/evidence.md); they are reviewed on the triggers in [docs/evidence.md#review-triggers](docs/evidence.md#review-triggers).

## 1. Layers

| Layer | Owns | Lives in | Enforced by |
|---|---|---|---|
| Portfolio | Shared conventions, the registry of projects with profile and target level, the standard's version, routing defaults, budgets | This repository plus a registry file (`portfolio.yaml`) kept by the team | `ads portfolio`; scheduled `copier check-update` in every repository |
| Project | `AGENTS.md`, adapters, skills, acceptance list, progress log, specs, ADRs, CI, guarded paths, MCP config, profile files | Each repository, rendered by Copier and upgraded by `copier update` | `ads check` in CI, hooks, deny rules, branch protection or rulesets |
| Session | One deliverable, a brief, a fixed model and effort, a context budget, a handoff | The agent session, `progress.md` and the spec it starts from | Session hook, the `handoff` skill, `ads usage` |

## 2. Profiles

A project has exactly one profile. Profiles add files and rules; they never remove core ones.

| Profile | For | Adds | Default level |
|---|---|---|---|
| `product` | Apps and services with users | `docs/product/` (brief, assumptions), `docs/ops/` (runbook, restore log), `discover` skill, human gates for auth, personal data, production and AI changes; optional modules `multi-user`, `eu-personal-data`, `ai-extraction` | L3 |
| `service` | APIs, libraries, CLIs and internal tools | `CHANGELOG.md` with semantic versioning; compatibility and migration rules | L2 |
| `research` | Evidence libraries and analysis repositories | Source registration, absolute dates and frozen reports | L2 |
| `site` | Static and content sites | Checks against the production build, performance budget, layout check | L2 |
| `demo` | Samples and experiments that are not maintained | README states "demo, not maintained" | L1 |

## 3. Conformance levels

Levels are cumulative: L2 includes L1, L3 includes L2. `ads check` reports the highest level whose rules all pass; a project conforms when that level reaches its target.

### L1 baseline

| Rule | Requirement |
|---|---|
| L1-GIT | The project MUST be a Git repository. |
| L1-REMOTE | It MUST have a remote, unless `local_only` is set on purpose. |
| L1-README | `README.md` MUST say what the project is (demos: that it is a demo, rule L1-DEMO). |
| L1-ANSWERS | `.copier-answers.yml` MUST record the standard's version, profile and level. |
| C1-AGENTS | `AGENTS.md` MUST exist and have at most **200 lines**. |
| C1-CHAIN | The always-loaded instruction files (`AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`) MUST total at most **32 KiB**. |
| L1-SECTIONS | `AGENTS.md` MUST have the sections Commands, Definition of done, Prohibitions, Portfolio conventions and Where things live. |
| L1-CLAUDE | With the Claude Code adapter, `CLAUDE.md` MUST import `@AGENTS.md` and have at most 20 lines. |
| L1-CHECK | One check command MUST exist as `scripts/check.sh` (and `scripts/check.ps1` on Windows). |
| L1-GITIGNORE | `.gitignore` MUST exclude `.env` files. |
| L1-SECRETS | Secret scanning (gitleaks) MUST run in CI or, for local-only projects, in the check command. |
| L1-DENY | With the Claude Code adapter, agents MUST be denied `git push`, `gh pr merge` and reading `.env`. |
| L1-DIAGRAMS | With the `diagrams` capability, every row of the manifest in `docs/design/README.md` MUST link an existing SVG, and every SVG in `docs/diagrams/` MUST have a row and MUST NOT contain `@font-face` or `<script>`. |

### L2 gated

| Rule | Requirement |
|---|---|
| L2-CI | Unless local-only, CI MUST run the check and `ads check` on every pull request, as required checks on a protected `main`. |
| L2-UPDATE | Unless local-only, CI MUST run `copier check-update` on a schedule. |
| L2-GUARDED | `.standard/guarded-paths.txt` MUST protect `AGENTS.md`, `.github/*` and `scripts/check-gates.sh`; the hook blocks agent edits and `check-gates.sh` blocks the PR without the `human-approved` label. |
| L2-ACCEPTANCE | `acceptance/features.json` MUST list criteria with `id`, `steps` and a boolean `passes`; criteria change only with the human. |
| C6-STATE | `progress.md` MUST exist; it and `acceptance/features.json` MUST stay under **5,000 tokens** each. |
| C6-REFERENCE | No Markdown document SHOULD exceed **25,000 tokens**; split it. Checked as MUST. |
| L2-DOCS | `docs/specs/` and `docs/adr/` MUST exist. |
| L2-SKILLS | The skills `spec`, `build-slice`, `review`, `handoff` and `release` MUST be in `.agents/skills/`. |
| C4-SKILLS | Each skill MUST follow the Agent Skills specification: `name` equal to its folder, a `description` of at most 1,024 characters, only specification fields, at most 500 lines. |
| L2-MIRROR | With the Claude Code adapter, `.claude/skills/` MUST be a byte-identical mirror of `.agents/skills/` (`scripts/sync-skills.sh`). |
| C7-MCP | `.mcp.json` MUST exist and list at most **5** servers. |
| L2-HOOKS | With the Claude Code adapter, a PreToolUse hook MUST run the guarded-paths check. |
| L2-PRODUCT, L2-SERVICE, L2-MODULES | Profile and module files MUST be present. |

### L3 measured

| Rule | Requirement |
|---|---|
| L3-BUDGET | `.standard/budget.yml` MUST declare the weekly budget and the session limits. |
| L3-METRICS | `metrics/README.md` MUST exist and, once the repository is older than 45 days, a monthly `metrics/YYYY-MM.md` record (section 8). |
| L3-REVIEW | `docs/harness-review.md` MUST record a quarterly review of what recurred and which guide or sensor changed. |
| L3-EVALS | Products with the `ai-extraction` module MUST keep an eval set with a pass floor, a baseline and a drift rule; any prompt, model or schema change runs it. |

## 4. Context rules

| ID | Rule |
|---|---|
| C1 | Root `AGENTS.md` at most 200 lines (target 120); whole always-loaded chain at most 32 KiB. |
| C2 | `AGENTS.md` holds only non-inferable commands, gotchas and prohibitions, written as "do not". No directory tours or architecture overviews. |
| C3 | A rule that must always hold is a hook, deny rule, CI check or ruleset, never only prose. |
| C4 | Skills: at most 500 lines and about 5,000 tokens, specification-only frontmatter in the tool-neutral copy, references one level deep. |
| C5 | Nested instruction files and path rules at most 40,000 characters each; a rule that must survive compaction is not path-scoped. |
| C6 | State files under 5,000 tokens; reference documents under 25,000 tokens. |
| C7 | MCP servers enabled per project, not globally; fewer than 20 tools loaded eagerly; a fixed session floor of at most **55,000 tokens**, measured with `/context`. |
| C8 | Test and build scripts print a summary (counts and one line per error) and write details to log files. |
| C9 | Agent memory is per developer and not authoritative; anything a collaborator or another tool needs lives in the repository. |

## 5. Session rules

| ID | Rule |
|---|---|
| S1 | One deliverable per session: one acceptance entry, one spec or one fix. |
| S2 | Start from a written brief; after writing a spec, build in a fresh session. |
| S3 | `/clear` or a new session between unrelated tasks; after two failed corrections, restart with a better prompt. |
| S4 | Hand off when context per call passes **200,000 tokens**: a handoff entry of at most ten lines, then a fresh session. |
| S5 | Do not fork a long session; do not resume after an idle gap longer than the cache lifetime unless the history is needed. |
| S6 | Model and effort are fixed for the session; change them only at session or subagent boundaries. |
| S7 | Subagents are for verbose read-only exploration and independent review, on a small model, returning at most about 2,000 tokens. |
| S8 | Parallel sessions: one writer per worktree, file-disjoint tasks, shared-interface changes serial, full tests after merge. No agent teams by default. |
| S9 | Size a task well below the current agent time horizon; default to work a person would finish in one to two hours. |
| S10 | Unattended agents only after the task works manually: read-only token, agent-prefixed branch, no self-approval, turn, budget and time caps (60 minutes or less). |
| S11 | Close every session by running the check, letting the check set `passes`, appending a progress entry of at most five lines and committing. |

## 6. Cost and routing rules

| ID | Rule |
|---|---|
| R1 | On subscriptions, budget the share of the weekly window and tokens by type; on API or credits, dollars with hard caps and alerts at 50% and 80%. |
| R2 | Default routing: implementation on the mid-tier model at medium effort; the top model for planning, architecture and hard debugging; a small model at low effort for exploration and test-runner subagents. |
| R3 | Never switch the main model mid-session. |
| R4 | Keep a routing rule only if cost per accepted change improves without lowering first-pass acceptance. |
| R5 | Headless and CI agent runs always carry a turn limit, a budget cap and a timeout. |
| R6 | Review usage weekly; trim any skill, MCP server or file that takes 10% of usage or more. |
| R7 | Never rank individuals by tokens; aggregate by project. |

## 7. Human gates

These MUST stay with a human. Agents prepare the change and stop.

| Gate | Mechanism |
|---|---|
| Approve a spec and its acceptance criteria before building | Approval commit; build in a fresh session |
| Change acceptance criteria, guarded paths, CI or the rules | Guarded-paths hook, `check-gates.sh`, `human-approved` label |
| Merge to `main` | Deny rule for agents; required checks; in teams, a second human (the requester's approval does not count) |
| Release or deploy to production | Protected environment with required reviewers |
| Secrets, credentials and production data | No credentials in the agent environment; deny reads of `.env` |
| Irreversible or destructive operations | The agent hands over the command; the human runs it |
| Change a model, prompt version or provider for an AI feature | Eval gate passes, then approval |
| Add a dependency, MCP server, paid service or unattended agent | PR checklist; `ads check` flags new MCP servers over the limit |
| Merge an upgrade of this standard | `copier update` PR; conflicts resolved by the human; CI fails on conflict markers or `.rej` files |

A solo developer has no second human. The substitute is the `review` skill in a fresh context against the spec, then the human's merge behind required checks. This is an untested substitute and is recorded as an open question.

## 8. Metrics

| Metric | Definition |
|---|---|
| Cost per accepted change | List-price-equivalent agent spend (tokens by type × a dated price table) per repository per month ÷ accepted changes. An accepted change is a merged PR that passed the gates and was not reverted or hotfixed within 14 days. |
| First-pass acceptance | Share of agent PRs merged without a change-request cycle or a follow-up fix commit before merge. |
| Rework rate | Share of accepted changes followed by a revert or hotfix within 14 days (proxy for DORA's deployment rework rate where the project does not deploy). |
| Review latency | Median time from PR opened to merge. |
| Context health | P50 and P90 context tokens per call, share of sessions averaging over 200,000 tokens, fixed floor (`ads usage`). |

For one to five people, read trends over 8–12 weeks, not week to week.

## 9. Packaging and adapters

- The **core** is tool-neutral: `AGENTS.md`, `.agents/skills/`, `scripts/check.*`, CI, `acceptance/`, `docs/`. Codex, Cursor, Copilot and Gemini CLI read `AGENTS.md`; `.agents/skills` is read by Codex, Copilot, Cursor and Gemini CLI.
- The **Claude Code adapter** adds `CLAUDE.md` (`@AGENTS.md`, never a symlink, because Windows checks symlinks out as text), the `.claude/skills/` mirror, deny rules, a session-start hook, the guarded-paths hook and a small-model `Explore` subagent.
- The **Copilot adapter** adds `.github/copilot-instructions.md` pointing to `AGENTS.md`.
- The optional **diagrams** capability (`diagrams: true`, any profile and level) makes Penpot the source of truth for a project's diagrams and the repository the home of what is published: a Penpot file named `<project> · docs` with one page per diagram and one board per SVG, the exported SVGs in `docs/diagrams/`, and in `docs/design/` a README with the manifest, the visual language and the content rules, `tokens.json` (the shared visual language) and `postprocess-svg.sh`, which strips web fonts and adds system fallbacks. The README and tokens belong to the project after rendering; the script and the `update-diagram` skill (L2 and L3, where skills are rendered) stay with the template. Agents work through the Penpot MCP plugin, which cannot write to disk, so the human exports the SVGs and the agent copies them in.
- Enforcement travels with the repository (CI, hooks, rulesets), never with an agent's instruction channel.

## 10. Versioning

- Releases are SemVer tags (`v1.0.0`), which is Copier's update contract.
- **MAJOR**: adds a MUST to an existing level, tightens a numeric limit, or removes or moves a required file without a migration.
- **MINOR**: adds a SHOULD, a profile, a module, an adapter, a skill or a new rule at a level above the ones it changes nothing for.
- **PATCH**: fixes wording, the checker or templates without changing requirements.
- Deprecations are announced in [DEPRECATIONS.md](DEPRECATIONS.md) with a migration path and kept for at least one minor release and 90 days; removal happens only in a major release. Renames ship a Copier migration.
- Every repository records the version it was rendered from in `.copier-answers.yml`, because neither AGENTS.md nor Agent Skills carries a version.
