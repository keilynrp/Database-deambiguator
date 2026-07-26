from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response


def _get_kwargs(
    ann_id: int,
    *,
    emoji: str,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["emoji"] = emoji

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/annotations/{ann_id}/react".format(
            ann_id=quote(str(ann_id), safe=""),
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
    ann_id: int,
    *,
    client: AuthenticatedClient,
    emoji: str,
) -> Response[Any | HTTPValidationError]:
    """React To Annotation

     Add or remove an emoji reaction (toggle).
    Pass ?emoji=👍 (URL-encoded) as a query param.
    Allowed: 👍 ❤️ 🚀 👀 ✅ 😄 🎉

    Args:
        ann_id (int):
        emoji (str): Emoji character, e.g. 👍

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        ann_id=ann_id,
        emoji=emoji,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    ann_id: int,
    *,
    client: AuthenticatedClient,
    emoji: str,
) -> Any | HTTPValidationError | None:
    """React To Annotation

     Add or remove an emoji reaction (toggle).
    Pass ?emoji=👍 (URL-encoded) as a query param.
    Allowed: 👍 ❤️ 🚀 👀 ✅ 😄 🎉

    Args:
        ann_id (int):
        emoji (str): Emoji character, e.g. 👍

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        ann_id=ann_id,
        client=client,
        emoji=emoji,
    ).parsed


async def asyncio_detailed(
    ann_id: int,
    *,
    client: AuthenticatedClient,
    emoji: str,
) -> Response[Any | HTTPValidationError]:
    """React To Annotation

     Add or remove an emoji reaction (toggle).
    Pass ?emoji=👍 (URL-encoded) as a query param.
    Allowed: 👍 ❤️ 🚀 👀 ✅ 😄 🎉

    Args:
        ann_id (int):
        emoji (str): Emoji character, e.g. 👍

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        ann_id=ann_id,
        emoji=emoji,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    ann_id: int,
    *,
    client: AuthenticatedClient,
    emoji: str,
) -> Any | HTTPValidationError | None:
    """React To Annotation

     Add or remove an emoji reaction (toggle).
    Pass ?emoji=👍 (URL-encoded) as a query param.
    Allowed: 👍 ❤️ 🚀 👀 ✅ 😄 🎉

    Args:
        ann_id (int):
        emoji (str): Emoji character, e.g. 👍

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            ann_id=ann_id,
            client=client,
            emoji=emoji,
        )
    ).parsed
