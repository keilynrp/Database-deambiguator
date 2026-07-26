from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.coauthor_backfill_request import CoauthorBackfillRequest
from ...models.coauthor_backfill_response import CoauthorBackfillResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    *,
    body: CoauthorBackfillRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/admin/data-fixes/coauthor-edges",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CoauthorBackfillResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = CoauthorBackfillResponse.from_dict(response.json())

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
) -> Response[CoauthorBackfillResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: CoauthorBackfillRequest,
) -> Response[CoauthorBackfillResponse | HTTPValidationError]:
    """Backfill CO_AUTHOR edges from enrichment_authors lists

     Materializes the coauthorship graph for entities enriched before the
    extraction hook landed in enrichment_worker. Idempotent (upserts on
    ``relation_type='CO_AUTHOR'`` + ``notes='A||B'``); pass ``reset=True``
    when you want a fresh start.

    Args:
        body (CoauthorBackfillRequest): Inputs for the CO_AUTHOR edge backfill.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CoauthorBackfillResponse | HTTPValidationError]
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
    body: CoauthorBackfillRequest,
) -> CoauthorBackfillResponse | HTTPValidationError | None:
    """Backfill CO_AUTHOR edges from enrichment_authors lists

     Materializes the coauthorship graph for entities enriched before the
    extraction hook landed in enrichment_worker. Idempotent (upserts on
    ``relation_type='CO_AUTHOR'`` + ``notes='A||B'``); pass ``reset=True``
    when you want a fresh start.

    Args:
        body (CoauthorBackfillRequest): Inputs for the CO_AUTHOR edge backfill.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CoauthorBackfillResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: CoauthorBackfillRequest,
) -> Response[CoauthorBackfillResponse | HTTPValidationError]:
    """Backfill CO_AUTHOR edges from enrichment_authors lists

     Materializes the coauthorship graph for entities enriched before the
    extraction hook landed in enrichment_worker. Idempotent (upserts on
    ``relation_type='CO_AUTHOR'`` + ``notes='A||B'``); pass ``reset=True``
    when you want a fresh start.

    Args:
        body (CoauthorBackfillRequest): Inputs for the CO_AUTHOR edge backfill.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CoauthorBackfillResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: CoauthorBackfillRequest,
) -> CoauthorBackfillResponse | HTTPValidationError | None:
    """Backfill CO_AUTHOR edges from enrichment_authors lists

     Materializes the coauthorship graph for entities enriched before the
    extraction hook landed in enrichment_worker. Idempotent (upserts on
    ``relation_type='CO_AUTHOR'`` + ``notes='A||B'``); pass ``reset=True``
    when you want a fresh start.

    Args:
        body (CoauthorBackfillRequest): Inputs for the CO_AUTHOR edge backfill.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CoauthorBackfillResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
