from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_analyzers_coauthorship_by_domain_id_diagnostics_response_get_analyzers_coauthorship_by_domain_id_diagnostics import (
    GetAnalyzersCoauthorshipByDomainIdDiagnosticsResponseGetAnalyzersCoauthorshipByDomainIdDiagnostics,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    domain_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/analyzers/coauthorship/{domain_id}/diagnostics".format(
            domain_id=quote(str(domain_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    GetAnalyzersCoauthorshipByDomainIdDiagnosticsResponseGetAnalyzersCoauthorshipByDomainIdDiagnostics
    | HTTPValidationError
    | None
):
    if response.status_code == 200:
        response_200 = GetAnalyzersCoauthorshipByDomainIdDiagnosticsResponseGetAnalyzersCoauthorshipByDomainIdDiagnostics.from_dict(
            response.json()
        )

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
) -> Response[
    GetAnalyzersCoauthorshipByDomainIdDiagnosticsResponseGetAnalyzersCoauthorshipByDomainIdDiagnostics
    | HTTPValidationError
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    domain_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[
    GetAnalyzersCoauthorshipByDomainIdDiagnosticsResponseGetAnalyzersCoauthorshipByDomainIdDiagnostics
    | HTTPValidationError
]:
    """Coauthorship Diagnostics

     Pipeline counters for one scope: storage -> scope filter -> stats.

    Args:
        domain_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetAnalyzersCoauthorshipByDomainIdDiagnosticsResponseGetAnalyzersCoauthorshipByDomainIdDiagnostics | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        domain_id=domain_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    domain_id: str,
    *,
    client: AuthenticatedClient,
) -> (
    GetAnalyzersCoauthorshipByDomainIdDiagnosticsResponseGetAnalyzersCoauthorshipByDomainIdDiagnostics
    | HTTPValidationError
    | None
):
    """Coauthorship Diagnostics

     Pipeline counters for one scope: storage -> scope filter -> stats.

    Args:
        domain_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetAnalyzersCoauthorshipByDomainIdDiagnosticsResponseGetAnalyzersCoauthorshipByDomainIdDiagnostics | HTTPValidationError
    """

    return sync_detailed(
        domain_id=domain_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    domain_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[
    GetAnalyzersCoauthorshipByDomainIdDiagnosticsResponseGetAnalyzersCoauthorshipByDomainIdDiagnostics
    | HTTPValidationError
]:
    """Coauthorship Diagnostics

     Pipeline counters for one scope: storage -> scope filter -> stats.

    Args:
        domain_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetAnalyzersCoauthorshipByDomainIdDiagnosticsResponseGetAnalyzersCoauthorshipByDomainIdDiagnostics | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        domain_id=domain_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    domain_id: str,
    *,
    client: AuthenticatedClient,
) -> (
    GetAnalyzersCoauthorshipByDomainIdDiagnosticsResponseGetAnalyzersCoauthorshipByDomainIdDiagnostics
    | HTTPValidationError
    | None
):
    """Coauthorship Diagnostics

     Pipeline counters for one scope: storage -> scope filter -> stats.

    Args:
        domain_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetAnalyzersCoauthorshipByDomainIdDiagnosticsResponseGetAnalyzersCoauthorshipByDomainIdDiagnostics | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            domain_id=domain_id,
            client=client,
        )
    ).parsed
