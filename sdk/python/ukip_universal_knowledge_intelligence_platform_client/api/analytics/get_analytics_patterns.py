from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    domain_id: str | Unset = "default",
    import_batch_id: int | None | Unset = UNSET,
    provider: None | str | Unset = UNSET,
    portal_slug: None | str | Unset = UNSET,
    limit: int | Unset = 6,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["domain_id"] = domain_id

    json_import_batch_id: int | None | Unset
    if isinstance(import_batch_id, Unset):
        json_import_batch_id = UNSET
    else:
        json_import_batch_id = import_batch_id
    params["import_batch_id"] = json_import_batch_id

    json_provider: None | str | Unset
    if isinstance(provider, Unset):
        json_provider = UNSET
    else:
        json_provider = provider
    params["provider"] = json_provider

    json_portal_slug: None | str | Unset
    if isinstance(portal_slug, Unset):
        json_portal_slug = UNSET
    else:
        json_portal_slug = portal_slug
    params["portal_slug"] = json_portal_slug

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/analytics/patterns",
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
    *,
    client: AuthenticatedClient,
    domain_id: str | Unset = "default",
    import_batch_id: int | None | Unset = UNSET,
    provider: None | str | Unset = UNSET,
    portal_slug: None | str | Unset = UNSET,
    limit: int | Unset = 6,
) -> Response[Any | HTTPValidationError]:
    """Discover Hidden Patterns

     Discover explainable hidden patterns for a domain, import batch, provider, or catalog portal.

    Args:
        domain_id (str | Unset):  Default: 'default'.
        import_batch_id (int | None | Unset):
        provider (None | str | Unset):
        portal_slug (None | str | Unset):
        limit (int | Unset):  Default: 6.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        domain_id=domain_id,
        import_batch_id=import_batch_id,
        provider=provider,
        portal_slug=portal_slug,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    domain_id: str | Unset = "default",
    import_batch_id: int | None | Unset = UNSET,
    provider: None | str | Unset = UNSET,
    portal_slug: None | str | Unset = UNSET,
    limit: int | Unset = 6,
) -> Any | HTTPValidationError | None:
    """Discover Hidden Patterns

     Discover explainable hidden patterns for a domain, import batch, provider, or catalog portal.

    Args:
        domain_id (str | Unset):  Default: 'default'.
        import_batch_id (int | None | Unset):
        provider (None | str | Unset):
        portal_slug (None | str | Unset):
        limit (int | Unset):  Default: 6.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        domain_id=domain_id,
        import_batch_id=import_batch_id,
        provider=provider,
        portal_slug=portal_slug,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    domain_id: str | Unset = "default",
    import_batch_id: int | None | Unset = UNSET,
    provider: None | str | Unset = UNSET,
    portal_slug: None | str | Unset = UNSET,
    limit: int | Unset = 6,
) -> Response[Any | HTTPValidationError]:
    """Discover Hidden Patterns

     Discover explainable hidden patterns for a domain, import batch, provider, or catalog portal.

    Args:
        domain_id (str | Unset):  Default: 'default'.
        import_batch_id (int | None | Unset):
        provider (None | str | Unset):
        portal_slug (None | str | Unset):
        limit (int | Unset):  Default: 6.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        domain_id=domain_id,
        import_batch_id=import_batch_id,
        provider=provider,
        portal_slug=portal_slug,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    domain_id: str | Unset = "default",
    import_batch_id: int | None | Unset = UNSET,
    provider: None | str | Unset = UNSET,
    portal_slug: None | str | Unset = UNSET,
    limit: int | Unset = 6,
) -> Any | HTTPValidationError | None:
    """Discover Hidden Patterns

     Discover explainable hidden patterns for a domain, import batch, provider, or catalog portal.

    Args:
        domain_id (str | Unset):  Default: 'default'.
        import_batch_id (int | None | Unset):
        provider (None | str | Unset):
        portal_slug (None | str | Unset):
        limit (int | Unset):  Default: 6.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            domain_id=domain_id,
            import_batch_id=import_batch_id,
            provider=provider,
            portal_slug=portal_slug,
            limit=limit,
        )
    ).parsed
