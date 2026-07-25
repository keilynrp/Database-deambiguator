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
    limit: int | Unset = 20,
    min_year: int | None | Unset = UNSET,
    max_year: int | None | Unset = UNSET,
    min_years: int | Unset = 3,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["limit"] = limit

    json_min_year: int | None | Unset
    if isinstance(min_year, Unset):
        json_min_year = UNSET
    else:
        json_min_year = min_year
    params["min_year"] = json_min_year

    json_max_year: int | None | Unset
    if isinstance(max_year, Unset):
        json_max_year = UNSET
    else:
        json_max_year = max_year
    params["max_year"] = json_max_year

    params["min_years"] = min_years

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/analyzers/trends/{domain_id}".format(
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
    limit: int | Unset = 20,
    min_year: int | None | Unset = UNSET,
    max_year: int | None | Unset = UNSET,
    min_years: int | Unset = 3,
) -> Response[Any | HTTPValidationError]:
    """Analyzer Trends

     Concept frequency trends with slope-based classification (emerging/declining/stable).

    Args:
        domain_id (str):
        limit (int | Unset):  Default: 20.
        min_year (int | None | Unset):
        max_year (int | None | Unset):
        min_years (int | Unset):  Default: 3.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        domain_id=domain_id,
        limit=limit,
        min_year=min_year,
        max_year=max_year,
        min_years=min_years,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    domain_id: str,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 20,
    min_year: int | None | Unset = UNSET,
    max_year: int | None | Unset = UNSET,
    min_years: int | Unset = 3,
) -> Any | HTTPValidationError | None:
    """Analyzer Trends

     Concept frequency trends with slope-based classification (emerging/declining/stable).

    Args:
        domain_id (str):
        limit (int | Unset):  Default: 20.
        min_year (int | None | Unset):
        max_year (int | None | Unset):
        min_years (int | Unset):  Default: 3.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        domain_id=domain_id,
        client=client,
        limit=limit,
        min_year=min_year,
        max_year=max_year,
        min_years=min_years,
    ).parsed


async def asyncio_detailed(
    domain_id: str,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 20,
    min_year: int | None | Unset = UNSET,
    max_year: int | None | Unset = UNSET,
    min_years: int | Unset = 3,
) -> Response[Any | HTTPValidationError]:
    """Analyzer Trends

     Concept frequency trends with slope-based classification (emerging/declining/stable).

    Args:
        domain_id (str):
        limit (int | Unset):  Default: 20.
        min_year (int | None | Unset):
        max_year (int | None | Unset):
        min_years (int | Unset):  Default: 3.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        domain_id=domain_id,
        limit=limit,
        min_year=min_year,
        max_year=max_year,
        min_years=min_years,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    domain_id: str,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 20,
    min_year: int | None | Unset = UNSET,
    max_year: int | None | Unset = UNSET,
    min_years: int | Unset = 3,
) -> Any | HTTPValidationError | None:
    """Analyzer Trends

     Concept frequency trends with slope-based classification (emerging/declining/stable).

    Args:
        domain_id (str):
        limit (int | Unset):  Default: 20.
        min_year (int | None | Unset):
        max_year (int | None | Unset):
        min_years (int | Unset):  Default: 3.

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
            limit=limit,
            min_year=min_year,
            max_year=max_year,
            min_years=min_years,
        )
    ).parsed
