from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.entity_relationship_create import EntityRelationshipCreate
from ...models.entity_relationship_response import EntityRelationshipResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    entity_id: int,
    *,
    body: EntityRelationshipCreate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/entities/{entity_id}/relationships".format(
            entity_id=quote(str(entity_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> EntityRelationshipResponse | HTTPValidationError | None:
    if response.status_code == 201:
        response_201 = EntityRelationshipResponse.from_dict(response.json())

        return response_201

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[EntityRelationshipResponse | HTTPValidationError]:
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
    body: EntityRelationshipCreate,
) -> Response[EntityRelationshipResponse | HTTPValidationError]:
    """Create Relationship

     Create a directed relationship from entity_id → target_id.

    Args:
        entity_id (int):
        body (EntityRelationshipCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EntityRelationshipResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        entity_id=entity_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    entity_id: int,
    *,
    client: AuthenticatedClient,
    body: EntityRelationshipCreate,
) -> EntityRelationshipResponse | HTTPValidationError | None:
    """Create Relationship

     Create a directed relationship from entity_id → target_id.

    Args:
        entity_id (int):
        body (EntityRelationshipCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EntityRelationshipResponse | HTTPValidationError
    """

    return sync_detailed(
        entity_id=entity_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    entity_id: int,
    *,
    client: AuthenticatedClient,
    body: EntityRelationshipCreate,
) -> Response[EntityRelationshipResponse | HTTPValidationError]:
    """Create Relationship

     Create a directed relationship from entity_id → target_id.

    Args:
        entity_id (int):
        body (EntityRelationshipCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EntityRelationshipResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        entity_id=entity_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    entity_id: int,
    *,
    client: AuthenticatedClient,
    body: EntityRelationshipCreate,
) -> EntityRelationshipResponse | HTTPValidationError | None:
    """Create Relationship

     Create a directed relationship from entity_id → target_id.

    Args:
        entity_id (int):
        body (EntityRelationshipCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EntityRelationshipResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            entity_id=entity_id,
            client=client,
            body=body,
        )
    ).parsed
