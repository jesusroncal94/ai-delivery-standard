# ai-delivery-standard: rules for agents

The AI delivery standard: a Copier template (`copier.yml`, `template/`), its normative text (`STANDARD.md`) and the `ads` checker (`checker/`).

## Commands

```
docker compose run --rm tests                                  # checker tests, rendering every profile
bash scripts/ads.sh check <dir>                                # conformance of a project
bash scripts/ads.sh usage                                      # context per call from local transcripts
```

## Definition of done

1. `docker compose run --rm tests` passes.
2. A change to a rule appears in `STANDARD.md`, in `checker/ads/rules.py` and, when it changes what is rendered, in `template/`, all in the same commit.
3. `CHANGELOG.md` records the change under the version it will ship in, following the versioning policy in `STANDARD.md` section 10.

## Prohibitions

- Do not push, tag or release; the human does.
- Do not edit a rendered skill wrapper; edit its single source in `template/_skills/`.
- Do not put GitHub `${{ }}` expressions in a `.jinja` file outside `{% raw %}` blocks.
- Do not use `<`, `>`, `:`, `"`, `|`, `?` or `*` in template file names: Windows cannot check them out. Write conditions as `level in [2, 3]`.
- Do not add a runtime dependency to the checker beyond PyYAML.
- Do not cite private material in `docs/evidence.md`; every finding links a public primary source.

## Portfolio conventions

- Conventional commits: `<type>(<scope>): <subject>`, imperative, lowercase, no trailing period.
- One long-lived branch, `main`; short-lived feature branches; squash merges only.
- Never commit a secret, token or key.
- Everything committed is in English.

## Where things live

- `template/_skills/`: one source per skill, included into both `.agents/skills/` and `.claude/skills/`.
- Copier's Jinja search path is the repository root, so includes are written `template/_skills/<name>.md`.
- `checker/tests/fixtures/transcripts/`: synthetic transcripts for `ads usage`.
