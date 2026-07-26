from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/openalex-lake/status",
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | None:
    if response.status_code == 200:
        return None

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[Any]:
    r"""Get Openalex Lake Status

     Ingestion status: phase, backfill progress, table counts, quota snapshot.

    Read-only against the lake DuckDB file; safe to call while a pull is
    running (reports `{\"lake\": \"locked\"}` instead of erroring) or before the
    first pull has ever run (`{\"lake\": \"not_initialized\"}`). `total_issns`
    (the intended backfill scope) comes from distinct journal_metrics.issn_l
    so the dashboard can render a completion percentage.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[Any]:
    r"""Get Openalex Lake Status

     Ingestion status: phase, backfill progress, table counts, quota snapshot.

    Read-only against the lake DuckDB file; safe to call while a pull is
    running (reports `{\"lake\": \"locked\"}` instead of erroring) or before the
    first pull has ever run (`{\"lake\": \"not_initialized\"}`). `total_issns`
    (the intended backfill scope) comes from distinct journal_metrics.issn_l
    so the dashboard can render a completion percentage.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
