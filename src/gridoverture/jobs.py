# SPDX-License-Identifier: AGPL-3.0-or-later
"""
A job: work the engine does outside the request, which a study, an import or an edit queues. The
SDK returns it at once; `wait` polls it until it ends and gives back what it made.
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from ._generated.api.jobs import cancel_job_jobs_job_id_cancel_post, get_job_jobs_job_id_get
from ._generated.models import Job as JobBody
from .errors import JobCancelledError, JobFailedError, JobTimeoutError

if TYPE_CHECKING:
    from ._api import Api

T = TypeVar("T")
ENDED = ("done", "failed", "cancelled")
LONGEST_POLL_SECONDS = 5.0
NOT_YET = object()


class Job(Generic[T]):
    """
    A job of the platform's engine, and what it makes once it is done: a Version for an import or
    an edit, a PowerFlowResult, a ValidationResult or an ExportedFile for a study.

    `status`, `progress` and `error` are as the job was last read; `refresh` reads it again.
    """

    def __init__(self, api: Api, body: JobBody, build: Callable[[Api, JobBody], T]):
        self._api = api
        self._body = body
        self._build = build
        self._made: Any = NOT_YET

    @property
    def id(self) -> uuid.UUID:
        """The job's id, which `client.jobs.get` finds it by."""
        return self._body.id

    @property
    def kind(self) -> str:
        """What it does: "import", "edit", "power_flow", "validation" or "export"."""
        return self._body.kind

    @property
    def status(self) -> str:
        """ "pending", "running", "done", "failed" or "cancelled"."""
        return self._body.status

    @property
    def progress(self) -> str | None:
        """The stage it is at: waiting, starting, reading, running or storing."""
        progress = self._body.progress
        return None if progress is None else progress.to_dict().get("stage")

    @property
    def error(self) -> str | None:
        """The engine's message, for a failed job."""
        return self._body.error

    @property
    def params(self) -> dict[str, Any]:
        """What the job was asked to do, as the API keeps it."""
        return self._body.params.to_dict()

    @property
    def done(self) -> bool:
        """Whether it has ended: done, failed or cancelled."""
        return self.status in ENDED

    def refresh(self) -> Job[T]:
        """Read the job again, and return it."""
        self._body = self._api.call(get_job_jobs_job_id_get, job_id=self.id)
        return self

    def wait(self, timeout: float | None = None, poll_interval: float = 0.5) -> T:
        """
        Poll the job until it ends and return what it made.

        It reads the job at once, then after `poll_interval` seconds, doubling each time up to 5.
        A job already waited for returns what it made without asking again.

        Args:
            timeout: The most seconds to wait; None waits as long as it takes.
            poll_interval: The seconds before the second read.

        Raises:
            JobFailedError: The job failed; it carries the engine's message.
            JobCancelledError: The job was cancelled.
            JobTimeoutError: It did not end within `timeout`. The job carries on, and it may be
                waited for again or cancelled.
        """
        if self._made is not NOT_YET:
            return self._made
        deadline = None if timeout is None else time.monotonic() + timeout
        interval = poll_interval
        while not self.refresh().done:
            if deadline is not None:
                left = deadline - time.monotonic()
                if left <= 0:
                    raise JobTimeoutError(self.id, self.kind, timeout)
                time.sleep(min(interval, left))
            else:
                time.sleep(interval)
            interval = min(interval * 2, LONGEST_POLL_SECONDS)
        if self.status == "failed":
            raise JobFailedError(self.id, self.kind, self.error)
        if self.status == "cancelled":
            raise JobCancelledError(self.id, self.kind)
        self._made = self._build(self._api, self._body)
        return self._made

    def cancel(self) -> None:
        """
        Cancel the job: a pending one at once, a running one at the engine's next check, which
        stops its work and stores nothing. It does not wait; `wait` then raises JobCancelledError.

        Raises:
            ConflictError: The job has already ended.
        """
        self._body = self._api.call(cancel_job_jobs_job_id_cancel_post, job_id=self.id)

    def __repr__(self) -> str:
        return f"<Job {self.kind} {self.id} {self.status}>"
