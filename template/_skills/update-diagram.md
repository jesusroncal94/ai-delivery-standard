---
name: update-diagram
description: Create or change a diagram in Penpot and publish it to docs/diagrams/ with the manifest updated. Use when the human asks to add, fix, redraw or update a diagram, or when a change to the process or the architecture makes a diagram in docs/ out of date.
---

# update-diagram

Penpot is the source of the diagrams; the repository keeps the published SVGs and a backup of the Penpot file. Read `docs/design/README.md` first: the Penpot file's name, the manifest, the visual language and the content rules.

## 1. Check the connection before touching anything

1. Run `penpot.currentFile.name` through the Penpot MCP. It must be the file named in `docs/design/README.md` (`<project> · docs`). If it is any other file, stop and ask the human to connect the plugin from the right one; never change another Penpot file.
2. If a call fails or reports a suspended tab, ask the human to bring the Penpot tab to the front and keep it visible while you work.
3. Never switch the file's token theme; switching themes can stall the tab.

## 2. Edit in Penpot

1. Work on the diagram's own page and board (names in the manifest). A new diagram gets a new page and a kebab-case board, whose name becomes the file name.
2. Use only the file's library: the role colours, the neutral colours and the typographies mirrored in `docs/design/tokens.json`. Colour means a role; arrows follow the conventions in the design README.
3. Content: English; the process, the architecture and the boundaries, never the data (no personal details, credentials or confidential findings). Draw from the approved text in `docs/`; if the drawing needs something the text does not say, change the text too.
4. Review the board by exporting it to PNG with `export_shape`, and fix overlaps, overflowing or awkwardly wrapped text and stray lines before showing it. The export can time out on a cold font; retry.
5. The human approves the board before it is published.

## 3. Publish

The Penpot plugin cannot write to disk.

1. Ask the human to export the board as SVG, named after the board, to their `Downloads` folder, and the whole file as `.penpot` when its pages or library changed.
2. Check each downloaded file's content before copying it: `Downloads` may hold a file of the same name from another project. Copy, never move, into `docs/diagrams/<board>.svg` and `docs/design/<project>-docs.penpot`.
3. Run `bash docs/design/postprocess-svg.sh docs/diagrams/<board>.svg`; a second run must report the file unchanged. The SVG must contain no `@font-face` and no `<script>`.
4. Update the export date in the manifest of `docs/design/README.md` (a new diagram gets a row), and embed or link the SVG where the manifest says it is used, changing that page's text so both say the same.
5. Run the project's check command from `AGENTS.md` and `ads check`, which fails when the manifest and `docs/diagrams/` disagree. Fix everything they report.
6. Commit on a branch (`docs(diagrams): <subject>`) and stop; the human pushes and merges.
