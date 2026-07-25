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
    limit: int | Unset = 50,
    persist: bool | Unset = True,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["persist"] = persist

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/analytics/keywords/{domain_id}/materialize".format(
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
    limit: int | Unset = 50,
    persist: bool | Unset = True,
) -> Response[Any | HTTPValidationError]:
    """Materialize Semantic Keyword Signals

     Materialize semantic keyword opportunity signals for a domain.

    Args:
        domain_id (str):
        limit (int | Unset):  Default: 50.
        persist (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        domain_id=domain_id,
        limit=limit,
        persist=persist,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    domain_id: str,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 50,
    persist: bool | Unset = True,
) -> Any | HTTPValidationError | None:
    """Materialize Semantic Keyword Signals

     Materialize semantic keyword opportunity signals for a domain.

    Args:
        domain_id (str):
        limit (int | Unset):  Default: 50.
        persist (bool | Unset):  Default: True.

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
        persist=persist,
    ).parsed


async def asyncio_detailed(
    domain_id: str,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 50,
    persist: bool | Unset = True,
) -> Response[Any | HTTPValidationError]:
    """Materialize Semantic Keyword Signals

     Materialize semantic keyword opportunity signals for a domain.

    Args:
        domain_id (str):
        limit (int | Unset):  Default: 50.
        persist (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        domain_id=domain_id,
        limit=limit,
        persist=persist,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    domain_id: str,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 50,
    persist: bool | Unset = True,
) -> Any | HTTPValidationError | None:
    """Materialize Semantic Keyword Signals

     Materialize semantic keyword opportunity signals for a domain.

    Args:
        domain_id (str):
        limit (int | Unset):  Default: 50.
        persist (bool | Unset):  Default: True.

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
            persist=persist,
        )
    ).parsed
