#!/usr/bin/env bash
# Runs the standard's tools in Docker, so the host needs only Docker and Git.
#   scripts/ads.sh new <dir> [copier options]     render a new project
#   scripts/ads.sh adopt <dir> [copier options]   add the standard to an existing repository
#   scripts/ads.sh update <dir>                   upgrade a project to the latest standard
#   scripts/ads.sh check <dir> [--json]           conformance of one project
#   scripts/ads.sh portfolio <registry.yaml>      conformance of every project in a registry
#   scripts/ads.sh usage [<transcripts dir>]      context per call from Claude Code transcripts
set -euo pipefail

standard=$(cd "$(dirname "$0")/.." && pwd)
image=ai-delivery-standard
command=${1:?usage: ads.sh new|adopt|update|check|portfolio|usage ...}
shift

docker image inspect "$image" >/dev/null 2>&1 || docker build -q -t "$image" "$standard" >/dev/null

run() { MSYS_NO_PATHCONV=1 docker run --rm -i -v "$standard:/standard:ro" "$@"; }

case "$command" in
  new|adopt)
    target=$(mkdir -p "${1:?target directory}" && cd "$1" && pwd); shift
    run -v "$target:/work" --entrypoint copier "$image" copy --trust "$@" /standard /work ;;
  update)
    target=$(cd "${1:?target directory}" && pwd); shift
    run -v "$target:/work" -w /work --entrypoint copier "$image" update --trust "$@" ;;
  check)
    target=$(cd "${1:-.}" && pwd); shift || true
    run -v "$target:/work" "$image" check /work "$@" ;;
  portfolio)
    registry=$(cd "$(dirname "${1:?registry file}")" && pwd); name=$(basename "$1"); shift
    run -v "$registry:/portfolio" "$image" portfolio "/portfolio/$name" "$@" ;;
  usage)
    transcripts=${1:-$HOME/.claude/projects}; shift || true
    run -v "$transcripts:/transcripts:ro" "$image" usage /transcripts "$@" ;;
  *) echo "unknown command: $command" >&2; exit 2 ;;
esac
