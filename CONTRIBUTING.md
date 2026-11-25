# Contributing

## Setup and checks

You need [uv](https://docs.astral.sh/uv/). Everything else it installs.

```bash
uv sync          # the SDK, editable, and the dev tools
make lint        # ruff check and ruff format --check; line length 100
make test        # pytest, against a fake API: no platform needed
```

`ci` runs the same on Python 3.11 to 3.14, checks that the generated client is what `spec/` makes,
and builds the wheel. Pull requests target `main`.

## How the code is written

- English everywhere: code, names, comments, docs, commits.
- Descriptive names, no abbreviations (`bus_voltage_kv`, not `bv`), except the domain's own:
  `pu`, `mva`, `kv`, `rms`, `emt`.
- Comments say why, not what. Every public object has a docstring; a test fails otherwise.
- No engine is named outside the power flow's optional `engine`: a study has a kind, and the
  platform chooses what runs it. A test fails otherwise.
- Every new hand-written file starts with `# SPDX-License-Identifier: AGPL-3.0-or-later`.
- Commits follow [Conventional Commits](https://www.conventionalcommits.org): `feat:`, `fix:`,
  `docs:`, `chore:`.

## The generated client

`src/gridoverture/_generated` is never edited by hand. `make generate` writes it from the two
files in `spec/`:

- `openapi.public.json`, the platform's public routes, at the platform version in `PLATFORM_REF`.
- `cgmes-3.0-class-parents.json`, the CGMES 3.0 class hierarchy. CGMES 3.0 is fixed, so this one
  does not follow the platform.

To take a newer `openapi.public.json`, run the `sync-openapi` workflow from the Actions tab with the
platform's tag, or by hand:

```bash
make sync-openapi REF=v0.2.0 FILE=path/to/openapi.public.json
```

Either way it prints the routes added and removed. Add the hand-written layer for a new route, with
its tests, a line in `docs/reference.md` and one in `CHANGELOG.md`, in the same pull request.

## Releasing

1. Move `[Unreleased]` in `CHANGELOG.md` to the new version, with the platform version it speaks
   (`spec/PLATFORM_REF`).
2. Set `version` in `pyproject.toml`, and the version in the install commands of `README.md` and
   `README.es.md`.
3. Merge, then tag `main`: `git tag vX.Y.Z && git push origin vX.Y.Z`. `ci` fails on a tag that is
   not the version in `pyproject.toml`.

The package is not on PyPI yet; `pyproject.toml` is ready for it.
