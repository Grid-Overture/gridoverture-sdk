# SPDX-License-Identifier: AGPL-3.0-or-later
"""
The exceptions the SDK raises. An answer of the API that is an error becomes an ApiError carrying
its problem+json (RFC 9457), with the request id that finds it in the API's logs; a job that ends
badly becomes a JobFailedError, a JobCancelledError or, when waiting runs out, a JobTimeoutError.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import Iterable, Mapping
from dataclasses import dataclass


class GridOvertureError(Exception):
    """The base of every exception the SDK raises on its own."""


@dataclass(frozen=True)
class ProblemField:
    """One problem of a request that is not valid: where in it, and what is wrong there."""

    where: str
    """Where in the request, such as `body.edits[0].attribute`."""
    problem: str
    """What is wrong there."""


class ApiError(GridOvertureError):
    """
    The API answered with an error. It carries the API's problem: `status` (the HTTP code),
    `title`, `detail`, `type`, `instance`, `request_id`, `errors`, each problem of a request
    that is not valid, and `code`, the API's name for a refusal such as `needs_role`, or None.
    """

    def __init__(
        self,
        status: int,
        title: str,
        detail: str,
        *,
        type: str = "about:blank",
        instance: str | None = None,
        request_id: str | None = None,
        errors: Iterable[ProblemField] = (),
        code: str | None = None,
    ):
        self.status = status
        self.title = title
        self.detail = detail
        self.type = type
        self.instance = instance
        self.request_id = request_id
        self.errors = list(errors)
        self.code = code
        super().__init__(self._message())

    def _message(self):
        message = f"{self.status} {self.detail}"
        if self.errors:
            message += ": " + "; ".join(f"{field.where}: {field.problem}" for field in self.errors)
        if self.request_id:
            message += f" (request {self.request_id})"
        return message


class InvalidRequestError(ApiError):
    """422: the request is not valid, or cannot be done as it is. `errors` says where, if known."""


class AuthenticationError(ApiError):
    """
    401: the request carries no valid token, or its sign-in is too old (`code` sign_in_required or
    sign_in_again). Set the client's `token`, or GRIDOVERTURE_TOKEN.
    """


class ForbiddenError(ApiError):
    """
    403: the user may not do this: their role is below the one it needs (`code` needs_role), they
    are no member of an organization (not_a_member), or they see what the request names but may
    not change it, such as a project someone else shared.
    """


class NotFoundError(ApiError, LookupError):
    """404: what the request names does not exist, or the user does not see it."""


class ConflictError(ApiError):
    """409: the request clashes with what exists, such as cancelling a job that has ended."""


class RateLimitedError(ApiError):
    """429: the user made too many requests in a minute (`code` too_many_requests). Wait, and try
    again."""


class ServerError(ApiError):
    """5xx: the API, or something in front of it, failed. The request id finds it in the logs."""


ERRORS = {
    401: AuthenticationError,
    403: ForbiddenError,
    404: NotFoundError,
    409: ConflictError,
    422: InvalidRequestError,
    429: RateLimitedError,
}


def error_from(status: int, content: bytes, headers: Mapping[str, str]) -> ApiError:
    """
    The ApiError of an error answer. An answer that is not problem+json, from a proxy for one,
    still becomes one, with its text as the detail.
    """
    error_class = ServerError if status >= 500 else ERRORS.get(status, ApiError)
    request_id = headers.get("x-request-id")
    try:
        body = json.loads(content)
    except ValueError:
        body = None
    if not isinstance(body, dict) or "detail" not in body:
        text = content.decode("utf-8", errors="replace").strip()
        return error_class(
            status, text or f"HTTP {status}", text or f"HTTP {status}", request_id=request_id
        )
    fields = [
        ProblemField(str(item.get("where", "")), str(item.get("problem", "")))
        for item in body.get("errors") or ()
        if isinstance(item, dict)
    ]
    return error_class(
        int(body.get("status", status)),
        str(body.get("title", "")),
        str(body["detail"]),
        type=str(body.get("type", "about:blank")),
        instance=body.get("instance"),
        request_id=body.get("request_id") or request_id,
        errors=fields,
        code=body["code"] if isinstance(body.get("code"), str) else None,
    )


class ProjectNotFoundError(GridOvertureError, LookupError):
    """No project the user sees has the name asked for."""

    def __init__(self, name: str):
        self.name = name
        super().__init__(f"no project named {name!r}")


class ObjectNotFoundError(GridOvertureError, LookupError):
    """No object of a version's model has the class and name asked for."""

    def __init__(self, cim_classes: tuple[str, ...], name: str):
        self.cim_classes = cim_classes
        self.name = name
        super().__init__(f"no {' or '.join(cim_classes)} named {name!r}")


class JobFailedError(GridOvertureError):
    """A job ended failed. `message` is the engine's account of why."""

    def __init__(self, job_id: uuid.UUID, kind: str, message: str | None):
        self.job_id = job_id
        self.kind = kind
        self.message = message
        super().__init__(f"{kind} job {job_id} failed: {message or 'no message'}")


class JobCancelledError(GridOvertureError):
    """A job ended cancelled, so it made nothing."""

    def __init__(self, job_id: uuid.UUID, kind: str):
        self.job_id = job_id
        self.kind = kind
        super().__init__(f"{kind} job {job_id} was cancelled")


class JobTimeoutError(GridOvertureError, TimeoutError):
    """
    A job did not end within the seconds `Job.wait` was given. The job is not cancelled: it carries
    on, and `wait` may be called again.
    """

    def __init__(self, job_id: uuid.UUID, kind: str, timeout: float):
        self.job_id = job_id
        self.kind = kind
        self.timeout = timeout
        super().__init__(f"{kind} job {job_id} did not end within {timeout} seconds")


COMPATIBILITY = "https://github.com/Grid-Overture/gridoverture-sdk#compatibility"


class IncompatibleContractError(GridOvertureError):
    """
    The platform answered with an API contract of another major version than the one this SDK
    implements, so no request is read: install the SDK release that implements its major.
    """

    def __init__(self, platform_contract: str, sdk_contract: str, sdk_version: str):
        self.platform_contract = platform_contract
        self.sdk_contract = sdk_contract
        major = platform_contract.split(".")[0]
        super().__init__(
            f"the platform speaks API contract {platform_contract}, and gridoverture "
            f"{sdk_version} implements contract {sdk_contract}: install the SDK release for "
            f"contract {major}.x that {COMPATIBILITY} lists"
        )


class DeprecatedApiWarning(FutureWarning):
    """
    The platform said, with a Deprecation or Sunset header, that a route the SDK called is
    deprecated or will stop answering. A FutureWarning, so Python shows it by default.
    """
