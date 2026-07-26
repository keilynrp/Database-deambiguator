from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.legacy_affiliation_fix_request import LegacyAffiliationFixRequest
from ...models.legacy_affiliation_fix_response import LegacyAffiliationFixResponse
from ...types import Response


def _get_kwargs(
    *,
    body: LegacyAffiliationFixRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/admin/data-fixes/legacy-affiliations",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | LegacyAffiliationFixResponse | None:
    if response.status_code == 200:
        response_200 = LegacyAffiliationFixResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | LegacyAffiliationFixResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: LegacyAffiliationFixRequest,
) -> Response[HTTPValidationError | LegacyAffiliationFixResponse]:
    """Backfill legacy affiliation residue (cbe3255 bug)

     Idempotent. Safe to call repeatedly. Always log the request shape so
    the audit trail captures who initiated which run.

    Args:
        body (LegacyAffiliationFixRequest): Inputs for the legacy-affiliation backfill.

            Defaults bias toward safety: ``dry_run=True`` and no re-enrichment.
            Callers must explicitly opt out of dry-run to mutate the database.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | LegacyAffiliationFixResponse]
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
    body: LegacyAffiliationFixRequest,
) -> HTTPValidationError | LegacyAffiliationFixResponse | None:
    """Backfill legacy affiliation residue (cbe3255 bug)

     Idempotent. Safe to call repeatedly. Always log the request shape so
    the audit trail captures who initiated which run.

    Args:
        body (LegacyAffiliationFixRequest): Inputs for the legacy-affiliation backfill.

            Defaults bias toward safety: ``dry_run=True`` and no re-enrichment.
            Callers must explicitly opt out of dry-run to mutate the database.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | LegacyAffiliationFixResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: LegacyAffiliationFixRequest,
) -> Response[HTTPValidationError | LegacyAffiliationFixResponse]:
    """Backfill legacy affiliation residue (cbe3255 bug)

     Idempotent. Safe to call repeatedly. Always log the request shape so
    the audit trail captures who initiated which run.

    Args:
        body (LegacyAffiliationFixRequest): Inputs for the legacy-affiliation backfill.

            Defaults bias toward safety: ``dry_run=True`` and no re-enrichment.
            Callers must explicitly opt out of dry-run to mutate the database.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | LegacyAffiliationFixResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: LegacyAffiliationFixRequest,
) -> HTTPValidationError | LegacyAffiliationFixResponse | None:
    """Backfill legacy affiliation residue (cbe3255 bug)

     Idempotent. Safe to call repeatedly. Always log the request shape so
    the audit trail captures who initiated which run.

    Args:
        body (LegacyAffiliationFixRequest): Inputs for the legacy-affiliation backfill.

            Defaults bias toward safety: ``dry_run=True`` and no re-enrichment.
            Callers must explicitly opt out of dry-run to mutate the database.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | LegacyAffiliationFixResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
