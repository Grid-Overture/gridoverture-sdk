# SPDX-License-Identifier: AGPL-3.0-or-later
"""
The Client against a fake API: where it sends requests and with which token, how it finds and
makes projects and versions, how a file reaches storage through a signed URL without the token,
and how an error answer becomes an exception that carries the API's problem.
"""

import hashlib
import io
import pathlib
import uuid
import zipfile

import httpx2
import pytest
from sdk_fakes import (
    API,
    STORAGE,
    job_body,
    ok,
    problem,
    project_body,
    version_body,
)

import gridoverture as go
from gridoverture.client import format_of


def mocked(api, **arguments):
    transport = httpx2.MockTransport(api.handle)
    return go.Client(
        http_client=httpx2.Client(transport=transport, base_url=arguments.pop("base_url", API)),
        files_client=httpx2.Client(transport=transport),
        **arguments,
    )


def test_the_token_comes_from_the_argument_or_the_environment(api, monkeypatch):
    api.on("GET", "/projects", ok([]))
    monkeypatch.setenv("GRIDOVERTURE_TOKEN", "from-env")
    mocked(api, token="from-argument").projects.list()
    mocked(api).projects.list()
    monkeypatch.delenv("GRIDOVERTURE_TOKEN")
    mocked(api).projects.list()
    sent = [request.headers.get("authorization") for request in api.requests]
    assert sent == ["Bearer from-argument", "Bearer from-env", None]


def test_the_address_comes_from_the_argument_the_environment_or_a_local_platform(monkeypatch):
    monkeypatch.delenv("GRIDOVERTURE_URL", raising=False)
    assert go.Client().base_url == "http://localhost:8780"  # a local gateway
    monkeypatch.setenv("GRIDOVERTURE_URL", "https://api.example.test/")
    assert go.Client().base_url == "https://api.example.test"
    assert go.Client("http://other.test").base_url == "http://other.test"


def test_projects_are_listed_found_by_name_and_made(client, api):
    first, second = project_body("IEEE 14"), project_body("IEEE 14")
    api.on("GET", "/projects", ok([first, project_body("Other"), second]))
    api.on("POST", "/projects", ok(project_body("New"), status=201))

    assert [project.name for project in client.projects.list()] == ["IEEE 14", "Other", "IEEE 14"]
    found = client.projects.get("IEEE 14")
    assert (found.id, found.mine, found.version_count) == (uuid.UUID(first["id"]), True, 0)
    with pytest.raises(go.ProjectNotFoundError) as missing:
        client.projects.get("Nope")
    assert isinstance(missing.value, LookupError)
    assert client.projects.create("New").name == "New"
    assert api.body("POST", "/projects") == {"name": "New"}


def test_a_project_lists_its_versions_and_its_latest(client, api):
    project = project_body()
    newest, oldest = version_body(project["id"]), version_body(project["id"])
    api.on("GET", f"/projects/{project['id']}", ok(project))
    api.on("GET", f"/projects/{project['id']}/versions", ok([newest, oldest]), ok([]))
    found = client.projects.get_by_id(project["id"])
    assert [str(v.id) for v in found.versions.list()] == [newest["id"], oldest["id"]]
    assert found.versions.latest() is None
    assert found.versions.list() == []


def test_an_error_carries_the_apis_problem(client, api):
    fields = [{"where": "body.name", "problem": "String should have at least 1 character"}]
    api.on("POST", "/projects", problem(422, "the request is not valid", fields, "abc123"))
    with pytest.raises(go.InvalidRequestError) as raised:
        client.projects.create("")
    error = raised.value
    assert isinstance(error, go.ApiError)
    assert (error.status, error.detail, error.request_id) == (
        422,
        "the request is not valid",
        "abc123",
    )
    assert error.errors == [go.ProblemField("body.name", "String should have at least 1 character")]
    assert str(error) == (
        "422 the request is not valid: body.name: String should have at least 1 character"
        " (request abc123)"
    )


@pytest.mark.parametrize(
    ("status", "error_class"),
    [
        (401, go.AuthenticationError),
        (403, go.ForbiddenError),
        (404, go.NotFoundError),
        (429, go.RateLimitedError),
        (409, go.ConflictError),
        (500, go.ServerError),
        (503, go.ServerError),
        (418, go.ApiError),
    ],
)
def test_each_status_has_its_error(client, api, status, error_class):
    api.on("GET", "/projects", problem(status, "it went wrong"))
    with pytest.raises(error_class) as raised:
        client.projects.list()
    assert type(raised.value) is error_class
    assert raised.value.status == status


def test_an_answer_that_is_no_problem_still_becomes_an_error(client, api):
    api.on(
        "GET",
        "/projects",
        httpx2.Response(502, text="Bad Gateway", headers={"x-request-id": "edge-7"}),
    )
    with pytest.raises(go.ServerError) as raised:
        client.projects.list()
    assert (raised.value.status, raised.value.detail, raised.value.request_id) == (
        502,
        "Bad Gateway",
        "edge-7",
    )
    assert isinstance(go.NotFoundError(404, "Not Found", "no project"), LookupError)


