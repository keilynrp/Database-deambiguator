from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    entity_id: int,
    *,
    limit: int | Unset = 8,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/entities/{entity_id}/relationships/suggestions".format(
            entity_id=quote(str(entity_id), safe=""),
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
    entity_id: int,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 8,
) -> Response[Any | HTTPValidationError]:
    """Suggest Relationships

     Suggest concrete relationships from shared concepts, batch context, and derived graph nodes.

    Args:
        entity_id (int):
        limit (int | Unset):  Default: 8.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        entity_id=entity_id,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    entity_id: int,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 8,
) -> Any | HTTPValidationError | None:
    """Suggest Relationships

     Suggest concrete relationships from shared concepts, batch context, and derived graph nodes.

    Args:
        entity_id (int):
        limit (int | Unset):  Default: 8.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        entity_id=entity_id,
        client=client,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    entity_id: int,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 8,
) -> Response[Any | HTTPValidationError]:
    """Suggest Relationships

     Suggest concrete relationships from shared concepts, batch context, and derived graph nodes.

    Args:
        entity_id (int):
        limit (int | Unset):  Default: 8.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        entity_id=entity_id,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    entity_id: int,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 8,
) -> Any | HTTPValidationError | None:
    """Suggest Relationships

     Suggest concrete relationships from shared concepts, batch context, and derived graph nodes.

    Args:
        entity_id (int):
        limit (int | Unset):  Default: 8.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            entity_id=entity_id,
            client=client,
            limit=limit,
        )
    ).parsed
