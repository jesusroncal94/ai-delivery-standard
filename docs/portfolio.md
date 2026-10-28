# Running a portfolio

The portfolio layer is two files a team keeps next to its projects, plus the standard's tools.

## Registry: `portfolio.yaml`

```yaml
root: .            # folder that holds the projects, relative to this file
projects:
  - path: billing-api
    profile: service
    target: 2
    status: active
  - path: onboarding-app
    profile: product
    target: 3
    status: active
    note: pilot for L3 metrics
  - path: old-demo
    profile: demo
    target: 1
    status: archived
```

`scripts/ads.sh portfolio portfolio.yaml --output /portfolio/portfolio-status.md` checks every project against its target and writes a table of achieved levels and failing rules. The registry's profile and target apply when a project has no answers file yet, which is how unadopted repositories show up as gaps.

## Shared conventions: `portfolio-defaults.yml`

A Copier data file with the answers every project in the portfolio shares, above all the `conventions` list rendered into each `AGENTS.md`:

```yaml
conventions:
  - "Conventional commits: `<type>(<scope>): <subject>`, imperative, lowercase, no trailing period."
  - "One long-lived branch, `main`; squash merges only."
  - "Never commit a secret, token or key; use environment variables."
  - "Everything committed is in English."
  - "Toolchains run in Docker; task shortcuts are scripts, not a Makefile."
standard_repo: https://github.com/your-org/ai-delivery-standard
```

Pass it on every render from the folder that holds it: `bash ai-delivery-standard/scripts/ads.sh new x --data-file /cwd/portfolio-defaults.yml` (the wrapper mounts the current folder read-only at `/cwd`). Changing a convention means editing this file and running `copier update --data-file ...` in each project, so the change arrives as reviewed PRs rather than as edits by hand.

## A portfolio-level rules file (optional)

Agents that load parent folders' instruction files (Claude Code does) also read a rules file in the folder above the projects. Keep it short and limited to what spans projects: where the registry is, how to run the portfolio check, which projects are private, and which tools need the human. Do not repeat the conventions there: they already live in every repository, where collaborators and other tools see them.

## Cadence

| When | What |
|---|---|
| Every PR | `ads check` and the gates in CI |
| Weekly | `standard-update` job; usage review (rule R6) |
| Monthly | `ads portfolio`; metrics record per L3 project |
| Quarterly | Harness review per L3 project; review the standard against its triggers |
