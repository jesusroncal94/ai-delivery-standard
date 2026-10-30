#!/usr/bin/env bash
# Runs the standard's tools in Docker, so the host needs only Docker and Git.
#   scripts/ads.sh new <dir> [copier options]     render a new project
#   scripts/ads.sh adopt <dir> [copier options]   add the standard to an existing repository
#   scripts/ads.sh update <dir>                   upgrade a project to the latest standard
#   scripts/ads.sh check <dir> [--json]           conformance of one project
#   scripts/ads.sh portfolio <registry.yaml>      conformance of every project in a registry
#   scripts/ads.sh usage [<transcripts dir>]      context per call from Claude Code transcripts
# The current directory is mounted read-only at /cwd, e.g. new <dir> --data-file /cwd/portfolio-defaults.yml
# new and adopt render from the published template (ADS_SOURCE=/standard renders this checkout instead).
# portfolio mounts the registry's folder at /portfolio (write reports with --output /portfolio/<file>) and,
# when its root: points outside that folder (root: ..), the projects folder read-only at /projects.
set -euo pipefail

abspath() { (cd "$1" && { pwd -W 2>/dev/null || pwd; }); }

standard=$(abspath "$(dirname "$0")/..")
image=ai-delivery-standard
source=${ADS_SOURCE:-https://github.com/jesusroncal94/ai-delivery-standard.git}
command=${1:?usage: ads.sh new|adopt|update|check|portfolio|usage ...}
shift

docker build -q -t "$image" "$standard" >/dev/null

run() { MSYS_NO_PATHCONV=1 docker run --rm -i -v "$standard:/standard:ro" -v "$(abspath .):/cwd:ro" "$@"; }

case "$command" in
  new|adopt)
    mkdir -p "${1:?target directory}"; target=$(abspath "$1"); shift
    run -v "$target:/work" --entrypoint copier "$image" copy --trust "$@" "$source" /work ;;
  update)
    target=$(abspath "${1:?target directory}"); shift
    run -v "$target:/work" -w /work --entrypoint copier "$image" update --trust "$@" ;;
  check)
    target=$(abspath "${1:-.}"); shift || true
    remotes=$(git -C "$target" remote 2>/dev/null | tr '\n' ' ' || true)
    first_commit=$(git -C "$target" log --reverse --format=%cs --max-parents=0 2>/dev/null | head -n 1 || true)
    run -v "$target:/work" -e ADS_GIT_REMOTES="$remotes" -e ADS_GIT_FIRST_COMMIT="$first_commit" "$image" check /work "$@" ;;
  portfolio)
    file=${1:?registry file}; file=${file//\\//}; shift
    registry=$(abspath "$(dirname "$file")"); name=$(basename "$file")
    root=$(sed -n -E "s/^root:[[:space:]]*['\"]?([^'\"#]*[^'\"#[:space:]])['\"]?[[:space:]]*(#.*)?\$/\1/p" "$registry/$name" | head -n 1)
    projects=$(cd "$registry" && abspath "${root:-.}")
    case "$projects/" in
      "$registry/"*) run -v "$registry:/portfolio" "$image" portfolio "/portfolio/$name" "$@" ;;
      *) run -v "$registry:/portfolio" -v "$projects:/projects:ro" "$image" portfolio "/portfolio/$name" --root /projects "$@" ;;
    esac ;;
  usage)
    transcripts=$(abspath "${1:-$HOME/.claude/projects}"); shift || true
    run -v "$transcripts:/transcripts:ro" "$image" usage /transcripts "$@" ;;
  *) echo "unknown command: $command" >&2; exit 2 ;;
esac
