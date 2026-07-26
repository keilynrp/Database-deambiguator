from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    topic: str,
    domain_id: str | Unset = "default",
    limit: int | Unset = 50,
    min_weight: int | Unset = 1,
    source: None | str | Unset = UNSET,
    year_from: int | None | Unset = UNSET,
    year_to: int | None | Unset = UNSET,
    country: None | str | Unset = UNSET,
    institution: None | str | Unset = UNSET,
    min_citations: int | Unset = 0,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["topic"] = topic

    params["domain_id"] = domain_id

    params["limit"] = limit

    params["min_weight"] = min_weight

    json_source: None | str | Unset
    if isinstance(source, Unset):
        json_source = UNSET
    else:
        json_source = source
    params["source"] = json_source

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

    json_country: None | str | Unset
    if isinstance(country, Unset):
        json_country = UNSET
    else:
        json_country = country
    params["country"] = json_country

    json_institution: None | str | Unset
    if isinstance(institution, Unset):
        json_institution = UNSET
    else:
        json_institution = institution
    params["institution"] = json_institution

    params["min_citations"] = min_citations

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/analytics/topic-researcher-graph",
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
    topic: str,
    domain_id: str | Unset = "default",
    limit: int | Unset = 50,
    min_weight: int | Unset = 1,
    source: None | str | Unset = UNSET,
    year_from: int | None | Unset = UNSET,
    year_to: int | None | Unset = UNSET,
    country: None | str | Unset = UNSET,
    institution: None | str | Unset = UNSET,
    min_citations: int | Unset = 0,
) -> Response[Any | HTTPValidationError]:
    """Analytics Topic Researcher Graph

     Build a topic-centered researcher graph from co-authorship and topic affinity evidence.

    Args:
        topic (str):
        domain_id (str | Unset):  Default: 'default'.
        limit (int | Unset):  Default: 50.
        min_weight (int | Unset):  Default: 1.
        source (None | str | Unset):
        year_from (int | None | Unset):
        year_to (int | None | Unset):
        country (None | str | Unset):
        institution (None | str | Unset):
        min_citations (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        topic=topic,
        domain_id=domain_id,
        limit=limit,
        min_weight=min_weight,
        source=source,
        year_from=year_from,
        year_to=year_to,
        country=country,
        institution=institution,
        min_citations=min_citations,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    topic: str,
    domain_id: str | Unset = "default",
    limit: int | Unset = 50,
    min_weight: int | Unset = 1,
    source: None | str | Unset = UNSET,
    year_from: int | None | Unset = UNSET,
    year_to: int | None | Unset = UNSET,
    country: None | str | Unset = UNSET,
    institution: None | str | Unset = UNSET,
    min_citations: int | Unset = 0,
) -> Any | HTTPValidationError | None:
    """Analytics Topic Researcher Graph

     Build a topic-centered researcher graph from co-authorship and topic affinity evidence.

    Args:
        topic (str):
        domain_id (str | Unset):  Default: 'default'.
        limit (int | Unset):  Default: 50.
        min_weight (int | Unset):  Default: 1.
        source (None | str | Unset):
        year_from (int | None | Unset):
        year_to (int | None | Unset):
        country (None | str | Unset):
        institution (None | str | Unset):
        min_citations (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        topic=topic,
        domain_id=domain_id,
        limit=limit,
        min_weight=min_weight,
        source=source,
        year_from=year_from,
        year_to=year_to,
        country=country,
        institution=institution,
        min_citations=min_citations,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    topic: str,
    domain_id: str | Unset = "default",
    limit: int | Unset = 50,
    min_weight: int | Unset = 1,
    source: None | str | Unset = UNSET,
    year_from: int | None | Unset = UNSET,
    year_to: int | None | Unset = UNSET,
    country: None | str | Unset = UNSET,
    institution: None | str | Unset = UNSET,
    min_citations: int | Unset = 0,
) -> Response[Any | HTTPValidationError]:
    """Analytics Topic Researcher Graph

     Build a topic-centered researcher graph from co-authorship and topic affinity evidence.

    Args:
        topic (str):
        domain_id (str | Unset):  Default: 'default'.
        limit (int | Unset):  Default: 50.
        min_weight (int | Unset):  Default: 1.
        source (None | str | Unset):
        year_from (int | None | Unset):
        year_to (int | None | Unset):
        country (None | str | Unset):
        institution (None | str | Unset):
        min_citations (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        topic=topic,
        domain_id=domain_id,
        limit=limit,
        min_weight=min_weight,
        source=source,
        year_from=year_from,
        year_to=year_to,
        country=country,
        institution=institution,
        min_citations=min_citations,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    topic: str,
    domain_id: str | Unset = "default",
    limit: int | Unset = 50,
    min_weight: int | Unset = 1,
    source: None | str | Unset = UNSET,
    year_from: int | None | Unset = UNSET,
    year_to: int | None | Unset = UNSET,
    country: None | str | Unset = UNSET,
    institution: None | str | Unset = UNSET,
    min_citations: int | Unset = 0,
) -> Any | HTTPValidationError | None:
    """Analytics Topic Researcher Graph

     Build a topic-centered researcher graph from co-authorship and topic affinity evidence.

    Args:
        topic (str):
        domain_id (str | Unset):  Default: 'default'.
        limit (int | Unset):  Default: 50.
        min_weight (int | Unset):  Default: 1.
        source (None | str | Unset):
        year_from (int | None | Unset):
        year_to (int | None | Unset):
        country (None | str | Unset):
        institution (None | str | Unset):
        min_citations (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            topic=topic,
            domain_id=domain_id,
            limit=limit,
            min_weight=min_weight,
            source=source,
            year_from=year_from,
            year_to=year_to,
            country=country,
            institution=institution,
            min_citations=min_citations,
        )
    ).parsed
