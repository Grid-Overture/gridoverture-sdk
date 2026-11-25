# SPDX-License-Identifier: AGPL-3.0-or-later
"""scripts/release_notes.py: the body of a GitHub Release, which the platform's release reads for
the API contract the SDK implements, and the reader for the release's changes."""

import json
import re

import pytest
import release_notes

CHANGELOG = """# Changelog

Intro.

## [Unreleased]

## [0.2.0] - 2026-12-01

Speaks the contract.

### Added

- A check.

## [0.1.0] - 2026-11-25

The first release.

[Unreleased]: https://example.test/compare/v0.2.0...HEAD
[0.2.0]: https://example.test/v0.2.0
"""


@pytest.fixture
def sources(tmp_path, monkeypatch):
    spec = tmp_path / "openapi.public.json"
    spec.write_text(json.dumps({"openapi": "3.1.0", "info": {"version": "1.4.0"}, "paths": {}}))
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(CHANGELOG)
    monkeypatch.setattr(release_notes, "OPENAPI", spec)
    monkeypatch.setattr(release_notes, "CHANGELOG", changelog)
    return spec


def test_the_notes_declare_the_contract_alone_on_a_line_then_the_changes(sources):
    notes = release_notes.notes("0.2.0")
    assert re.search(r"^Gridoverture-Contract: 1\.4\.0$", notes, re.MULTILINE)
    assert notes.splitlines()[0] == "Gridoverture-Contract: 1.4.0"
    assert "Speaks the contract." in notes and "- A check." in notes
    assert "The first release." not in notes and "[0.2.0]:" not in notes


def test_the_last_section_ends_at_the_links(sources):
    notes = release_notes.notes("0.1.0")
    assert notes.rstrip().endswith("The first release.")


def test_the_contract_is_the_vendored_specs_version(sources):
    sources.write_text(json.dumps({"info": {"version": "2.0.0"}}))
    assert release_notes.notes("0.2.0").startswith("Gridoverture-Contract: 2.0.0\n")


def test_a_version_without_a_changelog_section_is_refused(sources):
    with pytest.raises(ValueError, match="no section for 0.3.0"):
        release_notes.notes("0.3.0")


def test_a_spec_version_that_is_not_semver_is_refused(sources):
    sources.write_text(json.dumps({"info": {"version": "1.0"}}))
    with pytest.raises(ValueError, match="not a contract version"):
        release_notes.notes("0.2.0")


def test_the_repositorys_own_changelog_and_spec_make_notes():
    version = re.search(r"^## \[(\d+\.\d+\.\d+)\]", release_notes.CHANGELOG.read_text(), re.M)
    assert release_notes.notes(version.group(1)).startswith("Gridoverture-Contract: ")
