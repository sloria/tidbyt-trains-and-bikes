#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <version>" >&2
  echo "Example: $0 26.1.0" >&2
  exit 1
fi

version="$1"
tag="v${version}"

# Bump version in pyproject.toml
sed -i '' "s/^version = \".*\"/version = \"${version}\"/" pyproject.toml

# Sync lockfile
uv sync

# Commit, tag, and push
git add pyproject.toml uv.lock
git commit -m "Bump version to ${version}"
git tag "$tag"
git push --tags origin main
