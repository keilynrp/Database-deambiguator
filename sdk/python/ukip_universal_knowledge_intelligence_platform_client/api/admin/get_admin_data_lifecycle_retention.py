from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_admin_data_lifecycle_retention_response_get_admin_data_lifecycle_retention import (
    GetAdminDataLifecycleRetentionResponseGetAdminDataLifecycleRetention,
)
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/data-lifecycle/retention",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetAdminDataLifecycleRetentionResponseGetAdminDataLifecycleRetention | None:
    if response.status_code == 200:
        response_200 = GetAdminDataLifecycleRetentionResponseGetAdminDataLifecycleRetention.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetAdminDataLifecycleRetentionResponseGetAdminDataLifecycleRetention]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[GetAdminDataLifecycleRetentionResponseGetAdminDataLifecycleRetention]:
    """Get Retention Policy

     Return the retention policy for the active org (or the platform default if none set).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetAdminDataLifecycleRetentionResponseGetAdminDataLifecycleRetention]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> GetAdminDataLifecycleRetentionResponseGetAdminDataLifecycleRetention | None:
    """Get Retention Policy

     Return the retention policy for the active org (or the platform default if none set).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetAdminDataLifecycleRetentionResponseGetAdminDataLifecycleRetention
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[GetAdminDataLifecycleRetentionResponseGetAdminDataLifecycleRetention]:
    """Get Retention Policy

     Return the retention policy for the active org (or the platform default if none set).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetAdminDataLifecycleRetentionResponseGetAdminDataLifecycleRetention]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> GetAdminDataLifecycleRetentionResponseGetAdminDataLifecycleRetention | None:
    """Get Retention Policy

     Return the retention policy for the active org (or the platform default if none set).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetAdminDataLifecycleRetentionResponseGetAdminDataLifecycleRetention
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
