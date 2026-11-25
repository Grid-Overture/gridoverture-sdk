# SPDX-License-Identifier: AGPL-3.0-or-later
"""The SDK's unit tests speak to a fake API (sdk_fakes), never to a server."""

import httpx2
import pytest
from sdk_fakes import API, FakeApi

import gridoverture as go


@pytest.fixture
def api():
    return FakeApi()


@pytest.fixture
def client(api, monkeypatch):
    """A Client that speaks to the fake API, for both the API and the signed URLs."""
    monkeypatch.delenv("GRIDOVERTURE_TOKEN", raising=False)
    monkeypatch.delenv("GRIDOVERTURE_URL", raising=False)
    transport = httpx2.MockTransport(api.handle)
    with go.Client(
        API,
        token="secret",
        http_client=httpx2.Client(transport=transport, base_url=API),
        files_client=httpx2.Client(transport=transport),
    ) as client:
        yield client


@pytest.fixture
def no_sleep(monkeypatch):
    """Polls without waiting: time moves only by the sleeps asked for. The seconds slept."""
    slept = []
    clock = [0.0]

    def sleep(seconds):
        slept.append(seconds)
        clock[0] += seconds

    monkeypatch.setattr("gridoverture.jobs.time.sleep", sleep)
    monkeypatch.setattr("gridoverture.jobs.time.monotonic", lambda: clock[0])
    return slept
