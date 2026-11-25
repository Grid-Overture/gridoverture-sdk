from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx2

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.job import Job
from ...models.problem import Problem
from ...models.validation_in import ValidationIn
from typing import cast



def _get_kwargs(
    *,
    body: ValidationIn,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/validations",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx2.Response) -> Job | Problem | None:
    if response.status_code == 202:
        response_202 = Job.from_dict(response.json())



        return response_202

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
    *,
    client: AuthenticatedClient | Client,
    body: ValidationIn,

) -> Response[Job | Problem]:
    """ Validation

     Queue a validation of a version or a snapshot. Its result is a ValidationResult.

    Args:
        body (ValidationIn): A validation at the levels asked, worded by where the model's
            solution comes from.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Job | Problem]
     """


    kwargs = _get_kwargs(
        body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient | Client,
    body: ValidationIn,

) -> Job | Problem | None:
    """ Validation

     Queue a validation of a version or a snapshot. Its result is a ValidationResult.

    Args:
        body (ValidationIn): A validation at the levels asked, worded by where the model's
            solution comes from.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Job | Problem
     """


    return sync_detailed(
        client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ValidationIn,

) -> Response[Job | Problem]:
    """ Validation

     Queue a validation of a version or a snapshot. Its result is a ValidationResult.

    Args:
        body (ValidationIn): A validation at the levels asked, worded by where the model's
            solution comes from.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Job | Problem]
     """


    kwargs = _get_kwargs(
        body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: ValidationIn,

) -> Job | Problem | None:
    """ Validation

     Queue a validation of a version or a snapshot. Its result is a ValidationResult.

    Args:
        body (ValidationIn): A validation at the levels asked, worded by where the model's
            solution comes from.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Job | Problem
     """


    return (await asyncio_detailed(
        client=client,
body=body,

    )).parsed
