# SPDX-License-Identifier: AGPL-3.0-or-later
"""Writes the body of the GitHub Release of a version: first, alone on its line,

    Gridoverture-Contract: <info.version of spec/openapi.public.json>

which the platform's own release reads to know which API contract this SDK release implements
(drafts and prereleases it ignores), then the version's section of CHANGELOG.md.

Usage: release_notes.py <version>, as 0.2.0 (no leading v). The release workflow runs it on a tag.
"""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OPENAPI = ROOT / "spec" / "openapi.public.json"
CHANGELOG = ROOT / "CHANGELOG.md"
SEMVER = re.compile(r"\d+\.\d+\.\d+")


def contract() -> str:
    """The API contract the vendored spec, and so the generated client, speaks."""
    version = json.loads(OPENAPI.read_text(encoding="utf-8"))["info"]["version"]
    if not SEMVER.fullmatch(version):
        raise ValueError(f"{version!r} in {OPENAPI.name} is not a contract version (X.Y.Z)")
    return version


def changelog_section(text: str, version: str) -> str:
    """What CHANGELOG.md says under `## [version]`, up to the next section or the link list."""
    heading = re.search(rf"^## \[{re.escape(version)}\][^\n]*\n", text, re.MULTILINE)
    if heading is None:
        raise ValueError(f"CHANGELOG.md has no section for {version}")
    rest = text[heading.end() :]
    end = re.search(r"^(## \[|\[[^\]]+\]: )", rest, re.MULTILINE)
    return (rest[: end.start()] if end else rest).strip()


def notes(version: str) -> str:
    """The release's body: the contract line, a blank line, then the version's changes."""
    section = changelog_section(CHANGELOG.read_text(encoding="utf-8"), version)
    return f"Gridoverture-Contract: {contract()}\n\n{section}\n"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    try:
        print(notes(sys.argv[1].removeprefix("v")), end="")
    except ValueError as error:
        sys.exit(f"release_notes: {error}")
