from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.bulk_suggestion_review_payload import BulkSuggestionReviewPayload
from ...models.bulk_suggestion_review_response import BulkSuggestionReviewResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    action: str,
    *,
    body: BulkSuggestionReviewPayload,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/mapping-suggestions/bulk/{action}".format(
            action=quote(str(action), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> BulkSuggestionReviewResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = BulkSuggestionReviewResponse.from_dict(response.json())

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
) -> Response[BulkSuggestionReviewResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    action: str,
    *,
    client: AuthenticatedClient,
    body: BulkSuggestionReviewPayload,
) -> Response[BulkSuggestionReviewResponse | HTTPValidationError]:
    """Bulk Review Mapping Suggestions

     Accept or reject multiple mapping suggestions in one review action.

    Args:
        action (str):
        body (BulkSuggestionReviewPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BulkSuggestionReviewResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        action=action,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    action: str,
    *,
    client: AuthenticatedClient,
    body: BulkSuggestionReviewPayload,
) -> BulkSuggestionReviewResponse | HTTPValidationError | None:
    """Bulk Review Mapping Suggestions

     Accept or reject multiple mapping suggestions in one review action.

    Args:
        action (str):
        body (BulkSuggestionReviewPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BulkSuggestionReviewResponse | HTTPValidationError
    """

    return sync_detailed(
        action=action,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    action: str,
    *,
    client: AuthenticatedClient,
    body: BulkSuggestionReviewPayload,
) -> Response[BulkSuggestionReviewResponse | HTTPValidationError]:
    """Bulk Review Mapping Suggestions

     Accept or reject multiple mapping suggestions in one review action.

    Args:
        action (str):
        body (BulkSuggestionReviewPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BulkSuggestionReviewResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        action=action,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    action: str,
    *,
    client: AuthenticatedClient,
    body: BulkSuggestionReviewPayload,
) -> BulkSuggestionReviewResponse | HTTPValidationError | None:
    """Bulk Review Mapping Suggestions

     Accept or reject multiple mapping suggestions in one review action.

    Args:
        action (str):
        body (BulkSuggestionReviewPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BulkSuggestionReviewResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            action=action,
            client=client,
            body=body,
        )
    ).parsed
