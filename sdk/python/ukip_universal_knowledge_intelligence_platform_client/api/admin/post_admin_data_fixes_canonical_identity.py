from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.canonical_identity_fix_request import CanonicalIdentityFixRequest
from ...models.canonical_identity_fix_response import CanonicalIdentityFixResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    *,
    body: CanonicalIdentityFixRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/admin/data-fixes/canonical-identity",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CanonicalIdentityFixResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = CanonicalIdentityFixResponse.from_dict(response.json())

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
) -> Response[CanonicalIdentityFixResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: CanonicalIdentityFixRequest,
) -> Response[CanonicalIdentityFixResponse | HTTPValidationError]:
    """Backfill canonical_id and entity_type for existing entities

     Idempotent. Safe to call repeatedly. Intended for production data
    repair after imports that stored identifiers in enrichment/attribute
    fields but left the canonical columns empty.

    Args:
        body (CanonicalIdentityFixRequest): Inputs for canonical_id/entity_type backfill.

            Defaults bias toward safety: ``dry_run=True`` and both fields included.
            The operation is idempotent and never overwrites existing non-empty values.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CanonicalIdentityFixResponse | HTTPValidationError]
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
    body: CanonicalIdentityFixRequest,
) -> CanonicalIdentityFixResponse | HTTPValidationError | None:
    """Backfill canonical_id and entity_type for existing entities

     Idempotent. Safe to call repeatedly. Intended for production data
    repair after imports that stored identifiers in enrichment/attribute
    fields but left the canonical columns empty.

    Args:
        body (CanonicalIdentityFixRequest): Inputs for canonical_id/entity_type backfill.

            Defaults bias toward safety: ``dry_run=True`` and both fields included.
            The operation is idempotent and never overwrites existing non-empty values.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CanonicalIdentityFixResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: CanonicalIdentityFixRequest,
) -> Response[CanonicalIdentityFixResponse | HTTPValidationError]:
    """Backfill canonical_id and entity_type for existing entities

     Idempotent. Safe to call repeatedly. Intended for production data
    repair after imports that stored identifiers in enrichment/attribute
    fields but left the canonical columns empty.

    Args:
        body (CanonicalIdentityFixRequest): Inputs for canonical_id/entity_type backfill.

            Defaults bias toward safety: ``dry_run=True`` and both fields included.
            The operation is idempotent and never overwrites existing non-empty values.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CanonicalIdentityFixResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: CanonicalIdentityFixRequest,
) -> CanonicalIdentityFixResponse | HTTPValidationError | None:
    """Backfill canonical_id and entity_type for existing entities

     Idempotent. Safe to call repeatedly. Intended for production data
    repair after imports that stored identifiers in enrichment/attribute
    fields but left the canonical columns empty.

    Args:
        body (CanonicalIdentityFixRequest): Inputs for canonical_id/entity_type backfill.

            Defaults bias toward safety: ``dry_run=True`` and both fields included.
            The operation is idempotent and never overwrites existing non-empty values.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CanonicalIdentityFixResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
