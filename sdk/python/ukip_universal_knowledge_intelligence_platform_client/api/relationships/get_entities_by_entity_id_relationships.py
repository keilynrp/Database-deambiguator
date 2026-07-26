from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.entity_relationship_response import EntityRelationshipResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    entity_id: int,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/entities/{entity_id}/relationships".format(
            entity_id=quote(str(entity_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | list[EntityRelationshipResponse] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = EntityRelationshipResponse.from_dict(response_200_item_data)

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
) -> Response[HTTPValidationError | list[EntityRelationshipResponse]]:
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
) -> Response[HTTPValidationError | list[EntityRelationshipResponse]]:
    """List Relationships

     List all relationships where this entity is source or target.

    Args:
        entity_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[EntityRelationshipResponse]]
    """

    kwargs = _get_kwargs(
        entity_id=entity_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    entity_id: int,
    *,
    client: AuthenticatedClient,
) -> HTTPValidationError | list[EntityRelationshipResponse] | None:
    """List Relationships

     List all relationships where this entity is source or target.

    Args:
        entity_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[EntityRelationshipResponse]
    """

    return sync_detailed(
        entity_id=entity_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    entity_id: int,
    *,
    client: AuthenticatedClient,
) -> Response[HTTPValidationError | list[EntityRelationshipResponse]]:
    """List Relationships

     List all relationships where this entity is source or target.

    Args:
        entity_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[EntityRelationshipResponse]]
    """

    kwargs = _get_kwargs(
        entity_id=entity_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    entity_id: int,
    *,
    client: AuthenticatedClient,
) -> HTTPValidationError | list[EntityRelationshipResponse] | None:
    """List Relationships

     List all relationships where this entity is source or target.

    Args:
        entity_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[EntityRelationshipResponse]
    """

    return (
        await asyncio_detailed(
            entity_id=entity_id,
            client=client,
        )
    ).parsed
