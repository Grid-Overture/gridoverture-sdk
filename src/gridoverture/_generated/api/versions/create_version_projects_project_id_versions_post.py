from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx2

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.job import Job
from ...models.problem import Problem
from ...models.version_in import VersionIn
from typing import cast
from uuid import UUID



def _get_kwargs(
    project_id: UUID,
    *,
    body: VersionIn,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/projects/{project_id}/versions".format(project_id=quote(str(project_id), safe=""),),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx2.Response) -> Job | Problem | None:
    if response.status_code == 202:
        response_202 = Job.from_dict(response.json())



        return response_202

    if response.status_code == 403:
        response_403 = Problem.from_dict(response.json())



        return response_403

    if response.status_code == 404:
        response_404 = Problem.from_dict(response.json())



        return response_404

    if response.status_code == 422:
        response_422 = Problem.from_dict(response.json())



        return response_422

    if response.status_code == 500:
        response_500 = Problem.from_dict(response.json())



        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx2.Response) -> Response[Job | Problem]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: VersionIn,

) -> Response[Job | Problem]:
    """ Create Version

     Queue the job that makes a version: an import of an upload, or an edit of a version. The job
    is launched once its row is committed (docs/adr/0004); a launch that fails leaves it pending
    for the scheduler (docs/adr/0007).

    Args:
        project_id (UUID):
        body (VersionIn): A version from an uploaded file in a format the converter reads
            (`artifact_id` and `format`),
            or from a version of the same project and CIM edits to it (`parent_id` and `edits`). A
            CGMES
            model or a pf2xml export is uploaded as a zip of its files. `time_zone` is the
            requester's, an
            IANA name ("America/Santiago"), which the conversion report is dated in; UTC when it is
            not
            given or not known.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Job | Problem]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: VersionIn,

) -> Job | Problem | None:
    """ Create Version

     Queue the job that makes a version: an import of an upload, or an edit of a version. The job
    is launched once its row is committed (docs/adr/0004); a launch that fails leaves it pending
    for the scheduler (docs/adr/0007).

    Args:
        project_id (UUID):
        body (VersionIn): A version from an uploaded file in a format the converter reads
            (`artifact_id` and `format`),
            or from a version of the same project and CIM edits to it (`parent_id` and `edits`). A
            CGMES
            model or a pf2xml export is uploaded as a zip of its files. `time_zone` is the
            requester's, an
            IANA name ("America/Santiago"), which the conversion report is dated in; UTC when it is
            not
            given or not known.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Job | Problem
     """


    return sync_detailed(
        project_id=project_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    project_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: VersionIn,

) -> Response[Job | Problem]:
    """ Create Version

     Queue the job that makes a version: an import of an upload, or an edit of a version. The job
    is launched once its row is committed (docs/adr/0004); a launch that fails leaves it pending
    for the scheduler (docs/adr/0007).

    Args:
        project_id (UUID):
        body (VersionIn): A version from an uploaded file in a format the converter reads
            (`artifact_id` and `format`),
            or from a version of the same project and CIM edits to it (`parent_id` and `edits`). A
            CGMES
            model or a pf2xml export is uploaded as a zip of its files. `time_zone` is the
            requester's, an
            IANA name ("America/Santiago"), which the conversion report is dated in; UTC when it is
            not
            given or not known.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Job | Problem]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: VersionIn,

) -> Job | Problem | None:
    """ Create Version

     Queue the job that makes a version: an import of an upload, or an edit of a version. The job
    is launched once its row is committed (docs/adr/0004); a launch that fails leaves it pending
    for the scheduler (docs/adr/0007).

    Args:
        project_id (UUID):
        body (VersionIn): A version from an uploaded file in a format the converter reads
            (`artifact_id` and `format`),
            or from a version of the same project and CIM edits to it (`parent_id` and `edits`). A
            CGMES
            model or a pf2xml export is uploaded as a zip of its files. `time_zone` is the
            requester's, an
            IANA name ("America/Santiago"), which the conversion report is dated in; UTC when it is
            not
            given or not known.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Job | Problem
     """


    return (await asyncio_detailed(
        project_id=project_id,
client=client,
body=body,

    )).parsed
