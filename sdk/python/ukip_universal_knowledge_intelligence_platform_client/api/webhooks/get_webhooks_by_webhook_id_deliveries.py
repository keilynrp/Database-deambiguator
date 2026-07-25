from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    webhook_id: int,
    *,
    page: int | Unset = 1,
    size: int | Unset = 20,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["page"] = page

    params["size"] = size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/webhooks/{webhook_id}/deliveries".format(
            webhook_id=quote(str(webhook_id), safe=""),
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
    webhook_id: int,
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    size: int | Unset = 20,
) -> Response[Any | HTTPValidationError]:
    """List Deliveries

     Paginated delivery history for a single webhook, newest first.

    Args:
        webhook_id (int):
        page (int | Unset):  Default: 1.
        size (int | Unset):  Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        webhook_id=webhook_id,
        page=page,
        size=size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    webhook_id: int,
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    size: int | Unset = 20,
) -> Any | HTTPValidationError | None:
    """List Deliveries

     Paginated delivery history for a single webhook, newest first.

    Args:
        webhook_id (int):
        page (int | Unset):  Default: 1.
        size (int | Unset):  Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        webhook_id=webhook_id,
        client=client,
        page=page,
        size=size,
    ).parsed


async def asyncio_detailed(
    webhook_id: int,
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    size: int | Unset = 20,
) -> Response[Any | HTTPValidationError]:
    """List Deliveries

     Paginated delivery history for a single webhook, newest first.

    Args:
        webhook_id (int):
        page (int | Unset):  Default: 1.
        size (int | Unset):  Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        webhook_id=webhook_id,
        page=page,
        size=size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    webhook_id: int,
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    size: int | Unset = 20,
) -> Any | HTTPValidationError | None:
    """List Deliveries

     Paginated delivery history for a single webhook, newest first.

    Args:
        webhook_id (int):
        page (int | Unset):  Default: 1.
        size (int | Unset):  Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            webhook_id=webhook_id,
            client=client,
            page=page,
            size=size,
        )
    ).parsed
