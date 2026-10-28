# Adopting the standard

Everything runs in Docker, so a machine needs only Docker and Git. On Windows, run the commands from PowerShell with `.\scripts\ads.ps1` (it forwards to Git Bash) or from Git Bash with `scripts/ads.sh`. The first run builds the image `ai-delivery-standard`.

## Start a new project

```
scripts/ads.sh new ../my-api
```

Copier asks for the profile, the level, the adapters and the check command; pass `--data-file /cwd/portfolio-defaults.yml` (the current folder is mounted at `/cwd`) to reuse a team's conventions (see [portfolio.md](portfolio.md)). Then:

1. Fill in the Commands section of `AGENTS.md` and the check command in `scripts/check.sh`.
2. `git init -b main`, commit, add the remote and push.
3. Protect `main`: require a pull request and the `standard` workflow's checks. Create the `human-approved` label.
4. Run `scripts/ads.sh check ../my-api` until it conforms.

## Adopt an existing repository

Work on a branch. Copier never overwrites user-owned files listed in `_skip_if_exists` (README, `.gitignore`, `progress.md`, `acceptance/features.json`, product and privacy documents) and shows a diff for every other file it would change.

```
git -C ../legacy switch -c chore/adopt-ai-delivery-standard
scripts/ads.sh adopt ../legacy --data profile=service --data level=1
```

1. Merge the generated `AGENTS.md` with the old rules file. Keep commands, gotchas and prohibitions; drop anything an agent can read from the code. Stay under 200 lines.
2. If the old file was `CLAUDE.md`, move its content into `AGENTS.md` and leave `CLAUDE.md` as the single line `@AGENTS.md`.
3. Split any reference document over 25,000 tokens into sections, and archive old progress entries until `progress.md` is under 5,000 tokens.
4. Move project skills from `.claude/skills/` to `.agents/skills/` with only specification frontmatter (`name`, `description`), then run `scripts/sync-skills.sh`.
5. Start at L1, merge, then raise the level one step at a time with `scripts/ads.sh update ../legacy --data level=2`.

## Upgrade to a new version

```
scripts/ads.sh update ../my-api
```

Copier regenerates the old version, applies the new one and replays your local changes. Conflicts appear as inline markers or `.rej` files; resolve them, then open a PR. `check-gates.sh` fails while any marker or `.rej` file remains, and the guarded paths need the `human-approved` label. The scheduled `standard-update` job warns when a newer version exists.

## Check conformance

```
scripts/ads.sh check ../my-api
scripts/ads.sh check ../my-api --json
```

The report lists every rule with `ok`, `FAIL` (required at the target level) or `next` (required at a higher level). The exit code is 0 when the project meets its target level.

## Measure sessions

```
scripts/ads.sh usage
```

Reads Claude Code transcripts (`~/.claude/projects` by default) and prints, per session, the number of model calls, P50 and P90 context per call and cache-read tokens, flagging sessions that average over 200,000 tokens per call. Use it for the context-health metric and the monthly record. Transcripts never leave the machine.

## Other agent tools

- Codex, Cursor, Gemini CLI and Copilot read `AGENTS.md` and `.agents/skills/` natively.
- For Copilot surfaces that read only `.github/copilot-instructions.md`, add the `copilot` adapter.
- Claude Code needs the `claude-code` adapter: it reads `.claude/skills/` and `CLAUDE.md`, not `.agents/skills/`.
