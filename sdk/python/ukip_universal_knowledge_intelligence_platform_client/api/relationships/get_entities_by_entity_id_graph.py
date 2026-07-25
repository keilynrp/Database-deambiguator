from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.entity_graph_response import EntityGraphResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    entity_id: int,
    *,
    depth: int | Unset = 1,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["depth"] = depth

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/entities/{entity_id}/graph".format(
            entity_id=quote(str(entity_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> EntityGraphResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = EntityGraphResponse.from_dict(response.json())

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
) -> Response[EntityGraphResponse | HTTPValidationError]:
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
    depth: int | Unset = 1,
) -> Response[EntityGraphResponse | HTTPValidationError]:
    """Get Entity Graph

     Return a subgraph centered on entity_id.
    depth=1 → direct neighbors only.
    depth=2 → neighbors + their neighbors (capped at 50 nodes total).

    Args:
        entity_id (int):
        depth (int | Unset):  Default: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EntityGraphResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        entity_id=entity_id,
        depth=depth,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    entity_id: int,
    *,
    client: AuthenticatedClient,
    depth: int | Unset = 1,
) -> EntityGraphResponse | HTTPValidationError | None:
    """Get Entity Graph

     Return a subgraph centered on entity_id.
    depth=1 → direct neighbors only.
    depth=2 → neighbors + their neighbors (capped at 50 nodes total).

    Args:
        entity_id (int):
        depth (int | Unset):  Default: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EntityGraphResponse | HTTPValidationError
    """

    return sync_detailed(
        entity_id=entity_id,
        client=client,
        depth=depth,
    ).parsed


async def asyncio_detailed(
    entity_id: int,
    *,
    client: AuthenticatedClient,
    depth: int | Unset = 1,
) -> Response[EntityGraphResponse | HTTPValidationError]:
    """Get Entity Graph

     Return a subgraph centered on entity_id.
    depth=1 → direct neighbors only.
    depth=2 → neighbors + their neighbors (capped at 50 nodes total).

    Args:
        entity_id (int):
        depth (int | Unset):  Default: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EntityGraphResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        entity_id=entity_id,
        depth=depth,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    entity_id: int,
    *,
    client: AuthenticatedClient,
    depth: int | Unset = 1,
) -> EntityGraphResponse | HTTPValidationError | None:
    """Get Entity Graph

     Return a subgraph centered on entity_id.
    depth=1 → direct neighbors only.
    depth=2 → neighbors + their neighbors (capped at 50 nodes total).

    Args:
        entity_id (int):
        depth (int | Unset):  Default: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EntityGraphResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            entity_id=entity_id,
            client=client,
            depth=depth,
        )
    ).parsed
