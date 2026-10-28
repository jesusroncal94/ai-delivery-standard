# Changelog

The standard follows semantic versioning as defined in [STANDARD.md](STANDARD.md#10-versioning).

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
