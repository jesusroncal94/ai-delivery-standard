#!/usr/bin/env bash
# Runs the standard's tools in Docker, so the host needs only Docker and Git.
#   scripts/ads.sh new <dir> [copier options]     render a new project
#   scripts/ads.sh adopt <dir> [copier options]   add the standard to an existing repository
#   scripts/ads.sh update <dir>                   upgrade a project to the latest standard
#   scripts/ads.sh check <dir> [--json]           conformance of one project
#   scripts/ads.sh portfolio <registry.yaml>      conformance of every project in a registry
#   scripts/ads.sh usage [<transcripts dir>]      context per call from Claude Code transcripts
# The current directory is mounted read-only at /cwd, e.g. new <dir> --data-file /cwd/portfolio-defaults.yml
set -euo pipefail

abspath() { (cd "$1" && { pwd -W 2>/dev/null || pwd; }); }

standard=$(abspath "$(dirname "$0")/..")
image=ai-delivery-standard
command=${1:?usage: ads.sh new|adopt|update|check|portfolio|usage ...}
shift

docker build -q -t "$image" "$standard" >/dev/null

run() { MSYS_NO_PATHCONV=1 docker run --rm -i -v "$standard:/standard:ro" -v "$(abspath .):/cwd:ro" "$@"; }

case "$command" in
  new|adopt)
    mkdir -p "${1:?target directory}"; target=$(abspath "$1"); shift
    run -v "$target:/work" --entrypoint copier "$image" copy --trust "$@" /standard /work ;;
  update)
    target=$(abspath "${1:?target directory}"); shift
    run -v "$target:/work" -w /work --entrypoint copier "$image" update --trust "$@" ;;
  check)
    target=$(abspath "${1:-.}"); shift || true
    run -v "$target:/work" "$image" check /work "$@" ;;
  portfolio)
    registry=$(abspath "$(dirname "${1:?registry file}")"); name=$(basename "$1"); shift
    run -v "$registry:/portfolio" "$image" portfolio "/portfolio/$name" "$@" ;;
  usage)
    transcripts=$(abspath "${1:-$HOME/.claude/projects}"); shift || true
    run -v "$transcripts:/transcripts:ro" "$image" usage /transcripts "$@" ;;
  *) echo "unknown command: $command" >&2; exit 2 ;;
esac
