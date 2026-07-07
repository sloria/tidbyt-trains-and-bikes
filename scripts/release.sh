#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <version>" >&2
  echo "Example: $0 26.1.0" >&2
  exit 1
fi

version="$1"
tag="v${version}"

# Bump version in pyproject.toml and re-lock
uv version "${version}"

# Commit, tag, and push
git add pyproject.toml uv.lock
git commit -m "chore: bump version to ${version}"
git tag "$tag"
git push --tags origin main
