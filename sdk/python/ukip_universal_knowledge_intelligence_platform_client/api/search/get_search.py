from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    q: str,
    limit: int | Unset = 20,
    skip: int | Unset = 0,
    doc_type: None | str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["q"] = q

    params["limit"] = limit

    params["skip"] = skip

    json_doc_type: None | str | Unset
    if isinstance(doc_type, Unset):
        json_doc_type = UNSET
    else:
        json_doc_type = doc_type
    params["doc_type"] = json_doc_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/search",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = response.json()
        return response_200

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
    q: str,
    limit: int | Unset = 20,
    skip: int | Unset = 0,
    doc_type: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Global Search

     Full-text search across entities, authority records, and annotations.
    Returns ranked results with navigation hrefs.
    Dialect-aware: FTS5 on SQLite, tsvector on PostgreSQL.

    Args:
        q (str):
        limit (int | Unset):  Default: 20.
        skip (int | Unset):  Default: 0.
        doc_type (None | str | Unset): entity | authority | annotation

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        q=q,
        limit=limit,
        skip=skip,
        doc_type=doc_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    q: str,
    limit: int | Unset = 20,
    skip: int | Unset = 0,
    doc_type: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Global Search

     Full-text search across entities, authority records, and annotations.
    Returns ranked results with navigation hrefs.
    Dialect-aware: FTS5 on SQLite, tsvector on PostgreSQL.

    Args:
        q (str):
        limit (int | Unset):  Default: 20.
        skip (int | Unset):  Default: 0.
        doc_type (None | str | Unset): entity | authority | annotation

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        q=q,
        limit=limit,
        skip=skip,
        doc_type=doc_type,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    q: str,
    limit: int | Unset = 20,
    skip: int | Unset = 0,
    doc_type: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Global Search

     Full-text search across entities, authority records, and annotations.
    Returns ranked results with navigation hrefs.
    Dialect-aware: FTS5 on SQLite, tsvector on PostgreSQL.

    Args:
        q (str):
        limit (int | Unset):  Default: 20.
        skip (int | Unset):  Default: 0.
        doc_type (None | str | Unset): entity | authority | annotation

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        q=q,
        limit=limit,
        skip=skip,
        doc_type=doc_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    q: str,
    limit: int | Unset = 20,
    skip: int | Unset = 0,
    doc_type: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Global Search

     Full-text search across entities, authority records, and annotations.
    Returns ranked results with navigation hrefs.
    Dialect-aware: FTS5 on SQLite, tsvector on PostgreSQL.

    Args:
        q (str):
        limit (int | Unset):  Default: 20.
        skip (int | Unset):  Default: 0.
        doc_type (None | str | Unset): entity | authority | annotation

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            q=q,
            limit=limit,
            skip=skip,
            doc_type=doc_type,
        )
    ).parsed
