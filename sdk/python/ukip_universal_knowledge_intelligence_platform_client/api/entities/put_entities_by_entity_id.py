from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.entity import Entity
from ...models.entity_base import EntityBase
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    entity_id: int,
    *,
    body: EntityBase,
    language: None | str | Unset = UNSET,
    accept_language: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(accept_language, Unset):
        headers["accept-language"] = accept_language

    params: dict[str, Any] = {}

    json_language: None | str | Unset
    if isinstance(language, Unset):
        json_language = UNSET
    else:
        json_language = language
    params["language"] = json_language

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/entities/{entity_id}".format(
            entity_id=quote(str(entity_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
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
    entity_id: int,
    *,
    client: AuthenticatedClient,
    body: EntityBase,
    language: None | str | Unset = UNSET,
    accept_language: None | str | Unset = UNSET,
) -> Response[Entity | HTTPValidationError]:
    """Update Entity

    Args:
        entity_id (int):
        language (None | str | Unset): Language for catalog-sourced text (en, es). Falls back to
            Accept-Language, then English.
        accept_language (None | str | Unset):
        body (EntityBase):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Entity | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        entity_id=entity_id,
        body=body,
        language=language,
        accept_language=accept_language,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    entity_id: int,
    *,
    client: AuthenticatedClient,
    body: EntityBase,
    language: None | str | Unset = UNSET,
    accept_language: None | str | Unset = UNSET,
) -> Entity | HTTPValidationError | None:
    """Update Entity

    Args:
        entity_id (int):
        language (None | str | Unset): Language for catalog-sourced text (en, es). Falls back to
            Accept-Language, then English.
        accept_language (None | str | Unset):
        body (EntityBase):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Entity | HTTPValidationError
    """

    return sync_detailed(
        entity_id=entity_id,
        client=client,
        body=body,
        language=language,
        accept_language=accept_language,
    ).parsed


async def asyncio_detailed(
    entity_id: int,
    *,
    client: AuthenticatedClient,
    body: EntityBase,
    language: None | str | Unset = UNSET,
    accept_language: None | str | Unset = UNSET,
) -> Response[Entity | HTTPValidationError]:
    """Update Entity

    Args:
        entity_id (int):
        language (None | str | Unset): Language for catalog-sourced text (en, es). Falls back to
            Accept-Language, then English.
        accept_language (None | str | Unset):
        body (EntityBase):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Entity | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        entity_id=entity_id,
        body=body,
        language=language,
        accept_language=accept_language,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    entity_id: int,
    *,
    client: AuthenticatedClient,
    body: EntityBase,
    language: None | str | Unset = UNSET,
    accept_language: None | str | Unset = UNSET,
) -> Entity | HTTPValidationError | None:
    """Update Entity

    Args:
        entity_id (int):
        language (None | str | Unset): Language for catalog-sourced text (en, es). Falls back to
            Accept-Language, then English.
        accept_language (None | str | Unset):
        body (EntityBase):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Entity | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            entity_id=entity_id,
            client=client,
            body=body,
            language=language,
            accept_language=accept_language,
        )
    ).parsed
