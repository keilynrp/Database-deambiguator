from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.journal_metric_response import JournalMetricResponse
from ...types import Response


def _get_kwargs(
    issn_l: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/journals/{issn_l}".format(
            issn_l=quote(str(issn_l), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | JournalMetricResponse | None:
    if response.status_code == 200:
        response_200 = JournalMetricResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | JournalMetricResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    issn_l: str,
    *,
    client: AuthenticatedClient,
) -> Response[HTTPValidationError | JournalMetricResponse]:
    """Get Journal

    Args:
        issn_l (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | JournalMetricResponse]
    """

    kwargs = _get_kwargs(
        issn_l=issn_l,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    issn_l: str,
    *,
    client: AuthenticatedClient,
) -> HTTPValidationError | JournalMetricResponse | None:
    """Get Journal

    Args:
        issn_l (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | JournalMetricResponse
    """

    return sync_detailed(
        issn_l=issn_l,
        client=client,
    ).parsed


async def asyncio_detailed(
    issn_l: str,
    *,
    client: AuthenticatedClient,
) -> Response[HTTPValidationError | JournalMetricResponse]:
    """Get Journal

    Args:
        issn_l (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | JournalMetricResponse]
    """

    kwargs = _get_kwargs(
        issn_l=issn_l,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    issn_l: str,
    *,
    client: AuthenticatedClient,
) -> HTTPValidationError | JournalMetricResponse | None:
    """Get Journal

    Args:
        issn_l (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | JournalMetricResponse
    """

    return (
        await asyncio_detailed(
            issn_l=issn_l,
            client=client,
        )
    ).parsed
