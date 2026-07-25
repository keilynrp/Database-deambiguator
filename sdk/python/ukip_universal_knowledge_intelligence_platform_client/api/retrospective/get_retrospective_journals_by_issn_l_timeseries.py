import datetime
from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    issn_l: str,
    *,
    since: datetime.datetime | None | Unset = UNSET,
    until: datetime.datetime | None | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_since: None | str | Unset
    if isinstance(since, Unset):
        json_since = UNSET
    elif isinstance(since, datetime.datetime):
        json_since = since.isoformat()
    else:
        json_since = since
    params["since"] = json_since

    json_until: None | str | Unset
    if isinstance(until, Unset):
        json_until = UNSET
    elif isinstance(until, datetime.datetime):
        json_until = until.isoformat()
    else:
        json_until = until
    params["until"] = json_until

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/retrospective/journals/{issn_l}/timeseries".format(
            issn_l=quote(str(issn_l), safe=""),
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
    issn_l: str,
    *,
    client: AuthenticatedClient,
    since: datetime.datetime | None | Unset = UNSET,
    until: datetime.datetime | None | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Journal Timeseries

     Ordered journal-metric snapshot history for one journal.

    Args:
        issn_l (str):
        since (datetime.datetime | None | Unset):
        until (datetime.datetime | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        issn_l=issn_l,
        since=since,
        until=until,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    issn_l: str,
    *,
    client: AuthenticatedClient,
    since: datetime.datetime | None | Unset = UNSET,
    until: datetime.datetime | None | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Journal Timeseries

     Ordered journal-metric snapshot history for one journal.

    Args:
        issn_l (str):
        since (datetime.datetime | None | Unset):
        until (datetime.datetime | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        issn_l=issn_l,
        client=client,
        since=since,
        until=until,
    ).parsed


async def asyncio_detailed(
    issn_l: str,
    *,
    client: AuthenticatedClient,
    since: datetime.datetime | None | Unset = UNSET,
    until: datetime.datetime | None | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Journal Timeseries

     Ordered journal-metric snapshot history for one journal.

    Args:
        issn_l (str):
        since (datetime.datetime | None | Unset):
        until (datetime.datetime | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        issn_l=issn_l,
        since=since,
        until=until,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    issn_l: str,
    *,
    client: AuthenticatedClient,
    since: datetime.datetime | None | Unset = UNSET,
    until: datetime.datetime | None | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Journal Timeseries

     Ordered journal-metric snapshot history for one journal.

    Args:
        issn_l (str):
        since (datetime.datetime | None | Unset):
        until (datetime.datetime | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            issn_l=issn_l,
            client=client,
            since=since,
            until=until,
        )
    ).parsed
