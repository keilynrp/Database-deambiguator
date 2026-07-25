from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    import_batch_id: int | None | Unset = UNSET,
    entity_id: int | None | Unset = UNSET,
    domain: None | str | Unset = UNSET,
    limit: int | Unset = 25,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_import_batch_id: int | None | Unset
    if isinstance(import_batch_id, Unset):
        json_import_batch_id = UNSET
    else:
        json_import_batch_id = import_batch_id
    params["import_batch_id"] = json_import_batch_id

    json_entity_id: int | None | Unset
    if isinstance(entity_id, Unset):
        json_entity_id = UNSET
    else:
        json_entity_id = entity_id
    params["entity_id"] = json_entity_id

    json_domain: None | str | Unset
    if isinstance(domain, Unset):
        json_domain = UNSET
    else:
        json_domain = domain
    params["domain"] = json_domain

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/graph/materialize",
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
    import_batch_id: int | None | Unset = UNSET,
    entity_id: int | None | Unset = UNSET,
    domain: None | str | Unset = UNSET,
    limit: int | Unset = 25,
) -> Response[Any | HTTPValidationError]:
    """Materialize Graph

     Backfill graph relationships for previously ingested/enriched records.

    Args:
        import_batch_id (int | None | Unset):
        entity_id (int | None | Unset):
        domain (None | str | Unset):
        limit (int | Unset):  Default: 25.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        import_batch_id=import_batch_id,
        entity_id=entity_id,
        domain=domain,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    import_batch_id: int | None | Unset = UNSET,
    entity_id: int | None | Unset = UNSET,
    domain: None | str | Unset = UNSET,
    limit: int | Unset = 25,
) -> Any | HTTPValidationError | None:
    """Materialize Graph

     Backfill graph relationships for previously ingested/enriched records.

    Args:
        import_batch_id (int | None | Unset):
        entity_id (int | None | Unset):
        domain (None | str | Unset):
        limit (int | Unset):  Default: 25.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        import_batch_id=import_batch_id,
        entity_id=entity_id,
        domain=domain,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    import_batch_id: int | None | Unset = UNSET,
    entity_id: int | None | Unset = UNSET,
    domain: None | str | Unset = UNSET,
    limit: int | Unset = 25,
) -> Response[Any | HTTPValidationError]:
    """Materialize Graph

     Backfill graph relationships for previously ingested/enriched records.

    Args:
        import_batch_id (int | None | Unset):
        entity_id (int | None | Unset):
        domain (None | str | Unset):
        limit (int | Unset):  Default: 25.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        import_batch_id=import_batch_id,
        entity_id=entity_id,
        domain=domain,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    import_batch_id: int | None | Unset = UNSET,
    entity_id: int | None | Unset = UNSET,
    domain: None | str | Unset = UNSET,
    limit: int | Unset = 25,
) -> Any | HTTPValidationError | None:
    """Materialize Graph

     Backfill graph relationships for previously ingested/enriched records.

    Args:
        import_batch_id (int | None | Unset):
        entity_id (int | None | Unset):
        domain (None | str | Unset):
        limit (int | Unset):  Default: 25.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            import_batch_id=import_batch_id,
            entity_id=entity_id,
            domain=domain,
            limit=limit,
        )
    ).parsed
