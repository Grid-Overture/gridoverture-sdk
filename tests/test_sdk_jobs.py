# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Jobs and the studies that queue them, against a fake API: what each study sends from its typed
settings, how `wait` polls and ends (done, failed, cancelled, out of time), what `cancel` does, and
the edits a child version is asked with.
"""

import json
import uuid

import httpx2
import pytest
from sdk_fakes import STORAGE, artifact_body, job_body, ok, problem, project_body, version_body

import gridoverture as go


@pytest.fixture
def version(client, api):
    project = project_body()
    body = version_body(project["id"])
    api.on("GET", f"/versions/{body['id']}", ok(body))
    return client.get_version(body["id"])


def queue(api, path, kind, *statuses, result=None, error=None):
    """The fake answers `path` with a pending job, then one answer of it per status in turn."""
    job_id = uuid.uuid4()
    api.on("POST", path, ok(job_body(kind, job_id=job_id), status=202))
    answers = [
        ok(
            job_body(
                kind,
                status,
                result=result if status == "done" else None,
                error=error if status == "failed" else None,
                job_id=job_id,
            )
        )
        for status in statuses
    ]
    api.on("GET", f"/jobs/{job_id}", *answers)
    return job_id


def result_file(api, content):
    """The fake serves `content` as a result artifact's JSON; the artifact's id."""
    artifact_id = uuid.uuid4()
    url = f"{STORAGE}/download/{artifact_id}"
    api.on("GET", f"/artifacts/{artifact_id}", ok(artifact_body(artifact_id, url)))
    api.on("GET", f"/download/{artifact_id}", httpx2.Response(200, content=content))
    return artifact_id


FLOW = {
    "engine": "openloadflow",
    "converged": True,
    "status": "valid",
    "seconds": 0.4,
    "iterations": 3,
    "summary": {"generationMw": 272.4, "loadMw": 259.0, "lossesMw": 13.4},
    "buses": {"n1": {"vPu": 1.06, "angleDeg": 0.0, "name": "Bus 1", "voltageLevel": None}},
    "branches": {},
    "violations": [],
}


def test_a_power_flow_sends_its_settings_and_waits_for_its_result(version, api, no_sleep):
    artifact_id = result_file(api, json.dumps(FLOW).encode())
    result = {"operation": "power_flow", "outputs": {"result": str(artifact_id)}}
    queue(api, "/power-flows", "power_flow", "pending", "running", "running", "done", result=result)

    settings = go.PowerFlowSettings(engine="pandapower", start="flat", controls=True)
    job = version.power_flow(settings)
    flow = job.wait(poll_interval=0.5)

    assert api.body("POST", "/power-flows") == {
        "source": {"version_id": str(version.id)},
        "engine": "pandapower",
        "start": "flat",
        "reactive_limits": True,
        "controls": True,
    }
    assert (flow.converged, flow.status, flow.engine, flow.iterations) == (
        True,
        "valid",
        "openloadflow",
        3,
    )
    assert flow.summary["losses_mw"] == 13.4
    assert flow.buses.rows[0]["v_pu"] == 1.06
    assert no_sleep == [0.5, 1.0, 2.0]
    assert (job.status, job.done) == ("done", True)
    asked = len(api.requests)
    assert job.wait() is flow
    assert len(api.requests) == asked


def test_the_power_flow_engine_is_left_to_the_api_by_default(version, api):
    queue(api, "/power-flows", "power_flow", "pending")
    version.power_flow()
    assert "engine" not in api.body("POST", "/power-flows")


def test_polling_backs_off_to_five_seconds(version, api, no_sleep):
    queue(api, "/power-flows", "power_flow", *["running"] * 6, "failed", error="no")
    with pytest.raises(go.JobFailedError):
        version.power_flow().wait(poll_interval=1.0)
    assert no_sleep == [1.0, 2.0, 4.0, 5.0, 5.0, 5.0]


def test_a_failed_job_raises_with_the_engines_message(version, api, no_sleep):
    job_id = queue(
        api, "/validations", "validation", "running", "failed", error="source.raw cannot be read"
    )
    job = version.validate()
    with pytest.raises(go.JobFailedError) as raised:
        job.wait()
    assert (raised.value.job_id, raised.value.kind, raised.value.message) == (
        job_id,
        "validation",
        "source.raw cannot be read",
    )
    assert job.error == "source.raw cannot be read"
    assert str(job_id) in str(raised.value)


def test_a_job_out_of_time_raises_and_carries_on(version, api, no_sleep):
    job_id = queue(api, "/exports", "export", *["running"] * 10, "cancelled")
    job = version.export("cgmes")
    with pytest.raises(go.JobTimeoutError) as raised:
        job.wait(timeout=3, poll_interval=1)
    assert isinstance(raised.value, TimeoutError)
    assert (raised.value.job_id, raised.value.timeout) == (job_id, 3)
    assert api.sent("POST", f"/jobs/{job_id}/cancel") == []
    assert job.status == "running"


def test_a_cancel_asks_the_api_and_the_wait_then_raises(version, api, no_sleep):
    job_id = queue(api, "/exports", "export", "cancelled")
    api.on(
        "POST",
        f"/jobs/{job_id}/cancel",
        ok(job_body("export", "cancelled", job_id=job_id)),
        problem(409, f"job {job_id} has ended"),
    )
    job = version.export("cgmes")
    assert job.cancel() is None
    assert job.status == "cancelled"
    with pytest.raises(go.JobCancelledError):
        job.wait()
    with pytest.raises(go.ConflictError):
        job.cancel()


def test_a_job_is_found_by_its_id_and_its_result_by_its_kind(client, api, no_sleep):
    artifact_id = result_file(api, json.dumps({"counts": {"error": 0}, "findings": []}).encode())
    job_id = uuid.uuid4()
    result = {"operation": "validation", "outputs": {"result": str(artifact_id)}}
    body = job_body("validation", "done", result=result, job_id=job_id)
    api.on("GET", f"/jobs/{job_id}", ok(body))
    api.on("GET", "/jobs", ok([body]))
    assert client.jobs.get(job_id).wait().passed
    assert [job.id for job in client.jobs.list()] == [job_id]


def test_validation_and_export_send_their_settings(version, api):
    queue(api, "/validations", "validation", "pending")
    queue(api, "/exports", "export", "pending")
    version.validate()
    version.validate(go.ValidationSettings(levels=["physics"]))
    version.export("cgmes")
    version.export(go.ExportSettings("raw", raw_version=35))
    version.export(go.ExportSettings("cgmes", packaging="folder"))
    source = {"version_id": str(version.id)}
    assert [api.body("POST", "/validations", i) for i in (0, 1)] == [
        {"source": source, "levels": ["structure", "consistency", "physics"]},
        {"source": source, "levels": ["physics"]},
    ]
    assert [api.body("POST", "/exports", i) for i in (0, 1, 2)] == [
        {"source": source, "format": "cgmes", "version": 33},
        {"source": source, "format": "raw", "version": 35},
        {"source": source, "format": "cgmes", "version": 33, "packaging": "folder"},
    ]


def test_an_export_downloads_its_file(version, api, tmp_path, no_sleep):
    report = result_file(api, json.dumps({"format": "cgmes", "lost": []}).encode())
    exported = result_file(api, b"PK zip bytes")
    result = {"operation": "export", "outputs": {"result": str(report), "file": str(exported)}}
    queue(api, "/exports", "export", "done", result=result)
    file = version.export("cgmes").wait()
    assert (file.format, file.artifact_id, file.report) == (
        "cgmes",
        exported,
        {"format": "cgmes", "lost": []},
    )
    written = file.download(tmp_path / "out.zip")
    assert written.read_bytes() == file.content() == b"PK zip bytes"


@pytest.mark.parametrize(
    "build",
    [
        lambda: go.PowerFlowSettings(engine="dynawo"),
        lambda: go.PowerFlowSettings(start="warm"),
        lambda: go.PowerFlowSettings(controls="yes"),
        lambda: go.ValidationSettings(levels=[]),
        lambda: go.ValidationSettings(levels=["grammar"]),
        lambda: go.ExportSettings("psse"),
        lambda: go.ExportSettings("raw", raw_version=34),
        lambda: go.ExportSettings("cgmes", packaging="tarball"),
    ],
)
def test_settings_outside_the_allowed_values_are_refused_before_any_request(build):
    with pytest.raises(ValueError):
        build()


def test_an_edit_makes_a_child_version(version, api, no_sleep):
    child = version_body(version.project_id, parent_id=version.id)
    api.on("GET", f"/versions/{child['id']}", ok(child))
    queue(
        api,
        f"/projects/{version.project_id}/versions",
        "edit",
        "done",
        result={"version_id": child["id"]},
    )
    edits = [
        go.SetAttribute("load-1", "EnergyConsumer.p", 45.0),
        go.AddObject("EnergyConsumer", "load-2", {"IdentifiedObject.name": "New load"}),
        go.RemoveObject("line-3", dependents=True),
    ]
    edited = version.edit(edits).wait()
    assert edited.parent_id == version.id
    assert api.body("POST", f"/projects/{version.project_id}/versions") == {
        "parent_id": str(version.id),
        "edits": [
            {"op": "set", "mrid": "load-1", "attribute": "EnergyConsumer.p", "value": 45.0},
            {
                "op": "add",
                "cim_class": "EnergyConsumer",
                "mrid": "load-2",
                "values": {"IdentifiedObject.name": "New load"},
            },
            {"op": "remove", "mrid": "line-3", "dependents": True},
        ],
    }
    with pytest.raises(ValueError, match="at least one edit"):
        version.edit([])


def test_a_version_downloads_its_model(version, api, tmp_path):
    url = f"{STORAGE}/download/model"
    api.on("GET", f"/artifacts/{version.file.id}", ok(artifact_body(version.file.id, url)))
    api.on("GET", "/download/model", httpx2.Response(200, content=b"PK cgmes"))
    assert version.download(tmp_path / "model.zip").read_bytes() == b"PK cgmes"