def queue_import(api, project, data):
    """The fake's answers to an upload of `data` and the import of it as a version."""
    upload_id, artifact_id, job_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    version = version_body(project["id"], job_id=job_id)
    api.on(
        "POST",
        "/uploads",
        ok(
            {
                "upload_id": str(upload_id),
                "url": f"{STORAGE}/bucket/upload/{upload_id}",
                "headers": {"x-goog-content-sha256": "UNSIGNED-PAYLOAD"},
                "expires_at": "2026-11-23T13:00:00Z",
            },
            status=201,
        ),
    )
    api.on("PUT", f"/bucket/upload/{upload_id}", httpx2.Response(200))
    api.on(
        "POST",
        f"/uploads/{upload_id}/complete",
        ok({**version["file"], "id": str(artifact_id), "download_url": "-"}, status=201),
    )
    done = {"version_id": version["id"], "report_artifact_id": str(uuid.uuid4())}
    api.on(
        "POST",
        f"/projects/{project['id']}/versions",
        ok(job_body("import", job_id=job_id), status=202),
    )
    api.on("GET", f"/jobs/{job_id}", ok(job_body("import", "done", result=done, job_id=job_id)))
    api.on("GET", f"/versions/{version['id']}", ok(version))
    return upload_id, artifact_id, version


def test_a_file_is_uploaded_without_the_token_and_imported(client, api, tmp_path, no_sleep):
    project = project_body()
    api.on("GET", "/projects", ok([project]))
    data = b"function mpc = case14\n"
    upload_id, artifact_id, version = queue_import(api, project, data)
    path = tmp_path / "case14.m"
    path.write_bytes(data)

    job = client.projects.get("IEEE 14").versions.import_file(path)
    assert job.kind == "import"
    imported = job.wait()

    assert (str(imported.id), imported.summary) == (version["id"], {"buses": 14})
    (put,) = api.sent("PUT", f"/bucket/upload/{upload_id}")
    assert put.content == data
    assert put.headers["x-goog-content-sha256"] == "UNSIGNED-PAYLOAD"
    assert "authorization" not in put.headers
    assert api.body("POST", f"/uploads/{upload_id}/complete")["sha256"] == (
        hashlib.sha256(data).hexdigest()
    )
    assert api.body("POST", f"/projects/{project['id']}/versions") == {
        "artifact_id": str(artifact_id),
        "format": "matpower",
    }


def test_a_folder_is_zipped_and_needs_its_format(client, api, tmp_path, no_sleep):
    project = project_body()
    api.on("GET", "/projects", ok([project]))
    folder = tmp_path / "model"
    folder.mkdir()
    (folder / "EQ.xml").write_text("<rdf/>")
    (folder / "SSH.xml").write_text("<rdf/>")
    upload_id, _, _ = queue_import(api, project, b"")
    versions = client.projects.get("IEEE 14").versions

    with pytest.raises(ValueError, match="format"):
        versions.import_file(folder)
    versions.import_file(folder, format="cgmes").wait()

    (put,) = api.sent("PUT", f"/bucket/upload/{upload_id}")
    with zipfile.ZipFile(io.BytesIO(put.content)) as bundle:
        assert sorted(bundle.namelist()) == ["EQ.xml", "SSH.xml"]
    assert api.body("POST", f"/projects/{project['id']}/versions")["format"] == "cgmes"


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("case.raw", "raw"),
        ("case14.m", "matpower"),
        ("grid.veragrid", "veragrid"),
        ("net.json", "pandapower"),
        ("ieee14.cdf", "cdf"),
    ],
)
def test_the_format_is_told_from_the_suffix(name, expected):
    assert format_of(pathlib.Path(name), None) == expected


@pytest.mark.parametrize("name", ["model.zip", "notes.txt", "case"])
def test_a_suffix_that_does_not_tell_the_format_asks_for_it(client, api, tmp_path, name):
    project = project_body()
    api.on("GET", "/projects", ok([project]))
    path = tmp_path / name
    path.write_bytes(b"x")
    with pytest.raises(ValueError, match="format"):
        client.projects.get("IEEE 14").versions.import_file(path)
    with pytest.raises(ValueError, match="not a format"):
        client.projects.get("IEEE 14").versions.import_file(path, format="psse")
    assert [request.url.path for request in api.requests] == ["/projects", "/projects"]


def test_a_refusal_carries_the_apis_code(client, api):
    body = {"status": 403, "title": "Forbidden", "detail": "this needs the editor role"}
    api.on("GET", "/projects", httpx2.Response(403, json=body | {"code": "needs_role"}))
    with pytest.raises(go.ForbiddenError) as raised:
        client.projects.list()
    assert raised.value.code == "needs_role"
    api.on("GET", "/projects", httpx2.Response(403, json=body))
    with pytest.raises(go.ForbiddenError) as raised:
        client.projects.list()
    assert raised.value.code is None
