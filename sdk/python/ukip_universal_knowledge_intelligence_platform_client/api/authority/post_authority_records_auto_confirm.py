from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    field_name: None | str | Unset = UNSET,
    min_confidence: float | Unset = 0.95,
    reject_losers: bool | Unset = True,
    max_groups: int | Unset = 2000,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_field_name: None | str | Unset
    if isinstance(field_name, Unset):
        json_field_name = UNSET
    else:
        json_field_name = field_name
    params["field_name"] = json_field_name

    params["min_confidence"] = min_confidence

    params["reject_losers"] = reject_losers

    params["max_groups"] = max_groups

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/authority/records/auto-confirm",
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
    field_name: None | str | Unset = UNSET,
    min_confidence: float | Unset = 0.95,
    reject_losers: bool | Unset = True,
    max_groups: int | Unset = 2000,
) -> Response[Any | HTTPValidationError]:
    """Auto Confirm Authority Records

     Auto-confirm the best candidate per distinct value at scale.

    Groups pending records by ``(field_name, original_value)`` — one decision per
    author/institution rather than per candidate — and confirms the top candidate
    when it is auto-confirmable (exact ORCID match or confidence ≥ threshold),
    optionally rejecting that value's losing candidates. Confirmation reuses the
    normal side effects (feedback prior + entity write-back).

    Args:
        field_name (None | str | Unset):
        min_confidence (float | Unset):  Default: 0.95.
        reject_losers (bool | Unset):  Default: True.
        max_groups (int | Unset):  Default: 2000.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        field_name=field_name,
        min_confidence=min_confidence,
        reject_losers=reject_losers,
        max_groups=max_groups,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    field_name: None | str | Unset = UNSET,
    min_confidence: float | Unset = 0.95,
    reject_losers: bool | Unset = True,
    max_groups: int | Unset = 2000,
) -> Any | HTTPValidationError | None:
    """Auto Confirm Authority Records

     Auto-confirm the best candidate per distinct value at scale.

    Groups pending records by ``(field_name, original_value)`` — one decision per
    author/institution rather than per candidate — and confirms the top candidate
    when it is auto-confirmable (exact ORCID match or confidence ≥ threshold),
    optionally rejecting that value's losing candidates. Confirmation reuses the
    normal side effects (feedback prior + entity write-back).

    Args:
        field_name (None | str | Unset):
        min_confidence (float | Unset):  Default: 0.95.
        reject_losers (bool | Unset):  Default: True.
        max_groups (int | Unset):  Default: 2000.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        field_name=field_name,
        min_confidence=min_confidence,
        reject_losers=reject_losers,
        max_groups=max_groups,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    field_name: None | str | Unset = UNSET,
    min_confidence: float | Unset = 0.95,
    reject_losers: bool | Unset = True,
    max_groups: int | Unset = 2000,
) -> Response[Any | HTTPValidationError]:
    """Auto Confirm Authority Records

     Auto-confirm the best candidate per distinct value at scale.

    Groups pending records by ``(field_name, original_value)`` — one decision per
    author/institution rather than per candidate — and confirms the top candidate
    when it is auto-confirmable (exact ORCID match or confidence ≥ threshold),
    optionally rejecting that value's losing candidates. Confirmation reuses the
    normal side effects (feedback prior + entity write-back).

    Args:
        field_name (None | str | Unset):
        min_confidence (float | Unset):  Default: 0.95.
        reject_losers (bool | Unset):  Default: True.
        max_groups (int | Unset):  Default: 2000.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        field_name=field_name,
        min_confidence=min_confidence,
        reject_losers=reject_losers,
        max_groups=max_groups,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    field_name: None | str | Unset = UNSET,
    min_confidence: float | Unset = 0.95,
    reject_losers: bool | Unset = True,
    max_groups: int | Unset = 2000,
) -> Any | HTTPValidationError | None:
    """Auto Confirm Authority Records

     Auto-confirm the best candidate per distinct value at scale.

    Groups pending records by ``(field_name, original_value)`` — one decision per
    author/institution rather than per candidate — and confirms the top candidate
    when it is auto-confirmable (exact ORCID match or confidence ≥ threshold),
    optionally rejecting that value's losing candidates. Confirmation reuses the
    normal side effects (feedback prior + entity write-back).

    Args:
        field_name (None | str | Unset):
        min_confidence (float | Unset):  Default: 0.95.
        reject_losers (bool | Unset):  Default: True.
        max_groups (int | Unset):  Default: 2000.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            field_name=field_name,
            min_confidence=min_confidence,
            reject_losers=reject_losers,
            max_groups=max_groups,
        )
    ).parsed
