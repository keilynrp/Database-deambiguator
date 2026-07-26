from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    threshold_id: int,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/authority/thresholds/{threshold_id}".format(
            threshold_id=quote(str(threshold_id), safe=""),
        ),
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
    threshold_id: int,
    *,
    client: AuthenticatedClient,
) -> Response[Any | HTTPValidationError]:
    """Delete Resolution Threshold

     Delete a resolution-threshold override (falls back to defaults).

    Args:
        threshold_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        threshold_id=threshold_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    threshold_id: int,
    *,
    client: AuthenticatedClient,
) -> Any | HTTPValidationError | None:
    """Delete Resolution Threshold

     Delete a resolution-threshold override (falls back to defaults).

    Args:
        threshold_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        threshold_id=threshold_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    threshold_id: int,
    *,
    client: AuthenticatedClient,
) -> Response[Any | HTTPValidationError]:
    """Delete Resolution Threshold

     Delete a resolution-threshold override (falls back to defaults).

    Args:
        threshold_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        threshold_id=threshold_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    threshold_id: int,
    *,
    client: AuthenticatedClient,
) -> Any | HTTPValidationError | None:
    """Delete Resolution Threshold

     Delete a resolution-threshold override (falls back to defaults).

    Args:
        threshold_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            threshold_id=threshold_id,
            client=client,
        )
    ).parsed
