# Changelog

Every release of `gridoverture`, newest first, and the platform version whose public API it
speaks. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions
follow [semantic versioning](https://semver.org).

## [Unreleased]

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

[Unreleased]: https://github.com/Grid-Overture/gridoverture-sdk/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Grid-Overture/gridoverture-sdk/releases/tag/v0.1.0
