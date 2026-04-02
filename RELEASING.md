# Releasing

1. Bump version in `pyproject.toml`
2. Run `uv lock -U`
3. `git commit -m "Bump version"`
4. `git tag vX.Y.Z` (replace with the new version)
5. `git push --tags origin main`
