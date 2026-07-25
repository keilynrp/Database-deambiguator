from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    status: None | str | Unset = "pending",
    review_required: bool | None | Unset = True,
    route: None | str | Unset = UNSET,
    nil_only: bool | Unset = False,
    skip: int | Unset = 0,
    limit: int | Unset = 50,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_status: None | str | Unset
    if isinstance(status, Unset):
        json_status = UNSET
    else:
        json_status = status
    params["status"] = json_status

    json_review_required: bool | None | Unset
    if isinstance(review_required, Unset):
        json_review_required = UNSET
    else:
        json_review_required = review_required
    params["review_required"] = json_review_required

    json_route: None | str | Unset
    if isinstance(route, Unset):
        json_route = UNSET
    else:
        json_route = route
    params["route"] = json_route

    params["nil_only"] = nil_only

    params["skip"] = skip

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/authority/authors/review-queue",
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
    status: None | str | Unset = "pending",
    review_required: bool | None | Unset = True,
    route: None | str | Unset = UNSET,
    nil_only: bool | Unset = False,
    skip: int | Unset = 0,
    limit: int | Unset = 50,
) -> Response[Any | HTTPValidationError]:
    """Author Review Queue

     Author-only operational queue.

    This is intentionally scoped to records created by the adaptive author
    pipeline (identified by a non-null `resolution_route`). It gives the
    frontend a stable review surface without disturbing the legacy authority
    endpoints used for generic entity reconciliation.

    Args:
        status (None | str | Unset):  Default: 'pending'.
        review_required (bool | None | Unset):  Default: True.
        route (None | str | Unset):
        nil_only (bool | Unset):  Default: False.
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        status=status,
        review_required=review_required,
        route=route,
        nil_only=nil_only,
        skip=skip,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    status: None | str | Unset = "pending",
    review_required: bool | None | Unset = True,
    route: None | str | Unset = UNSET,
    nil_only: bool | Unset = False,
    skip: int | Unset = 0,
    limit: int | Unset = 50,
) -> Any | HTTPValidationError | None:
    """Author Review Queue

     Author-only operational queue.

    This is intentionally scoped to records created by the adaptive author
    pipeline (identified by a non-null `resolution_route`). It gives the
    frontend a stable review surface without disturbing the legacy authority
    endpoints used for generic entity reconciliation.

    Args:
        status (None | str | Unset):  Default: 'pending'.
        review_required (bool | None | Unset):  Default: True.
        route (None | str | Unset):
        nil_only (bool | Unset):  Default: False.
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        status=status,
        review_required=review_required,
        route=route,
        nil_only=nil_only,
        skip=skip,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    status: None | str | Unset = "pending",
    review_required: bool | None | Unset = True,
    route: None | str | Unset = UNSET,
    nil_only: bool | Unset = False,
    skip: int | Unset = 0,
    limit: int | Unset = 50,
) -> Response[Any | HTTPValidationError]:
    """Author Review Queue

     Author-only operational queue.

    This is intentionally scoped to records created by the adaptive author
    pipeline (identified by a non-null `resolution_route`). It gives the
    frontend a stable review surface without disturbing the legacy authority
    endpoints used for generic entity reconciliation.

    Args:
        status (None | str | Unset):  Default: 'pending'.
        review_required (bool | None | Unset):  Default: True.
        route (None | str | Unset):
        nil_only (bool | Unset):  Default: False.
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        status=status,
        review_required=review_required,
        route=route,
        nil_only=nil_only,
        skip=skip,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    status: None | str | Unset = "pending",
    review_required: bool | None | Unset = True,
    route: None | str | Unset = UNSET,
    nil_only: bool | Unset = False,
    skip: int | Unset = 0,
    limit: int | Unset = 50,
) -> Any | HTTPValidationError | None:
    """Author Review Queue

     Author-only operational queue.

    This is intentionally scoped to records created by the adaptive author
    pipeline (identified by a non-null `resolution_route`). It gives the
    frontend a stable review surface without disturbing the legacy authority
    endpoints used for generic entity reconciliation.

    Args:
        status (None | str | Unset):  Default: 'pending'.
        review_required (bool | None | Unset):  Default: True.
        route (None | str | Unset):
        nil_only (bool | Unset):  Default: False.
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            status=status,
            review_required=review_required,
            route=route,
            nil_only=nil_only,
            skip=skip,
            limit=limit,
        )
    ).parsed
