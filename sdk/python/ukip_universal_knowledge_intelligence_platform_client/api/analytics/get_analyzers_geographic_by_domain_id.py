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
    sort_by: str | Unset = "entity_count",
    limit: int | None | Unset = UNSET,
    include_collaboration: bool | Unset = False,
    year_from: int | None | Unset = UNSET,
    year_to: int | None | Unset = UNSET,
    min_citations: int | None | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["sort_by"] = sort_by

    json_limit: int | None | Unset
    if isinstance(limit, Unset):
        json_limit = UNSET
    else:
        json_limit = limit
    params["limit"] = json_limit

    params["include_collaboration"] = include_collaboration

    json_year_from: int | None | Unset
    if isinstance(year_from, Unset):
        json_year_from = UNSET
    else:
        json_year_from = year_from
    params["year_from"] = json_year_from

    json_year_to: int | None | Unset
    if isinstance(year_to, Unset):
        json_year_to = UNSET
    else:
        json_year_to = year_to
    params["year_to"] = json_year_to

    json_min_citations: int | None | Unset
    if isinstance(min_citations, Unset):
        json_min_citations = UNSET
    else:
        json_min_citations = min_citations
    params["min_citations"] = json_min_citations

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/analyzers/geographic/{domain_id}".format(
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
    sort_by: str | Unset = "entity_count",
    limit: int | None | Unset = UNSET,
    include_collaboration: bool | Unset = False,
    year_from: int | None | Unset = UNSET,
    year_to: int | None | Unset = UNSET,
    min_citations: int | None | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Analyzer Geographic

     Per-country aggregation with optional filters and collaboration analysis.

    Args:
        domain_id (str):
        sort_by (str | Unset):  Default: 'entity_count'.
        limit (int | None | Unset):
        include_collaboration (bool | Unset):  Default: False.
        year_from (int | None | Unset):
        year_to (int | None | Unset):
        min_citations (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        domain_id=domain_id,
        sort_by=sort_by,
        limit=limit,
        include_collaboration=include_collaboration,
        year_from=year_from,
        year_to=year_to,
        min_citations=min_citations,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    domain_id: str,
    *,
    client: AuthenticatedClient,
    sort_by: str | Unset = "entity_count",
    limit: int | None | Unset = UNSET,
    include_collaboration: bool | Unset = False,
    year_from: int | None | Unset = UNSET,
    year_to: int | None | Unset = UNSET,
    min_citations: int | None | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Analyzer Geographic

     Per-country aggregation with optional filters and collaboration analysis.

    Args:
        domain_id (str):
        sort_by (str | Unset):  Default: 'entity_count'.
        limit (int | None | Unset):
        include_collaboration (bool | Unset):  Default: False.
        year_from (int | None | Unset):
        year_to (int | None | Unset):
        min_citations (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        domain_id=domain_id,
        client=client,
        sort_by=sort_by,
        limit=limit,
        include_collaboration=include_collaboration,
        year_from=year_from,
        year_to=year_to,
        min_citations=min_citations,
    ).parsed


async def asyncio_detailed(
    domain_id: str,
    *,
    client: AuthenticatedClient,
    sort_by: str | Unset = "entity_count",
    limit: int | None | Unset = UNSET,
    include_collaboration: bool | Unset = False,
    year_from: int | None | Unset = UNSET,
    year_to: int | None | Unset = UNSET,
    min_citations: int | None | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Analyzer Geographic

     Per-country aggregation with optional filters and collaboration analysis.

    Args:
        domain_id (str):
        sort_by (str | Unset):  Default: 'entity_count'.
        limit (int | None | Unset):
        include_collaboration (bool | Unset):  Default: False.
        year_from (int | None | Unset):
        year_to (int | None | Unset):
        min_citations (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        domain_id=domain_id,
        sort_by=sort_by,
        limit=limit,
        include_collaboration=include_collaboration,
        year_from=year_from,
        year_to=year_to,
        min_citations=min_citations,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    domain_id: str,
    *,
    client: AuthenticatedClient,
    sort_by: str | Unset = "entity_count",
    limit: int | None | Unset = UNSET,
    include_collaboration: bool | Unset = False,
    year_from: int | None | Unset = UNSET,
    year_to: int | None | Unset = UNSET,
    min_citations: int | None | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Analyzer Geographic

     Per-country aggregation with optional filters and collaboration analysis.

    Args:
        domain_id (str):
        sort_by (str | Unset):  Default: 'entity_count'.
        limit (int | None | Unset):
        include_collaboration (bool | Unset):  Default: False.
        year_from (int | None | Unset):
        year_to (int | None | Unset):
        min_citations (int | None | Unset):

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
            sort_by=sort_by,
            limit=limit,
            include_collaboration=include_collaboration,
            year_from=year_from,
            year_to=year_to,
            min_citations=min_citations,
        )
    ).parsed
