from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.field_correspondence_evidence_score import FieldCorrespondenceEvidenceScore
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    active: bool | None | Unset = UNSET,
    source_schema: None | str | Unset = UNSET,
    limit: int | Unset = 100,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_active: bool | None | Unset
    if isinstance(active, Unset):
        json_active = UNSET
    else:
        json_active = active
    params["active"] = json_active

    json_source_schema: None | str | Unset
    if isinstance(source_schema, Unset):
        json_source_schema = UNSET
    else:
        json_source_schema = source_schema
    params["source_schema"] = json_source_schema

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/field-correspondence-rules/evidence-scores",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | list[FieldCorrespondenceEvidenceScore] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = FieldCorrespondenceEvidenceScore.from_dict(response_200_item_data)

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
) -> Response[HTTPValidationError | list[FieldCorrespondenceEvidenceScore]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    active: bool | None | Unset = UNSET,
    source_schema: None | str | Unset = UNSET,
    limit: int | Unset = 100,
) -> Response[HTTPValidationError | list[FieldCorrespondenceEvidenceScore]]:
    """Score Field Correspondence Rule Evidence

     Score visible rules against real records/suggestions so admins can prioritize review.

    Args:
        active (bool | None | Unset):
        source_schema (None | str | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[FieldCorrespondenceEvidenceScore]]
    """

    kwargs = _get_kwargs(
        active=active,
        source_schema=source_schema,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    active: bool | None | Unset = UNSET,
    source_schema: None | str | Unset = UNSET,
    limit: int | Unset = 100,
) -> HTTPValidationError | list[FieldCorrespondenceEvidenceScore] | None:
    """Score Field Correspondence Rule Evidence

     Score visible rules against real records/suggestions so admins can prioritize review.

    Args:
        active (bool | None | Unset):
        source_schema (None | str | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[FieldCorrespondenceEvidenceScore]
    """

    return sync_detailed(
        client=client,
        active=active,
        source_schema=source_schema,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    active: bool | None | Unset = UNSET,
    source_schema: None | str | Unset = UNSET,
    limit: int | Unset = 100,
) -> Response[HTTPValidationError | list[FieldCorrespondenceEvidenceScore]]:
    """Score Field Correspondence Rule Evidence

     Score visible rules against real records/suggestions so admins can prioritize review.

    Args:
        active (bool | None | Unset):
        source_schema (None | str | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[FieldCorrespondenceEvidenceScore]]
    """

    kwargs = _get_kwargs(
        active=active,
        source_schema=source_schema,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    active: bool | None | Unset = UNSET,
    source_schema: None | str | Unset = UNSET,
    limit: int | Unset = 100,
) -> HTTPValidationError | list[FieldCorrespondenceEvidenceScore] | None:
    """Score Field Correspondence Rule Evidence

     Score visible rules against real records/suggestions so admins can prioritize review.

    Args:
        active (bool | None | Unset):
        source_schema (None | str | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[FieldCorrespondenceEvidenceScore]
    """

    return (
        await asyncio_detailed(
            client=client,
            active=active,
            source_schema=source_schema,
            limit=limit,
        )
    ).parsed
