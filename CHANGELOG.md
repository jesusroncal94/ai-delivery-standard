# Changelog

The standard follows semantic versioning as defined in [STANDARD.md](STANDARD.md#10-versioning).

## 1.1.5 — unreleased

A template fix; no rule or checker changes.

- `scripts/check.sh` no longer calls itself when the check command runs it. A project that answered `check_command` with `bash scripts/check.sh` (or `scripts/check.sh`, or a command running `scripts/check.ps1`) got a script that ran that command, which ran the script again, forever. Such an answer now renders a script that fails with a message asking for the real check; `AGENTS.md` still shows the answer as the command agents run. A Copier validator was rejected: on `copier update --defaults` Copier drops an answer that fails validation and silently renders the default instead, and a check too long for one line belongs in the script.
- Upgrading a project whose answer runs `scripts/check.sh` and whose script already holds the real check: `ads.sh update` keeps the answer and leaves one conflict in `scripts/check.sh`. Keep the `before updating` side, which is your check, and delete the placeholder.
- `docs/adoption.md` and the `check_command` help text say to answer `bash scripts/check.sh` when the check is written in the script.

## 1.1.4 — 2026-11-02

A checker fix; no rule or template changes.

- `ads --version` reports the release: it said 1.0.0 since the first release, including in 1.1.3. A test keeps `ads/__init__.py`, `checker/pyproject.toml` and the latest changelog entry in step.

## 1.1.3 — 2026-11-01

Tooling and documentation only; no rule, template or checker changes.

- `tools/penpot-mcp/`: Penpot's official MCP server (`@penpot/mcp` 2.17.0) and its plugin in Docker, bound to `127.0.0.1`, as the local alternative to a hosted Penpot MCP connector for projects with the `diagrams` capability. Its README covers starting it, the one-time plugin setup in Penpot, registering `http://localhost:4401/mcp` in a project's `.mcp.json`, the `files/` mount and upgrading. Linked from the diagrams step in `docs/adoption.md` and from the README.

## 1.1.2 — 2026-10-30

Fixes to the wrappers and the checker; no rule or template changes.

- `ads.sh portfolio` sees the projects wherever the registry's `root:` points. It mounted only the registry's folder, so a registry kept in its own folder next to the projects (`root: ..`) found no project. The wrapper now reads `root:` on the host and, when it is outside the registry's folder, mounts that folder read-only at `/projects`; the registry's folder stays writable at `/portfolio` for `--output`. Registries with `root: .` run exactly as before.
- `ads portfolio --root <dir>` overrides the registry's `root:`.
- `ads.sh portfolio` accepts a registry path written with backslashes, as PowerShell passes it.
- `ads.ps1` runs Git Bash from the Git for Windows installation instead of the first `bash.exe` on PATH, which is often WSL's and cannot run Windows paths.
- `docs/portfolio.md`: keeping the registry in its own private repository next to the projects, with a one-line `CLAUDE.md` in the projects folder that imports the registry's rules file.

## 1.1.1 — 2026-10-29

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
