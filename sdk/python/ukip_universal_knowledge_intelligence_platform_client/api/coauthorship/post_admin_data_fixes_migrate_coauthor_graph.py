from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.migrate_coauthor_request import MigrateCoauthorRequest
from ...models.post_admin_data_fixes_migrate_coauthor_graph_response_post_admin_data_fixes_migrate_coauthor_graph import (
    PostAdminDataFixesMigrateCoauthorGraphResponsePostAdminDataFixesMigrateCoauthorGraph,
)
from ...types import Response


def _get_kwargs(
    *,
    body: MigrateCoauthorRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/admin/data-fixes/migrate-coauthor-graph",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | PostAdminDataFixesMigrateCoauthorGraphResponsePostAdminDataFixesMigrateCoauthorGraph | None:
    if response.status_code == 200:
        response_200 = PostAdminDataFixesMigrateCoauthorGraphResponsePostAdminDataFixesMigrateCoauthorGraph.from_dict(
            response.json()
        )

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
) -> Response[
    HTTPValidationError | PostAdminDataFixesMigrateCoauthorGraphResponsePostAdminDataFixesMigrateCoauthorGraph
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: MigrateCoauthorRequest,
) -> Response[
    HTTPValidationError | PostAdminDataFixesMigrateCoauthorGraphResponsePostAdminDataFixesMigrateCoauthorGraph
]:
    """Migrate Coauthor Graph Endpoint

     Run the one-shot legacy -> V2 coauthorship migration. Idempotent.
    Defaults to dry-run; callers must explicitly opt out to mutate data.

    Args:
        body (MigrateCoauthorRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PostAdminDataFixesMigrateCoauthorGraphResponsePostAdminDataFixesMigrateCoauthorGraph]
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
    body: MigrateCoauthorRequest,
) -> HTTPValidationError | PostAdminDataFixesMigrateCoauthorGraphResponsePostAdminDataFixesMigrateCoauthorGraph | None:
    """Migrate Coauthor Graph Endpoint

     Run the one-shot legacy -> V2 coauthorship migration. Idempotent.
    Defaults to dry-run; callers must explicitly opt out to mutate data.

    Args:
        body (MigrateCoauthorRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PostAdminDataFixesMigrateCoauthorGraphResponsePostAdminDataFixesMigrateCoauthorGraph
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: MigrateCoauthorRequest,
) -> Response[
    HTTPValidationError | PostAdminDataFixesMigrateCoauthorGraphResponsePostAdminDataFixesMigrateCoauthorGraph
]:
    """Migrate Coauthor Graph Endpoint

     Run the one-shot legacy -> V2 coauthorship migration. Idempotent.
    Defaults to dry-run; callers must explicitly opt out to mutate data.

    Args:
        body (MigrateCoauthorRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PostAdminDataFixesMigrateCoauthorGraphResponsePostAdminDataFixesMigrateCoauthorGraph]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: MigrateCoauthorRequest,
) -> HTTPValidationError | PostAdminDataFixesMigrateCoauthorGraphResponsePostAdminDataFixesMigrateCoauthorGraph | None:
    """Migrate Coauthor Graph Endpoint

     Run the one-shot legacy -> V2 coauthorship migration. Idempotent.
    Defaults to dry-run; callers must explicitly opt out to mutate data.

    Args:
        body (MigrateCoauthorRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PostAdminDataFixesMigrateCoauthorGraphResponsePostAdminDataFixesMigrateCoauthorGraph
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
