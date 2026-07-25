from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.field_correspondence_impact_response import FieldCorrespondenceImpactResponse
from ...models.field_correspondence_rule_payload import FieldCorrespondenceRulePayload
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    *,
    body: FieldCorrespondenceRulePayload,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/field-correspondence-rules/impact",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> FieldCorrespondenceImpactResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = FieldCorrespondenceImpactResponse.from_dict(response.json())

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
) -> Response[FieldCorrespondenceImpactResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: FieldCorrespondenceRulePayload,
) -> Response[FieldCorrespondenceImpactResponse | HTTPValidationError]:
    """Preview Field Correspondence Rule Impact

     Preview existing records and suggestions affected by a proposed rule.

    Args:
        body (FieldCorrespondenceRulePayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[FieldCorrespondenceImpactResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: FieldCorrespondenceRulePayload,
) -> FieldCorrespondenceImpactResponse | HTTPValidationError | None:
    """Preview Field Correspondence Rule Impact

     Preview existing records and suggestions affected by a proposed rule.

    Args:
        body (FieldCorrespondenceRulePayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        FieldCorrespondenceImpactResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: FieldCorrespondenceRulePayload,
) -> Response[FieldCorrespondenceImpactResponse | HTTPValidationError]:
    """Preview Field Correspondence Rule Impact

     Preview existing records and suggestions affected by a proposed rule.

    Args:
        body (FieldCorrespondenceRulePayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[FieldCorrespondenceImpactResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: FieldCorrespondenceRulePayload,
) -> FieldCorrespondenceImpactResponse | HTTPValidationError | None:
    """Preview Field Correspondence Rule Impact

     Preview existing records and suggestions affected by a proposed rule.

    Args:
        body (FieldCorrespondenceRulePayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        FieldCorrespondenceImpactResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
