from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx2

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.problem import Problem
from ...models.version import Version
from typing import cast
from uuid import UUID



def _get_kwargs(
    project_id: UUID,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/projects/{project_id}/versions".format(project_id=quote(str(project_id), safe=""),),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx2.Response) -> Problem | list[Version] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = Version.from_dict(response_200_item_data)



            response_200.append(response_200_item)

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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx2.Response) -> Response[Problem | list[Version]]:
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

) -> Response[Problem | list[Version]]:
    """ List Versions

     A project's versions, the newest first.

    Args:
        project_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Problem | list[Version]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: UUID,
    *,
    client: AuthenticatedClient | Client,

) -> Problem | list[Version] | None:
    """ List Versions

     A project's versions, the newest first.

    Args:
        project_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Problem | list[Version]
     """


    return sync_detailed(
        project_id=project_id,
client=client,

    ).parsed

async def asyncio_detailed(
    project_id: UUID,
    *,
    client: AuthenticatedClient | Client,

) -> Response[Problem | list[Version]]:
    """ List Versions

     A project's versions, the newest first.

    Args:
        project_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Problem | list[Version]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: UUID,
    *,
    client: AuthenticatedClient | Client,

) -> Problem | list[Version] | None:
    """ List Versions

     A project's versions, the newest first.

    Args:
        project_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Problem | list[Version]
     """


    return (await asyncio_detailed(
        project_id=project_id,
client=client,

    )).parsed
