# Changelog

Every release of `gridoverture`, newest first, and the platform version whose public API it
speaks. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions
follow [semantic versioning](https://semver.org).

## [Unreleased]

## [0.2.0] - 2026-11-25

Implements API contract 1.0.0, from the platform's public API at
`35fb71a36b13d614a07f82e572a97c853065fcbf`.

### Changed

- The client calls the platform's routes under `/v1`, the contract's major. v0.1.0 called them
  unversioned; the platform answers those as deprecated aliases until 2027-05-25.
- The generated client knows `Me.account_kind` and `VersionIn.time_zone`.

### Added

- The API contract: `go.CONTRACT`, the version of the spec the client is generated from. Every
  answer's `Gridoverture-Contract` header is checked: another major raises
  `IncompatibleContractError`, a newer minor works.
- `DeprecatedApiWarning`, from a `Deprecation` or `Sunset` header, with its dates and link.
- `go.__version__`.
- A GitHub Release for every tag, with the wheel and the sdist, whose notes start with
  `Gridoverture-Contract: X.Y.Z`.

## [0.1.0] - 2026-11-25

Speaks the platform's public API at `6ff5bb625c93ab0c35b422ed9c79d786091ca7ed`.

The first release on its own repository.

### Added

- `Client`, through the platform's public gateway with a personal access token, from arguments
  or `GRIDOVERTURE_URL` and `GRIDOVERTURE_TOKEN`.
- Projects: list, get by name or id, create.
- Versions: import a file (PSS/E RAW, MATPOWER, pandapower, VeraGrid, IEEE CDF, CGMES, PowerFactory
  pf2xml) through a signed upload, list, latest, download.
- Model objects read from a version's CGMES file: `Version.objects` and `Version.find`, with the
  CGMES 3.0 class hierarchy.
- Edits into a child version: `SetAttribute`, `AddObject`, `RemoveObject`.
- Studies as jobs with typed settings: power flow, validation, export, each with `Job.wait` and
  `Job.cancel`, and results as tables with `to_pandas()`.
- Errors as exceptions by kind, each with the platform's problem details and request id.
- The low-level client generated from the vendored `spec/openapi.public.json`, with
  `scripts/sync_openapi.py` and the `sync-openapi` workflow to take a newer one.

[Unreleased]: https://github.com/Grid-Overture/gridoverture-sdk/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/Grid-Overture/gridoverture-sdk/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Grid-Overture/gridoverture-sdk/releases/tag/v0.1.0
