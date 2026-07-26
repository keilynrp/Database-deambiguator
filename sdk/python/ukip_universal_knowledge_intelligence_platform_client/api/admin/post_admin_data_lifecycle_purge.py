from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_admin_data_lifecycle_purge_response_post_admin_data_lifecycle_purge import (
    PostAdminDataLifecyclePurgeResponsePostAdminDataLifecyclePurge,
)
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/admin/data-lifecycle/purge",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PostAdminDataLifecyclePurgeResponsePostAdminDataLifecyclePurge | None:
    if response.status_code == 200:
        response_200 = PostAdminDataLifecyclePurgeResponsePostAdminDataLifecyclePurge.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PostAdminDataLifecyclePurgeResponsePostAdminDataLifecyclePurge]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[PostAdminDataLifecyclePurgeResponsePostAdminDataLifecyclePurge]:
    """Trigger Retention Purge

     Manually trigger a retention purge run (super_admin only).

    Scans all orgs with a retention policy and purges expired data.
    Same logic as the scheduled RetentionPurger loop.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostAdminDataLifecyclePurgeResponsePostAdminDataLifecyclePurge]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> PostAdminDataLifecyclePurgeResponsePostAdminDataLifecyclePurge | None:
    """Trigger Retention Purge

     Manually trigger a retention purge run (super_admin only).

    Scans all orgs with a retention policy and purges expired data.
    Same logic as the scheduled RetentionPurger loop.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostAdminDataLifecyclePurgeResponsePostAdminDataLifecyclePurge
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[PostAdminDataLifecyclePurgeResponsePostAdminDataLifecyclePurge]:
    """Trigger Retention Purge

     Manually trigger a retention purge run (super_admin only).

    Scans all orgs with a retention policy and purges expired data.
    Same logic as the scheduled RetentionPurger loop.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostAdminDataLifecyclePurgeResponsePostAdminDataLifecyclePurge]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> PostAdminDataLifecyclePurgeResponsePostAdminDataLifecyclePurge | None:
    """Trigger Retention Purge

     Manually trigger a retention purge run (super_admin only).

    Scans all orgs with a retention policy and purges expired data.
    Same logic as the scheduled RetentionPurger loop.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostAdminDataLifecyclePurgeResponsePostAdminDataLifecyclePurge
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
