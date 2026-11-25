# SPDX-License-Identifier: AGPL-3.0-or-later
"""
The API contract the SDK implements, against the one the platform answers with in its
Gridoverture-Contract header: another major fails with both versions named, a newer minor works,
and a Deprecation or Sunset header becomes a warning with its dates.
"""

import json
import pathlib
import warnings

import httpx2
import pytest
from sdk_fakes import STORAGE, project_body

import gridoverture as go

SPEC = pathlib.Path(__file__).resolve().parents[1] / "spec" / "openapi.public.json"
MAJOR, MINOR, _ = (int(part) for part in go.CONTRACT.split("."))


def answer(body, status=200, **headers):
    return httpx2.Response(
        status, json=body, headers={name.replace("_", "-"): v for name, v in headers.items()}
    )


def test_the_contract_is_the_version_of_the_spec_the_client_was_generated_from():
    assert json.loads(SPEC.read_text(encoding="utf-8"))["info"]["version"] == go.CONTRACT


def test_a_newer_minor_of_the_same_major_works(api, client):
    newer = f"{MAJOR}.{MINOR + 3}.1"
    api.on("GET", "/projects", answer([project_body()], Gridoverture_Contract=newer))
    assert len(client.projects.list()) == 1


def test_a_platform_without_the_header_is_not_checked(api, client):
    api.on("GET", "/projects", answer([project_body()]))
    assert len(client.projects.list()) == 1


def test_another_major_fails_naming_both_contracts_and_what_to_install(api, client):
    other = f"{MAJOR + 1}.0.0"
    api.on("GET", "/projects", answer([project_body()], Gridoverture_Contract=other))

    with pytest.raises(go.IncompatibleContractError) as refused:
        client.projects.list()

    error = refused.value
    assert isinstance(error, go.GridOvertureError)
    assert (error.platform_contract, error.sdk_contract) == (other, go.CONTRACT)
    message = str(error)
    assert other in message and go.CONTRACT in message and go.__version__ in message
    assert f"contract {MAJOR + 1}.x" in message
    assert "github.com/Grid-Overture/gridoverture-sdk#compatibility" in message


def test_an_older_major_fails_too(api, client):
    older = f"{MAJOR - 1}.9.0" if MAJOR > 0 else "-1.0.0"
    api.on("GET", "/projects", answer([], Gridoverture_Contract=older))
    if MAJOR == 0:
        assert client.projects.list() == []  # not semver: not checked
    else:
        with pytest.raises(go.IncompatibleContractError):
            client.projects.list()


def test_the_contract_is_checked_before_an_error_answer_is_read(api, client):
    api.on(
        "GET",
        "/projects",
        answer({"detail": "no such route"}, 404, Gridoverture_Contract=f"{MAJOR + 1}.0.0"),
    )
    with pytest.raises(go.IncompatibleContractError):
        client.projects.list()


def test_a_platform_in_transition_names_both_majors(api, client):
    both = f"{MAJOR}.4.0, {MAJOR + 1}.0.0"
    api.on("GET", "/projects", answer([], Gridoverture_Contract=both))
    assert client.projects.list() == []


def test_a_header_that_is_not_a_version_is_not_checked(api, client):
    api.on("GET", "/projects", answer([], Gridoverture_Contract="latest"))
    assert client.projects.list() == []


def test_a_deprecated_route_warns_with_its_dates_and_link(api, client):
    api.on(
        "GET",
        "/projects",
        answer(
            [],
            Gridoverture_Contract=go.CONTRACT,
            Deprecation="@1798761600",  # RFC 9745: 2027-01-01T00:00:00Z
            Sunset="Wed, 30 Jun 2027 23:59:59 GMT",  # RFC 8594
            Link='<https://docs.example/v1>; rel="deprecation"',
        ),
    )
    with pytest.warns(go.DeprecatedApiWarning) as caught:
        client.projects.list()

    (warning,) = caught
    message = str(warning.message)
    assert "GET /projects" in message
    assert "2027-01-01" in message and "2027-06-30" in message
    assert "https://docs.example/v1" in message


def test_a_sunset_alone_warns_too(api, client):
    api.on("GET", "/projects", answer([], Sunset="Wed, 30 Jun 2027 23:59:59 GMT"))
    with pytest.warns(go.DeprecatedApiWarning, match="2027-06-30"):
        client.projects.list()


def test_a_deprecation_warns_once_per_client(api, client):
    api.on("GET", "/projects", answer([], Deprecation="@1798761600"))
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        client.projects.list()
        client.projects.list()
    assert len([w for w in caught if issubclass(w.category, go.DeprecatedApiWarning)]) == 1


def test_a_deprecation_warning_is_shown_by_default():
    assert issubclass(go.DeprecatedApiWarning, FutureWarning)


def test_storage_answers_are_not_the_platforms_contract(api, client):
    api.on(
        "GET",
        "/somewhere",
        answer({}, Gridoverture_Contract=f"{MAJOR + 1}.0.0"),
    )
    files = client._api.files
    assert files.get(f"{STORAGE}/somewhere").status_code == 200
