from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_coauthorship_merge_suggestions_generate_response_post_coauthorship_merge_suggestions_generate import (
    PostCoauthorshipMergeSuggestionsGenerateResponsePostCoauthorshipMergeSuggestionsGenerate,
)
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/coauthorship/merge-suggestions/generate",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PostCoauthorshipMergeSuggestionsGenerateResponsePostCoauthorshipMergeSuggestionsGenerate | None:
    if response.status_code == 200:
        response_200 = (
            PostCoauthorshipMergeSuggestionsGenerateResponsePostCoauthorshipMergeSuggestionsGenerate.from_dict(
                response.json()
            )
        )

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PostCoauthorshipMergeSuggestionsGenerateResponsePostCoauthorshipMergeSuggestionsGenerate]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[PostCoauthorshipMergeSuggestionsGenerateResponsePostCoauthorshipMergeSuggestionsGenerate]:
    """Generate Merge Suggestions Endpoint

     Scan authors and enqueue ambiguous (last+initial) pairs for review.
    Idempotent — safe to re-run; existing pairs are skipped.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostCoauthorshipMergeSuggestionsGenerateResponsePostCoauthorshipMergeSuggestionsGenerate]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> PostCoauthorshipMergeSuggestionsGenerateResponsePostCoauthorshipMergeSuggestionsGenerate | None:
    """Generate Merge Suggestions Endpoint

     Scan authors and enqueue ambiguous (last+initial) pairs for review.
    Idempotent — safe to re-run; existing pairs are skipped.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostCoauthorshipMergeSuggestionsGenerateResponsePostCoauthorshipMergeSuggestionsGenerate
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[PostCoauthorshipMergeSuggestionsGenerateResponsePostCoauthorshipMergeSuggestionsGenerate]:
    """Generate Merge Suggestions Endpoint

     Scan authors and enqueue ambiguous (last+initial) pairs for review.
    Idempotent — safe to re-run; existing pairs are skipped.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostCoauthorshipMergeSuggestionsGenerateResponsePostCoauthorshipMergeSuggestionsGenerate]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> PostCoauthorshipMergeSuggestionsGenerateResponsePostCoauthorshipMergeSuggestionsGenerate | None:
    """Generate Merge Suggestions Endpoint

     Scan authors and enqueue ambiguous (last+initial) pairs for review.
    Idempotent — safe to re-run; existing pairs are skipped.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostCoauthorshipMergeSuggestionsGenerateResponsePostCoauthorshipMergeSuggestionsGenerate
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
