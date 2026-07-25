import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response


def _get_kwargs(
    *,
    event_type: str,
    since: datetime.datetime,
    until: datetime.datetime,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["event_type"] = event_type

    json_since = since.isoformat()
    params["since"] = json_since

    json_until = until.isoformat()
    params["until"] = json_until

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/retrospective/cohort",
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
    event_type: str,
    since: datetime.datetime,
    until: datetime.datetime,
) -> Response[Any | HTTPValidationError]:
    """Cohort

     Subjects whose first event of ``event_type`` occurred within [since, until].

    Args:
        event_type (str):
        since (datetime.datetime):
        until (datetime.datetime):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        event_type=event_type,
        since=since,
        until=until,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    event_type: str,
    since: datetime.datetime,
    until: datetime.datetime,
) -> Any | HTTPValidationError | None:
    """Cohort

     Subjects whose first event of ``event_type`` occurred within [since, until].

    Args:
        event_type (str):
        since (datetime.datetime):
        until (datetime.datetime):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        event_type=event_type,
        since=since,
        until=until,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    event_type: str,
    since: datetime.datetime,
    until: datetime.datetime,
) -> Response[Any | HTTPValidationError]:
    """Cohort

     Subjects whose first event of ``event_type`` occurred within [since, until].

    Args:
        event_type (str):
        since (datetime.datetime):
        until (datetime.datetime):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        event_type=event_type,
        since=since,
        until=until,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    event_type: str,
    since: datetime.datetime,
    until: datetime.datetime,
) -> Any | HTTPValidationError | None:
    """Cohort

     Subjects whose first event of ``event_type`` occurred within [since, until].

    Args:
        event_type (str):
        since (datetime.datetime):
        until (datetime.datetime):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            event_type=event_type,
            since=since,
            until=until,
        )
    ).parsed
