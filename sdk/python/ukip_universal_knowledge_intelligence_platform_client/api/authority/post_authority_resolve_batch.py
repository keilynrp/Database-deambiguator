from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.batch_resolve_request import BatchResolveRequest
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: BatchResolveRequest,
    sync: bool | Unset = False,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["sync"] = sync

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/authority/resolve/batch",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | None:
    if response.status_code == 201:
        response_201 = response.json()
        return response_201

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: BatchResolveRequest,
    sync: bool | Unset = False,
) -> Response[Any | HTTPValidationError]:
    """Resolve Authority Batch

     Resolve all distinct values of a field against external authority sources.

    Default mode enqueues an async ``AuthorityResolveJob`` and returns a job id;
    poll ``GET /authority/jobs/{job_id}`` for progress. Pass ``?sync=true`` to
    run inline and receive the resolved records in the response (legacy shape).

    Args:
        sync (bool | Unset): Run inline (legacy) instead of enqueuing an async job Default: False.
        body (BatchResolveRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
        sync=sync,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: BatchResolveRequest,
    sync: bool | Unset = False,
) -> Any | HTTPValidationError | None:
    """Resolve Authority Batch

     Resolve all distinct values of a field against external authority sources.

    Default mode enqueues an async ``AuthorityResolveJob`` and returns a job id;
    poll ``GET /authority/jobs/{job_id}`` for progress. Pass ``?sync=true`` to
    run inline and receive the resolved records in the response (legacy shape).

    Args:
        sync (bool | Unset): Run inline (legacy) instead of enqueuing an async job Default: False.
        body (BatchResolveRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        body=body,
        sync=sync,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: BatchResolveRequest,
    sync: bool | Unset = False,
) -> Response[Any | HTTPValidationError]:
    """Resolve Authority Batch

     Resolve all distinct values of a field against external authority sources.

    Default mode enqueues an async ``AuthorityResolveJob`` and returns a job id;
    poll ``GET /authority/jobs/{job_id}`` for progress. Pass ``?sync=true`` to
    run inline and receive the resolved records in the response (legacy shape).

    Args:
        sync (bool | Unset): Run inline (legacy) instead of enqueuing an async job Default: False.
        body (BatchResolveRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
        sync=sync,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: BatchResolveRequest,
    sync: bool | Unset = False,
) -> Any | HTTPValidationError | None:
    """Resolve Authority Batch

     Resolve all distinct values of a field against external authority sources.

    Default mode enqueues an async ``AuthorityResolveJob`` and returns a job id;
    poll ``GET /authority/jobs/{job_id}`` for progress. Pass ``?sync=true`` to
    run inline and receive the resolved records in the response (legacy shape).

    Args:
        sync (bool | Unset): Run inline (legacy) instead of enqueuing an async job Default: False.
        body (BatchResolveRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            sync=sync,
        )
    ).parsed
