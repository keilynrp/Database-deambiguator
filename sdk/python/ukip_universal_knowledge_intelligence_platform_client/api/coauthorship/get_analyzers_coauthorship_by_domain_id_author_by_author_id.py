from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_analyzers_coauthorship_by_domain_id_author_by_author_id_response_get_analyzers_coauthorship_by_domain_id_author_by_author_id import (
    GetAnalyzersCoauthorshipByDomainIdAuthorByAuthorIdResponseGetAnalyzersCoauthorshipByDomainIdAuthorByAuthorId,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    domain_id: str,
    author_id: int,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/analyzers/coauthorship/{domain_id}/author/{author_id}".format(
            domain_id=quote(str(domain_id), safe=""),
            author_id=quote(str(author_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    GetAnalyzersCoauthorshipByDomainIdAuthorByAuthorIdResponseGetAnalyzersCoauthorshipByDomainIdAuthorByAuthorId
    | HTTPValidationError
    | None
):
    if response.status_code == 200:
        response_200 = GetAnalyzersCoauthorshipByDomainIdAuthorByAuthorIdResponseGetAnalyzersCoauthorshipByDomainIdAuthorByAuthorId.from_dict(
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
    GetAnalyzersCoauthorshipByDomainIdAuthorByAuthorIdResponseGetAnalyzersCoauthorshipByDomainIdAuthorByAuthorId
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
    author_id: int,
    *,
    client: AuthenticatedClient,
) -> Response[
    GetAnalyzersCoauthorshipByDomainIdAuthorByAuthorIdResponseGetAnalyzersCoauthorshipByDomainIdAuthorByAuthorId
    | HTTPValidationError
]:
    """Coauthorship Author Detail

     Detail for one author within a scope: identity header, stats, top
    publications (by year desc), and top collaborators (by edge weight desc).
    Served from the V2 tables; no legacy equivalent.

    Args:
        domain_id (str):
        author_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetAnalyzersCoauthorshipByDomainIdAuthorByAuthorIdResponseGetAnalyzersCoauthorshipByDomainIdAuthorByAuthorId | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        domain_id=domain_id,
        author_id=author_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    domain_id: str,
    author_id: int,
    *,
    client: AuthenticatedClient,
) -> (
    GetAnalyzersCoauthorshipByDomainIdAuthorByAuthorIdResponseGetAnalyzersCoauthorshipByDomainIdAuthorByAuthorId
    | HTTPValidationError
    | None
):
    """Coauthorship Author Detail

     Detail for one author within a scope: identity header, stats, top
    publications (by year desc), and top collaborators (by edge weight desc).
    Served from the V2 tables; no legacy equivalent.

    Args:
        domain_id (str):
        author_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetAnalyzersCoauthorshipByDomainIdAuthorByAuthorIdResponseGetAnalyzersCoauthorshipByDomainIdAuthorByAuthorId | HTTPValidationError
    """

    return sync_detailed(
        domain_id=domain_id,
        author_id=author_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    domain_id: str,
    author_id: int,
    *,
    client: AuthenticatedClient,
) -> Response[
    GetAnalyzersCoauthorshipByDomainIdAuthorByAuthorIdResponseGetAnalyzersCoauthorshipByDomainIdAuthorByAuthorId
    | HTTPValidationError
]:
    """Coauthorship Author Detail

     Detail for one author within a scope: identity header, stats, top
    publications (by year desc), and top collaborators (by edge weight desc).
    Served from the V2 tables; no legacy equivalent.

    Args:
        domain_id (str):
        author_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetAnalyzersCoauthorshipByDomainIdAuthorByAuthorIdResponseGetAnalyzersCoauthorshipByDomainIdAuthorByAuthorId | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        domain_id=domain_id,
        author_id=author_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    domain_id: str,
    author_id: int,
    *,
    client: AuthenticatedClient,
) -> (
    GetAnalyzersCoauthorshipByDomainIdAuthorByAuthorIdResponseGetAnalyzersCoauthorshipByDomainIdAuthorByAuthorId
    | HTTPValidationError
    | None
):
    """Coauthorship Author Detail

     Detail for one author within a scope: identity header, stats, top
    publications (by year desc), and top collaborators (by edge weight desc).
    Served from the V2 tables; no legacy equivalent.

    Args:
        domain_id (str):
        author_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetAnalyzersCoauthorshipByDomainIdAuthorByAuthorIdResponseGetAnalyzersCoauthorshipByDomainIdAuthorByAuthorId | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            domain_id=domain_id,
            author_id=author_id,
            client=client,
        )
    ).parsed
