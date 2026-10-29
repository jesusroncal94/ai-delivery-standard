# Changelog

The standard follows semantic versioning as defined in [STANDARD.md](STANDARD.md#10-versioning).

## 1.1.1 — unreleased

Documentation only; no rule, template or checker changes.

- `docs/workflow.md`: the day-to-day usage guide. It covers starting or adopting a project, the cycle of one change from `discover` to `release` with the human gates and CI jobs, the session rules S1–S11 at each step, and portfolio maintenance, saying who acts at each step. It is linked from the README.
- The repository documents itself with the `diagrams` capability: the Penpot file `ai-delivery-standard · docs`, `docs/design/` (manifest, visual language, `tokens.json`, `postprocess-svg.sh`) and four SVGs in `docs/diagrams/` (three layers, the cycle of one change, the cycle of one session, levels and profiles), embedded in the guide and the README.

## 1.1.0 — 2026-10-29

- Optional `diagrams` capability for every profile and level (Copier question `diagrams`, default false): Penpot is the source of truth for a project's diagrams and the repository keeps what is published. It renders `docs/design/README.md` (the Penpot file `<project> · docs`, working through the Penpot MCP plugin, an empty manifest, the visual language and the content rules), `docs/design/tokens.json` (the shared visual language), `docs/design/postprocess-svg.sh`, `docs/diagrams/` and, at L2 and L3, the `update-diagram` skill. The README and tokens are owned by the project after rendering.
- New rule L1-DIAGRAMS, applied only with `diagrams: true`: the manifest and `docs/diagrams/` agree, and no SVG contains `@font-face` or `<script>`.
- `AGENTS.md` lists `docs/design/`, `docs/diagrams/` and the `update-diagram` skill when diagrams are on.
- The test suite renders a committed snapshot of the working tree instead of the latest tag, so it tests the change under review.

## 1.0.1 — 2026-10-28

- Secret scanning runs the gitleaks container over the whole history instead of `gitleaks-action`, which failed on a repository's first push (the root commit has no parent), fails on pull requests in private repositories (the default token cannot list the PR's commits) and needs a licence for organisations.
- `ads.sh new` and `adopt` render from the published repository, so the answers file records a source that `copier update` and CI can reach; `ADS_SOURCE=/standard` renders the local checkout.
- `ads check` reads the Git remote and first commit date on the host, so projects checked out as worktrees pass L1-REMOTE.
- L2-MIRROR ignores CRLF line endings, so Windows checkouts with `core.autocrlf` compare equal when Git holds identical blobs.
- The local-only secret scan in `scripts/check.sh` passes Windows paths to Docker under Git Bash.

## 1.0.0 — 2026-10-28

First release.

- Three layers (portfolio, project, session), five profiles (`product`, `service`, `research`, `site`, `demo`) and three cumulative levels (L1 baseline, L2 gated, L3 measured).
- Context rules C1–C9, session rules S1–S11, cost and routing rules R1–R7, nine human gates and five metrics.
- Copier template with a tool-neutral core (`AGENTS.md`, `.agents/skills/`) and adapters for Claude Code and Copilot.
- Product modules `multi-user`, `eu-personal-data` and `ai-extraction`, carried over from the solo AI product starter kit (its v0).
- `ads` checker: `check`, `portfolio` and `usage`.
