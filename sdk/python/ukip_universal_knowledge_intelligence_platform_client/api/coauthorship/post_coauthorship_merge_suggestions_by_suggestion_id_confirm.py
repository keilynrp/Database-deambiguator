from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.post_coauthorship_merge_suggestions_by_suggestion_id_confirm_response_post_coauthorship_merge_suggestions_by_suggestion_id_confirm import (
    PostCoauthorshipMergeSuggestionsBySuggestionIdConfirmResponsePostCoauthorshipMergeSuggestionsBySuggestionIdConfirm,
)
from ...types import Response


def _get_kwargs(
    suggestion_id: int,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/coauthorship/merge-suggestions/{suggestion_id}/confirm".format(
            suggestion_id=quote(str(suggestion_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    HTTPValidationError
    | PostCoauthorshipMergeSuggestionsBySuggestionIdConfirmResponsePostCoauthorshipMergeSuggestionsBySuggestionIdConfirm
    | None
):
    if response.status_code == 200:
        response_200 = PostCoauthorshipMergeSuggestionsBySuggestionIdConfirmResponsePostCoauthorshipMergeSuggestionsBySuggestionIdConfirm.from_dict(
            response.json()
        )

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
) -> Response[
    HTTPValidationError
    | PostCoauthorshipMergeSuggestionsBySuggestionIdConfirmResponsePostCoauthorshipMergeSuggestionsBySuggestionIdConfirm
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    suggestion_id: int,
    *,
    client: AuthenticatedClient,
) -> Response[
    HTTPValidationError
    | PostCoauthorshipMergeSuggestionsBySuggestionIdConfirmResponsePostCoauthorshipMergeSuggestionsBySuggestionIdConfirm
]:
    """Confirm Merge Suggestion

     Confirm an ambiguous pair as the same person: merge author_b into
    author_a (manual tier), repoint rows, write the audit, and enqueue the
    surviving author's scopes for recompute.

    Args:
        suggestion_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PostCoauthorshipMergeSuggestionsBySuggestionIdConfirmResponsePostCoauthorshipMergeSuggestionsBySuggestionIdConfirm]
    """

    kwargs = _get_kwargs(
        suggestion_id=suggestion_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    suggestion_id: int,
    *,
    client: AuthenticatedClient,
) -> (
    HTTPValidationError
    | PostCoauthorshipMergeSuggestionsBySuggestionIdConfirmResponsePostCoauthorshipMergeSuggestionsBySuggestionIdConfirm
    | None
):
    """Confirm Merge Suggestion

     Confirm an ambiguous pair as the same person: merge author_b into
    author_a (manual tier), repoint rows, write the audit, and enqueue the
    surviving author's scopes for recompute.

    Args:
        suggestion_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PostCoauthorshipMergeSuggestionsBySuggestionIdConfirmResponsePostCoauthorshipMergeSuggestionsBySuggestionIdConfirm
    """

    return sync_detailed(
        suggestion_id=suggestion_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    suggestion_id: int,
    *,
    client: AuthenticatedClient,
) -> Response[
    HTTPValidationError
    | PostCoauthorshipMergeSuggestionsBySuggestionIdConfirmResponsePostCoauthorshipMergeSuggestionsBySuggestionIdConfirm
]:
    """Confirm Merge Suggestion

     Confirm an ambiguous pair as the same person: merge author_b into
    author_a (manual tier), repoint rows, write the audit, and enqueue the
    surviving author's scopes for recompute.

    Args:
        suggestion_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PostCoauthorshipMergeSuggestionsBySuggestionIdConfirmResponsePostCoauthorshipMergeSuggestionsBySuggestionIdConfirm]
    """

    kwargs = _get_kwargs(
        suggestion_id=suggestion_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    suggestion_id: int,
    *,
    client: AuthenticatedClient,
) -> (
    HTTPValidationError
    | PostCoauthorshipMergeSuggestionsBySuggestionIdConfirmResponsePostCoauthorshipMergeSuggestionsBySuggestionIdConfirm
    | None
):
    """Confirm Merge Suggestion

     Confirm an ambiguous pair as the same person: merge author_b into
    author_a (manual tier), repoint rows, write the audit, and enqueue the
    surviving author's scopes for recompute.

    Args:
        suggestion_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PostCoauthorshipMergeSuggestionsBySuggestionIdConfirmResponsePostCoauthorshipMergeSuggestionsBySuggestionIdConfirm
    """

    return (
        await asyncio_detailed(
            suggestion_id=suggestion_id,
            client=client,
        )
    ).parsed
