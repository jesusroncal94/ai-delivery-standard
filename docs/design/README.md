# Design: diagrams and visual language

## Source of truth

This repository is not rendered from its own template; this folder and `../diagrams/` were copied from a render with `diagrams: true` and follow the same rules, and the checker's L1-DIAGRAMS logic is run against them by hand.

The diagrams are designed in the Penpot file **ai-delivery-standard · docs**, one page per diagram and one board per exported SVG. The repository keeps what is published: the SVG export of each board in [`../diagrams/`](../diagrams/) and a backup of the Penpot file in this folder (`ai-delivery-standard-docs.penpot`), refreshed when the file's pages or library change.

Never edit an exported SVG by hand beyond [`postprocess-svg.sh`](postprocess-svg.sh); the change would be lost on the next export.

## Working with Penpot through an agent

Agents edit the diagrams through the Penpot MCP plugin; the `update-diagram` skill holds the full procedure (its source is [`template/_skills/update-diagram.md`](../../template/_skills/update-diagram.md), since this repository renders no skills for itself).

- The plugin must be connected to **ai-delivery-standard · docs**. An agent checks the connected file's name before any change and never edits another Penpot file.
- The Penpot tab must stay in the foreground: browsers suspend background tabs and the plugin stops answering until the tab is focused again.
- The plugin cannot write to disk (browsers block its requests to localhost). The owner exports the SVGs, and the `.penpot` backup when it changes, to their `Downloads` folder; the agent checks and copies them into the repository and runs `bash docs/design/postprocess-svg.sh`.

## Changing a diagram

1. Edit the board in Penpot with the file's library only, and review it as a PNG export.
2. Export it as SVG, named after the board, and copy it to `docs/diagrams/<board>.svg`.
3. Run `bash docs/design/postprocess-svg.sh`. It removes the `@font-face` block (it loads fonts from Penpot's servers) and adds the system fallbacks from [tokens.json](tokens.json); a second run reports every file unchanged.
4. Update the export date in the manifest (a new diagram gets a row), change the page that uses the diagram so text and image agree, run `docker compose run --rm tests` and open a pull request.

## Manifest

Every SVG in `docs/diagrams/` has a row and every row links an existing SVG; `ads check` (rule L1-DIAGRAMS) fails otherwise, and when an SVG carries `@font-face` or a `<script>`.

| Penpot page | Board | Published file | Used in | Exported |
|---|---|---|---|---|
| 01 Three layers | three-layers | [three-layers.svg](../diagrams/three-layers.svg) | [Workflow](../workflow.md), [README](../../README.md) | 2026-10-29 |
| 02 Change cycle | change-cycle | [change-cycle.svg](../diagrams/change-cycle.svg) | [Workflow](../workflow.md#2-the-cycle-of-one-change) | 2026-10-29 |
| 03 Session cycle | session-cycle | [session-cycle.svg](../diagrams/session-cycle.svg) | [Workflow](../workflow.md#sessions-inside-the-cycle) | 2026-10-29 |
| 04 Levels and profiles | levels-and-profiles | [levels-and-profiles.svg](../diagrams/levels-and-profiles.svg) | [Workflow](../workflow.md#1-start-or-adopt-a-project) | 2026-10-29 |

A Foundations page holds a style sheet board with every role, arrow and text style.

## Visual language

Defined as library colours and typographies in the Penpot file; [tokens.json](tokens.json) mirrors them for anyone drawing outside Penpot. Colour means a role, never decoration.

| Role | Fill | Stroke | Used for |
|---|---|---|---|
| Human gate | `#FEF3C7` | `#D97706` | Decisions only a person takes: approvals, merges, releases |
| Agent | `#E0E7FF` | `#4F46E5` | Coding agents, subagents, skills |
| Sensor or guard | `#D1FAE5` | `#059669` | Checks that can fail a change: tests, CI, hooks, validators |
| Artefact | `#F1F5F9` | `#475569` | Files in a repository |
| Production | `#E0F2FE` | `#0284C7` | Live systems, schedules, what users reach |
| AI-generated | `#FCE7F3` | `#DB2777` | Content produced by a generative model |
| Module (optional) | white | `#7C3AED`, dashed | Optional parts chosen per project |

Arrows are slate (`#475569`) and solid for the next step; failure and findings loops are red (`#DC2626`) and dashed; feedback loops are blue and dashed. Text uses Inter: titles 22/700, sections 15/700, node titles 13/700, body 12/400, notes 11/400. Exported SVGs fall back to Segoe UI, Roboto, Helvetica or Arial where Inter is not installed.

## Rules for content

- Text in diagrams is English, like the rest of the repository.
- Diagrams describe the process, the architecture and the boundaries, never the data: no personal details, credentials, customer names or confidential findings. Examples use generic products.
- Draw from the approved text in `docs/`, not the other way round; a diagram that shows something the text does not say changes the text in the same pull request.
