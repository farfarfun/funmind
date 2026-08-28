# Changelog

## Unreleased

### Breaking

- Renamed the package from `notemind` to `funmind` to match the repository name (`note*` → `fun*` cleanup, part of farfarfun/todo-list#298). The import name and the PyPI package name declared in `pyproject.toml` both changed:
  - `import notemind...` -> `import funmind...`
  - PyPI package name `notemind` -> `funmind`
  - Checked `pip index versions notemind`: no distribution was ever published under the old name, so there is nothing to forward. If that changes, publishing a final forwarding release of `notemind` that points users to `funmind` is a manual follow-up for the repo owner, not automated here.
