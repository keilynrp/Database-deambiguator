from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    domain_id: str | Unset = "all",
    sample_limit: int | Unset = 5,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["domain_id"] = domain_id

    params["sample_limit"] = sample_limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/analytics/abstract-coverage",
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
    domain_id: str | Unset = "all",
    sample_limit: int | Unset = 5,
) -> Response[Any | HTTPValidationError]:
    """Abstract Coverage

     Audit whether tenant-scoped records contain abstract or summary text.

    Args:
        domain_id (str | Unset):  Default: 'all'.
        sample_limit (int | Unset):  Default: 5.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        domain_id=domain_id,
        sample_limit=sample_limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    domain_id: str | Unset = "all",
    sample_limit: int | Unset = 5,
) -> Any | HTTPValidationError | None:
    """Abstract Coverage

     Audit whether tenant-scoped records contain abstract or summary text.

    Args:
        domain_id (str | Unset):  Default: 'all'.
        sample_limit (int | Unset):  Default: 5.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        domain_id=domain_id,
        sample_limit=sample_limit,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    domain_id: str | Unset = "all",
    sample_limit: int | Unset = 5,
) -> Response[Any | HTTPValidationError]:
    """Abstract Coverage

     Audit whether tenant-scoped records contain abstract or summary text.

    Args:
        domain_id (str | Unset):  Default: 'all'.
        sample_limit (int | Unset):  Default: 5.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        domain_id=domain_id,
        sample_limit=sample_limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    domain_id: str | Unset = "all",
    sample_limit: int | Unset = 5,
) -> Any | HTTPValidationError | None:
    """Abstract Coverage

     Audit whether tenant-scoped records contain abstract or summary text.

    Args:
        domain_id (str | Unset):  Default: 'all'.
        sample_limit (int | Unset):  Default: 5.

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
            sample_limit=sample_limit,
        )
    ).parsed
