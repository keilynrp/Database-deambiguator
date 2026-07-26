from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_export_graph_format import GetExportGraphFormat
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    format_: GetExportGraphFormat,
    domain: None | str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_format_ = format_.value
    params["format"] = json_format_

    json_domain: None | str | Unset
    if isinstance(domain, Unset):
        json_domain = UNSET
    else:
        json_domain = domain
    params["domain"] = json_domain

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/export/graph",
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
    format_: GetExportGraphFormat,
    domain: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Export Graph

     Sprint 75 — Export the knowledge graph in a standard interchange format.

    Nodes are entities; edges are typed, weighted relationships.
    Optional `domain` parameter scopes the export to a single domain.

    Args:
        format_ (GetExportGraphFormat): Output format: graphml | cytoscape | jsonld
        domain (None | str | Unset): Filter to a specific domain

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        format_=format_,
        domain=domain,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    format_: GetExportGraphFormat,
    domain: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Export Graph

     Sprint 75 — Export the knowledge graph in a standard interchange format.

    Nodes are entities; edges are typed, weighted relationships.
    Optional `domain` parameter scopes the export to a single domain.

    Args:
        format_ (GetExportGraphFormat): Output format: graphml | cytoscape | jsonld
        domain (None | str | Unset): Filter to a specific domain

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        format_=format_,
        domain=domain,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    format_: GetExportGraphFormat,
    domain: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Export Graph

     Sprint 75 — Export the knowledge graph in a standard interchange format.

    Nodes are entities; edges are typed, weighted relationships.
    Optional `domain` parameter scopes the export to a single domain.

    Args:
        format_ (GetExportGraphFormat): Output format: graphml | cytoscape | jsonld
        domain (None | str | Unset): Filter to a specific domain

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        format_=format_,
        domain=domain,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    format_: GetExportGraphFormat,
    domain: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Export Graph

     Sprint 75 — Export the knowledge graph in a standard interchange format.

    Nodes are entities; edges are typed, weighted relationships.
    Optional `domain` parameter scopes the export to a single domain.

    Args:
        format_ (GetExportGraphFormat): Output format: graphml | cytoscape | jsonld
        domain (None | str | Unset): Filter to a specific domain

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            format_=format_,
            domain=domain,
        )
    ).parsed
