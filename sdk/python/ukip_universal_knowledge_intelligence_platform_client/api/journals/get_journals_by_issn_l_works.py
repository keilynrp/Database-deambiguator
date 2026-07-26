from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.entity import Entity
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    issn_l: str,
    *,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/journals/{issn_l}/works".format(
            issn_l=quote(str(issn_l), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | list[Entity] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Entity.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[HTTPValidationError | list[Entity]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    issn_l: str,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> Response[HTTPValidationError | list[Entity]]:
    """List Journal Works

     List the catalog records (works) linked to a journal by ISSN-L.

    Complements the works_count surfaced on the journal rows: this resolves the
    actual records behind that count, each carrying the attached NIF + Bayes
    signal so callers can jump straight from a journal to its works.

    Args:
        issn_l (str):
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[Entity]]
    """

    kwargs = _get_kwargs(
        issn_l=issn_l,
        limit=limit,
        offset=offset,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    issn_l: str,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> HTTPValidationError | list[Entity] | None:
    """List Journal Works

     List the catalog records (works) linked to a journal by ISSN-L.

    Complements the works_count surfaced on the journal rows: this resolves the
    actual records behind that count, each carrying the attached NIF + Bayes
    signal so callers can jump straight from a journal to its works.

    Args:
        issn_l (str):
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[Entity]
    """

    return sync_detailed(
        issn_l=issn_l,
        client=client,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    issn_l: str,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> Response[HTTPValidationError | list[Entity]]:
    """List Journal Works

     List the catalog records (works) linked to a journal by ISSN-L.

    Complements the works_count surfaced on the journal rows: this resolves the
    actual records behind that count, each carrying the attached NIF + Bayes
    signal so callers can jump straight from a journal to its works.

    Args:
        issn_l (str):
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[Entity]]
    """

    kwargs = _get_kwargs(
        issn_l=issn_l,
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    issn_l: str,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> HTTPValidationError | list[Entity] | None:
    """List Journal Works

     List the catalog records (works) linked to a journal by ISSN-L.

    Complements the works_count surfaced on the journal rows: this resolves the
    actual records behind that count, each carrying the attached NIF + Bayes
    signal so callers can jump straight from a journal to its works.

    Args:
        issn_l (str):
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[Entity]
    """

    return (
        await asyncio_detailed(
            issn_l=issn_l,
            client=client,
            limit=limit,
            offset=offset,
        )
    ).parsed
