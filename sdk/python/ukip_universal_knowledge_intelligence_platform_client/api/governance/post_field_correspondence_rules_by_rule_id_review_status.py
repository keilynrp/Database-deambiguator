from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.field_correspondence_review_payload import FieldCorrespondenceReviewPayload
from ...models.field_correspondence_rule_response import FieldCorrespondenceRuleResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    rule_id: int,
    *,
    body: FieldCorrespondenceReviewPayload,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/field-correspondence-rules/{rule_id}/review-status".format(
            rule_id=quote(str(rule_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> FieldCorrespondenceRuleResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = FieldCorrespondenceRuleResponse.from_dict(response.json())

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
) -> Response[FieldCorrespondenceRuleResponse | HTTPValidationError]:
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
    body: FieldCorrespondenceReviewPayload,
) -> Response[FieldCorrespondenceRuleResponse | HTTPValidationError]:
    """Set Field Correspondence Review Status

     Mark an admin review decision without losing rule history.

    Args:
        rule_id (int):
        body (FieldCorrespondenceReviewPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[FieldCorrespondenceRuleResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        rule_id=rule_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    rule_id: int,
    *,
    client: AuthenticatedClient,
    body: FieldCorrespondenceReviewPayload,
) -> FieldCorrespondenceRuleResponse | HTTPValidationError | None:
    """Set Field Correspondence Review Status

     Mark an admin review decision without losing rule history.

    Args:
        rule_id (int):
        body (FieldCorrespondenceReviewPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        FieldCorrespondenceRuleResponse | HTTPValidationError
    """

    return sync_detailed(
        rule_id=rule_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    rule_id: int,
    *,
    client: AuthenticatedClient,
    body: FieldCorrespondenceReviewPayload,
) -> Response[FieldCorrespondenceRuleResponse | HTTPValidationError]:
    """Set Field Correspondence Review Status

     Mark an admin review decision without losing rule history.

    Args:
        rule_id (int):
        body (FieldCorrespondenceReviewPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[FieldCorrespondenceRuleResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        rule_id=rule_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    rule_id: int,
    *,
    client: AuthenticatedClient,
    body: FieldCorrespondenceReviewPayload,
) -> FieldCorrespondenceRuleResponse | HTTPValidationError | None:
    """Set Field Correspondence Review Status

     Mark an admin review decision without losing rule history.

    Args:
        rule_id (int):
        body (FieldCorrespondenceReviewPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        FieldCorrespondenceRuleResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            rule_id=rule_id,
            client=client,
            body=body,
        )
    ).parsed
