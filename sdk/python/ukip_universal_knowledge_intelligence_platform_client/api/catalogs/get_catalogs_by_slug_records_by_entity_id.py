from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.entity import Entity
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    slug: str,
    entity_id: int,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/catalogs/{slug}/records/{entity_id}".format(
            slug=quote(str(slug), safe=""),
            entity_id=quote(str(entity_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Entity | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = Entity.from_dict(response.json())

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
) -> Response[Entity | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    slug: str,
    entity_id: int,
    *,
    client: AuthenticatedClient,
) -> Response[Entity | HTTPValidationError]:
    """Get Catalog Record

    Args:
        slug (str):
        entity_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Entity | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        slug=slug,
        entity_id=entity_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    slug: str,
    entity_id: int,
    *,
    client: AuthenticatedClient,
) -> Entity | HTTPValidationError | None:
    """Get Catalog Record

    Args:
        slug (str):
        entity_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Entity | HTTPValidationError
    """

    return sync_detailed(
        slug=slug,
        entity_id=entity_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    slug: str,
    entity_id: int,
    *,
    client: AuthenticatedClient,
) -> Response[Entity | HTTPValidationError]:
    """Get Catalog Record

    Args:
        slug (str):
        entity_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Entity | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        slug=slug,
        entity_id=entity_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    slug: str,
    entity_id: int,
    *,
    client: AuthenticatedClient,
) -> Entity | HTTPValidationError | None:
    """Get Catalog Record

    Args:
        slug (str):
        entity_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Entity | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            slug=slug,
            entity_id=entity_id,
            client=client,
        )
    ).parsed
