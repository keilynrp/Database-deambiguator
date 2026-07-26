from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.author_resolve_request import AuthorResolveRequest
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    *,
    body: AuthorResolveRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/authority/authors/resolve",
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
    body: AuthorResolveRequest,
) -> Response[Any | HTTPValidationError]:
    """Resolve Author Profile

     Author-only adaptive resolution baseline.

    Reuses the existing authority resolver/scoring pipeline, then adds a
    deterministic routing heuristic that classifies the case as fast/hybrid/LLM
    or manual review. The response keeps all persisted records for auditability.

    Args:
        body (AuthorResolveRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
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
    client: AuthenticatedClient,
    body: AuthorResolveRequest,
) -> Any | HTTPValidationError | None:
    """Resolve Author Profile

     Author-only adaptive resolution baseline.

    Reuses the existing authority resolver/scoring pipeline, then adds a
    deterministic routing heuristic that classifies the case as fast/hybrid/LLM
    or manual review. The response keeps all persisted records for auditability.

    Args:
        body (AuthorResolveRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: AuthorResolveRequest,
) -> Response[Any | HTTPValidationError]:
    """Resolve Author Profile

     Author-only adaptive resolution baseline.

    Reuses the existing authority resolver/scoring pipeline, then adds a
    deterministic routing heuristic that classifies the case as fast/hybrid/LLM
    or manual review. The response keeps all persisted records for auditability.

    Args:
        body (AuthorResolveRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: AuthorResolveRequest,
) -> Any | HTTPValidationError | None:
    """Resolve Author Profile

     Author-only adaptive resolution baseline.

    Reuses the existing authority resolver/scoring pipeline, then adds a
    deterministic routing heuristic that classifies the case as fast/hybrid/LLM
    or manual review. The response keeps all persisted records for auditability.

    Args:
        body (AuthorResolveRequest):

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
        )
    ).parsed
