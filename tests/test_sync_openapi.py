# SPDX-License-Identifier: AGPL-3.0-or-later
"""scripts/sync_openapi.py: a newer spec from the platform replaces the vendored one, names its
platform version, regenerates the client and says which routes changed."""

import json

import pytest
import sync_openapi


def spec(*routes):
    paths = {}
    for route in routes:
        method, path = route.split(" ")
        paths.setdefault(path, {})[method.lower()] = {"responses": {}}
    return {"openapi": "3.1.0", "info": {"title": "API", "version": "1"}, "paths": paths}


@pytest.fixture
def spec_directory(tmp_path, monkeypatch):
    """spec/ and _generated/ in a scratch directory, with the vendored spec holding two routes."""
    vendored = tmp_path / "spec" / "openapi.public.json"
    vendored.parent.mkdir()
    vendored.write_text(json.dumps(spec("GET /projects", "GET /jobs")))
    generated = []
    monkeypatch.setattr(sync_openapi, "OPENAPI", vendored)
    monkeypatch.setattr(sync_openapi, "PLATFORM_REF", tmp_path / "spec" / "PLATFORM_REF")
    monkeypatch.setattr(sync_openapi, "generate", generated.append)
    return tmp_path, generated


def test_a_newer_spec_is_vendored_with_its_platform_version_and_regenerated(spec_directory):
    root, generated = spec_directory
    newer = root / "newer.json"
    newer.write_text(json.dumps(spec("GET /projects", "POST /short-circuits")))

    changed = sync_openapi.sync("v0.2.0", newer)

    assert (root / "spec" / "openapi.public.json").read_text() == newer.read_text()
    assert (root / "spec" / "PLATFORM_REF").read_text() == "v0.2.0\n"
    assert generated == [sync_openapi.OUT]
    assert changed.splitlines() == ["- added `POST /short-circuits`", "- removed `GET /jobs`"]


def test_the_same_routes_still_say_the_schemas_may_have_changed(spec_directory):
    root, _ = spec_directory
    same = root / "same.json"
    same.write_text(json.dumps(spec("GET /jobs", "GET /projects")))
    assert "no route added or removed" in sync_openapi.sync("abc1234", same)


def test_a_file_that_is_not_openapi_changes_nothing(spec_directory):
    root, generated = spec_directory
    before = (root / "spec" / "openapi.public.json").read_text()
    wrong = root / "wrong.json"
    wrong.write_text(json.dumps({"detail": "Not Found"}))

    with pytest.raises(ValueError, match="not an OpenAPI document"):
        sync_openapi.sync("v0.2.0", wrong)

    assert (root / "spec" / "openapi.public.json").read_text() == before
    assert not (root / "spec" / "PLATFORM_REF").exists()
    assert generated == []
