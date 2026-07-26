from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.field_correspondence_audit_entry import FieldCorrespondenceAuditEntry
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    rule_id: int,
    *,
    limit: int | Unset = 25,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/field-correspondence-rules/{rule_id}/audit".format(
            rule_id=quote(str(rule_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | list[FieldCorrespondenceAuditEntry] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = FieldCorrespondenceAuditEntry.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[HTTPValidationError | list[FieldCorrespondenceAuditEntry]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    rule_id: int,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 25,
) -> Response[HTTPValidationError | list[FieldCorrespondenceAuditEntry]]:
    """List Field Correspondence Rule Audit

     Return audit history for a governed correspondence rule.

    Args:
        rule_id (int):
        limit (int | Unset):  Default: 25.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[FieldCorrespondenceAuditEntry]]
    """

    kwargs = _get_kwargs(
        rule_id=rule_id,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    rule_id: int,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 25,
) -> HTTPValidationError | list[FieldCorrespondenceAuditEntry] | None:
    """List Field Correspondence Rule Audit

     Return audit history for a governed correspondence rule.

    Args:
        rule_id (int):
        limit (int | Unset):  Default: 25.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[FieldCorrespondenceAuditEntry]
    """

    return sync_detailed(
        rule_id=rule_id,
        client=client,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    rule_id: int,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 25,
) -> Response[HTTPValidationError | list[FieldCorrespondenceAuditEntry]]:
    """List Field Correspondence Rule Audit

     Return audit history for a governed correspondence rule.

    Args:
        rule_id (int):
        limit (int | Unset):  Default: 25.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[FieldCorrespondenceAuditEntry]]
    """

    kwargs = _get_kwargs(
        rule_id=rule_id,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    rule_id: int,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 25,
) -> HTTPValidationError | list[FieldCorrespondenceAuditEntry] | None:
    """List Field Correspondence Rule Audit

     Return audit history for a governed correspondence rule.

    Args:
        rule_id (int):
        limit (int | Unset):  Default: 25.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[FieldCorrespondenceAuditEntry]
    """

    return (
        await asyncio_detailed(
            rule_id=rule_id,
            client=client,
            limit=limit,
        )
    ).parsed
