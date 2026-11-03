#!/usr/bin/env bash
# Checks that a commit is ready to be tagged as a release, before tagging and again in CI once the tag is pushed:
# the latest CHANGELOG.md entry is that version with the release date, and the checker reports the same version.
#   scripts/check-release.sh v<major>.<minor>.<patch> [repository]
# The release date is the tag's own date once the tag exists, otherwise today.
set -euo pipefail

tag=${1:?usage: check-release.sh v<major>.<minor>.<patch> [repository]}
cd "${2:-$(dirname "$0")/..}"

[[ $tag =~ ^v([0-9]+\.[0-9]+\.[0-9]+)$ ]] || { echo "check-release: '$tag' is not a release tag like v1.2.3" >&2; exit 1; }
version=${BASH_REMATCH[1]}

if git rev-parse -q --verify "refs/tags/$tag" >/dev/null 2>&1; then
  released=$(git for-each-ref "refs/tags/$tag" --format='%(if)%(taggerdate)%(then)%(taggerdate:short)%(else)%(committerdate:short)%(end)')
else
  released=$(date +%F)
fi

# Windows checkouts may have CRLF line endings.
read_lf() { tr -d '\r' < "$1" 2>/dev/null || true; }

problems=()
latest=$(read_lf CHANGELOG.md | grep -m1 '^## ' || true)
[[ $latest == "## $version — $released" ]] || problems+=("the latest CHANGELOG.md entry is '$latest', not '## $version — $released'")
read_lf checker/ads/__init__.py | grep -qx "__version__ = \"$version\"" || problems+=("checker/ads/__init__.py does not set __version__ = \"$version\"")
read_lf checker/pyproject.toml | grep -qx "version = \"$version\"" || problems+=("checker/pyproject.toml does not set version = \"$version\"")

if ((${#problems[@]})); then
  echo "check-release: this commit is not ready to be released as $tag:" >&2
  printf -- '- %s\n' "${problems[@]}" >&2
  exit 1
fi
echo "check-release: ready to release $tag ($released)"
