# SPDX-License-Identifier: AGPL-3.0-or-later
"""
A fake of the API for the SDK's unit tests: canned answers by method and path, behind httpx2's
MockTransport, and every request it was sent, so a test reads what the SDK asked for.
"""

import json
import uuid

import httpx2

API = "http://api.test"
STORAGE = "http://storage.test"
NOW = "2026-11-23T12:00:00Z"


class FakeApi:
    """Answers each (method, path) with its queued answers in turn, repeating the last one."""

    def __init__(self):
        self.answers = {}  # (method, path) -> [httpx2.Response or a function of the request]
        self.requests = []

    def on(self, method, path, *answers):
        self.answers[(method, path)] = list(answers)

    def handle(self, request):
        self.requests.append(request)
        queued = self.answers.get((request.method, request.url.path))
        if not queued:
            return problem(404, f"the fake has no {request.method} {request.url.path}")
        answer = queued.pop(0) if len(queued) > 1 else queued[0]
        return answer(request) if callable(answer) else answer

    def sent(self, method, path):
        """The requests sent to (method, path), in order."""
        return [r for r in self.requests if (r.method, r.url.path) == (method, path)]

    def body(self, method, path, index=-1):
        return json.loads(self.sent(method, path)[index].content)


def ok(body, status=200):
    return httpx2.Response(status, json=body)


def problem(status, detail, errors=None, request_id="req-1"):
    body = {
        "type": "about:blank",
        "title": "Problem",
        "status": status,
        "detail": detail,
        "instance": "/somewhere",
        "request_id": request_id,
    }
    if errors is not None:
        body["errors"] = errors
    return httpx2.Response(
        status,
        content=json.dumps(body).encode(),
        headers={"content-type": "application/problem+json", "x-request-id": request_id},
    )


def stored_file(kind="cgmes", media_type="application/zip"):
    return {
        "id": str(uuid.uuid4()),
        "sha256": "0" * 64,
        "kind": kind,
        "media_type": media_type,
        "size_bytes": 10,
        "created_at": NOW,
    }


def version_body(project_id, version_id=None, parent_id=None, job_id=None):
    return {
        "id": str(version_id or uuid.uuid4()),
        "project_id": str(project_id),
        "parent_id": parent_id and str(parent_id),
        "job_id": job_id and str(job_id),
        "summary": {"buses": 14},
        "file": stored_file(),
        "previews": {},
        "created_at": NOW,
    }


def project_body(name="IEEE 14", project_id=None, latest=None, count=0):
    return {
        "id": str(project_id or uuid.uuid4()),
        "name": name,
        "created_at": NOW,
        "mine": True,
        "shared": False,
        "version_count": count,
        "latest_version": latest,
    }


def job_body(kind, status="pending", result=None, error=None, job_id=None):
    return {
        "id": str(job_id or uuid.uuid4()),
        "kind": kind,
        "status": status,
        "params": {},
        "result": result,
        "error": error,
        "attempts": 0,
        "progress": {"stage": "waiting"},
        "cancel_requested_at": None,
        "created_at": NOW,
        "started_at": None,
        "finished_at": None,
    }


def artifact_body(artifact_id, url):
    return {**stored_file("result"), "id": str(artifact_id), "download_url": url}
