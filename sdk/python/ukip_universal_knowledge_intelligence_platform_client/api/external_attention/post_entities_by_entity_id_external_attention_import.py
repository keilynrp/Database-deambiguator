from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.single_entity_observation_input import SingleEntityObservationInput
from ...models.single_import_response import SingleImportResponse
from ...types import Response


def _get_kwargs(
    entity_id: int,
    *,
    body: list[SingleEntityObservationInput],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/entities/{entity_id}/external-attention/import".format(
            entity_id=quote(str(entity_id), safe=""),
        ),
    }

    _kwargs["json"] = []
    for body_item_data in body:
        body_item = body_item_data.to_dict()
        _kwargs["json"].append(body_item)

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | SingleImportResponse | None:
    if response.status_code == 201:
        response_201 = SingleImportResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | SingleImportResponse]:
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
    body: list[SingleEntityObservationInput],
) -> Response[HTTPValidationError | SingleImportResponse]:
    """Single Entity Import

     Import external attention observations for a single entity.

    Args:
        entity_id (int):
        body (list[SingleEntityObservationInput]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SingleImportResponse]
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
    body: list[SingleEntityObservationInput],
) -> HTTPValidationError | SingleImportResponse | None:
    """Single Entity Import

     Import external attention observations for a single entity.

    Args:
        entity_id (int):
        body (list[SingleEntityObservationInput]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SingleImportResponse
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
    body: list[SingleEntityObservationInput],
) -> Response[HTTPValidationError | SingleImportResponse]:
    """Single Entity Import

     Import external attention observations for a single entity.

    Args:
        entity_id (int):
        body (list[SingleEntityObservationInput]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SingleImportResponse]
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
    body: list[SingleEntityObservationInput],
) -> HTTPValidationError | SingleImportResponse | None:
    """Single Entity Import

     Import external attention observations for a single entity.

    Args:
        entity_id (int):
        body (list[SingleEntityObservationInput]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SingleImportResponse
    """

    return (
        await asyncio_detailed(
            entity_id=entity_id,
            client=client,
            body=body,
        )
    ).parsed
