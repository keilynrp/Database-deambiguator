from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.deletion_request import DeletionRequest
from ...models.http_validation_error import HTTPValidationError
from ...models.post_admin_data_lifecycle_delete_response_post_admin_data_lifecycle_delete import (
    PostAdminDataLifecycleDeleteResponsePostAdminDataLifecycleDelete,
)
from ...types import Response


def _get_kwargs(
    *,
    body: DeletionRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/admin/data-lifecycle/delete",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | PostAdminDataLifecycleDeleteResponsePostAdminDataLifecycleDelete | None:
    if response.status_code == 200:
        response_200 = PostAdminDataLifecycleDeleteResponsePostAdminDataLifecycleDelete.from_dict(response.json())

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
) -> Response[HTTPValidationError | PostAdminDataLifecycleDeleteResponsePostAdminDataLifecycleDelete]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: DeletionRequest,
) -> Response[HTTPValidationError | PostAdminDataLifecycleDeleteResponsePostAdminDataLifecycleDelete]:
    r"""Delete Tenant Data

     Erase all org-scoped data for the active tenant (right to erasure / GDPR Art. 17).

    **Irreversible.** Requires an explicit confirmation string:
        ``{\"confirm\": \"DELETE org <org_id>\"}``

    Cascade: erases every tenant-owned DB surface plus the corresponding
    ChromaDB vector documents. DataLifecycleEvent audit records are retained
    as compliance evidence. Records a completed event with per-store counts.

    Args:
        body (DeletionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PostAdminDataLifecycleDeleteResponsePostAdminDataLifecycleDelete]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: DeletionRequest,
) -> HTTPValidationError | PostAdminDataLifecycleDeleteResponsePostAdminDataLifecycleDelete | None:
    r"""Delete Tenant Data

     Erase all org-scoped data for the active tenant (right to erasure / GDPR Art. 17).

    **Irreversible.** Requires an explicit confirmation string:
        ``{\"confirm\": \"DELETE org <org_id>\"}``

    Cascade: erases every tenant-owned DB surface plus the corresponding
    ChromaDB vector documents. DataLifecycleEvent audit records are retained
    as compliance evidence. Records a completed event with per-store counts.

    Args:
        body (DeletionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PostAdminDataLifecycleDeleteResponsePostAdminDataLifecycleDelete
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: DeletionRequest,
) -> Response[HTTPValidationError | PostAdminDataLifecycleDeleteResponsePostAdminDataLifecycleDelete]:
    r"""Delete Tenant Data

     Erase all org-scoped data for the active tenant (right to erasure / GDPR Art. 17).

    **Irreversible.** Requires an explicit confirmation string:
        ``{\"confirm\": \"DELETE org <org_id>\"}``

    Cascade: erases every tenant-owned DB surface plus the corresponding
    ChromaDB vector documents. DataLifecycleEvent audit records are retained
    as compliance evidence. Records a completed event with per-store counts.

    Args:
        body (DeletionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PostAdminDataLifecycleDeleteResponsePostAdminDataLifecycleDelete]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: DeletionRequest,
) -> HTTPValidationError | PostAdminDataLifecycleDeleteResponsePostAdminDataLifecycleDelete | None:
    r"""Delete Tenant Data

     Erase all org-scoped data for the active tenant (right to erasure / GDPR Art. 17).

    **Irreversible.** Requires an explicit confirmation string:
        ``{\"confirm\": \"DELETE org <org_id>\"}``

    Cascade: erases every tenant-owned DB surface plus the corresponding
    ChromaDB vector documents. DataLifecycleEvent audit records are retained
    as compliance evidence. Records a completed event with per-store counts.

    Args:
        body (DeletionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PostAdminDataLifecycleDeleteResponsePostAdminDataLifecycleDelete
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
