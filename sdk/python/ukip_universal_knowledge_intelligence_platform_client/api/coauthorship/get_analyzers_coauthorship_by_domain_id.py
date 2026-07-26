from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    domain_id: str,
    *,
    min_weight: int | Unset = 1,
    limit: int | None | Unset = 100,
    community_id: int | None | Unset = UNSET,
    search: None | str | Unset = UNSET,
    force_refresh: bool | Unset = False,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["min_weight"] = min_weight

    json_limit: int | None | Unset
    if isinstance(limit, Unset):
        json_limit = UNSET
    else:
        json_limit = limit
    params["limit"] = json_limit

    json_community_id: int | None | Unset
    if isinstance(community_id, Unset):
        json_community_id = UNSET
    else:
        json_community_id = community_id
    params["community_id"] = json_community_id

    json_search: None | str | Unset
    if isinstance(search, Unset):
        json_search = UNSET
    else:
        json_search = search
    params["search"] = json_search

    params["force_refresh"] = force_refresh

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/analyzers/coauthorship/{domain_id}".format(
            domain_id=quote(str(domain_id), safe=""),
        ),
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
    domain_id: str,
    *,
    client: AuthenticatedClient,
    min_weight: int | Unset = 1,
    limit: int | None | Unset = 100,
    community_id: int | None | Unset = UNSET,
    search: None | str | Unset = UNSET,
    force_refresh: bool | Unset = False,
) -> Response[Any | HTTPValidationError]:
    """Coauthorship Network V2

     Co-authorship network served from materialized V2 tables (author_stats +
    coauthor_edges). Behind COAUTHOR_V2_READ; when off, falls through to the
    legacy analyzer so behaviour is unchanged until cutover.

    Args:
        domain_id (str):
        min_weight (int | Unset):  Default: 1.
        limit (int | None | Unset):  Default: 100.
        community_id (int | None | Unset):
        search (None | str | Unset):
        force_refresh (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        domain_id=domain_id,
        min_weight=min_weight,
        limit=limit,
        community_id=community_id,
        search=search,
        force_refresh=force_refresh,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    domain_id: str,
    *,
    client: AuthenticatedClient,
    min_weight: int | Unset = 1,
    limit: int | None | Unset = 100,
    community_id: int | None | Unset = UNSET,
    search: None | str | Unset = UNSET,
    force_refresh: bool | Unset = False,
) -> Any | HTTPValidationError | None:
    """Coauthorship Network V2

     Co-authorship network served from materialized V2 tables (author_stats +
    coauthor_edges). Behind COAUTHOR_V2_READ; when off, falls through to the
    legacy analyzer so behaviour is unchanged until cutover.

    Args:
        domain_id (str):
        min_weight (int | Unset):  Default: 1.
        limit (int | None | Unset):  Default: 100.
        community_id (int | None | Unset):
        search (None | str | Unset):
        force_refresh (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        domain_id=domain_id,
        client=client,
        min_weight=min_weight,
        limit=limit,
        community_id=community_id,
        search=search,
        force_refresh=force_refresh,
    ).parsed


async def asyncio_detailed(
    domain_id: str,
    *,
    client: AuthenticatedClient,
    min_weight: int | Unset = 1,
    limit: int | None | Unset = 100,
    community_id: int | None | Unset = UNSET,
    search: None | str | Unset = UNSET,
    force_refresh: bool | Unset = False,
) -> Response[Any | HTTPValidationError]:
    """Coauthorship Network V2

     Co-authorship network served from materialized V2 tables (author_stats +
    coauthor_edges). Behind COAUTHOR_V2_READ; when off, falls through to the
    legacy analyzer so behaviour is unchanged until cutover.

    Args:
        domain_id (str):
        min_weight (int | Unset):  Default: 1.
        limit (int | None | Unset):  Default: 100.
        community_id (int | None | Unset):
        search (None | str | Unset):
        force_refresh (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        domain_id=domain_id,
        min_weight=min_weight,
        limit=limit,
        community_id=community_id,
        search=search,
        force_refresh=force_refresh,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    domain_id: str,
    *,
    client: AuthenticatedClient,
    min_weight: int | Unset = 1,
    limit: int | None | Unset = 100,
    community_id: int | None | Unset = UNSET,
    search: None | str | Unset = UNSET,
    force_refresh: bool | Unset = False,
) -> Any | HTTPValidationError | None:
    """Coauthorship Network V2

     Co-authorship network served from materialized V2 tables (author_stats +
    coauthor_edges). Behind COAUTHOR_V2_READ; when off, falls through to the
    legacy analyzer so behaviour is unchanged until cutover.

    Args:
        domain_id (str):
        min_weight (int | Unset):  Default: 1.
        limit (int | None | Unset):  Default: 100.
        community_id (int | None | Unset):
        search (None | str | Unset):
        force_refresh (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            domain_id=domain_id,
            client=client,
            min_weight=min_weight,
            limit=limit,
            community_id=community_id,
            search=search,
            force_refresh=force_refresh,
        )
    ).parsed
