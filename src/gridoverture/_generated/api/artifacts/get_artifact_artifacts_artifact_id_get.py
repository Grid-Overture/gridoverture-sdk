from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx2

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.artifact import Artifact
from ...models.problem import Problem
from typing import cast
from uuid import UUID



def _get_kwargs(
    artifact_id: UUID,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/artifacts/{artifact_id}".format(artifact_id=quote(str(artifact_id), safe=""),),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx2.Response) -> Artifact | Problem | None:
    if response.status_code == 200:
        response_200 = Artifact.from_dict(response.json())



        return response_200

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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx2.Response) -> Response[Artifact | Problem]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    artifact_id: UUID,
    *,
    client: AuthenticatedClient | Client,

) -> Response[Artifact | Problem]:
    """ Get Artifact

    Args:
        artifact_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Artifact | Problem]
     """


    kwargs = _get_kwargs(
        artifact_id=artifact_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    artifact_id: UUID,
    *,
    client: AuthenticatedClient | Client,

) -> Artifact | Problem | None:
    """ Get Artifact

    Args:
        artifact_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Artifact | Problem
     """


    return sync_detailed(
        artifact_id=artifact_id,
client=client,

    ).parsed

async def asyncio_detailed(
    artifact_id: UUID,
    *,
    client: AuthenticatedClient | Client,

) -> Response[Artifact | Problem]:
    """ Get Artifact

    Args:
        artifact_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Artifact | Problem]
     """


    kwargs = _get_kwargs(
        artifact_id=artifact_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    artifact_id: UUID,
    *,
    client: AuthenticatedClient | Client,

) -> Artifact | Problem | None:
    """ Get Artifact

    Args:
        artifact_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Artifact | Problem
     """


    return (await asyncio_detailed(
        artifact_id=artifact_id,
client=client,

    )).parsed
