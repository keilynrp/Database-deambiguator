from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.journal_metric_response import JournalMetricResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    sort_by: str | Unset = "nif",
    order: str | Unset = "desc",
    field: None | str | Unset = UNSET,
    metric_signal: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["sort_by"] = sort_by

    params["order"] = order

    json_field: None | str | Unset
    if isinstance(field, Unset):
        json_field = UNSET
    else:
        json_field = field
    params["field"] = json_field

    json_metric_signal: None | str | Unset
    if isinstance(metric_signal, Unset):
        json_metric_signal = UNSET
    else:
        json_metric_signal = metric_signal
    params["metric_signal"] = json_metric_signal

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/journals",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | list[JournalMetricResponse] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = JournalMetricResponse.from_dict(response_200_item_data)

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
) -> Response[HTTPValidationError | list[JournalMetricResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    sort_by: str | Unset = "nif",
    order: str | Unset = "desc",
    field: None | str | Unset = UNSET,
    metric_signal: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> Response[HTTPValidationError | list[JournalMetricResponse]]:
    """List Journals

    Args:
        sort_by (str | Unset):  Default: 'nif'.
        order (str | Unset):  Default: 'desc'.
        field (None | str | Unset):
        metric_signal (None | str | Unset):
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[JournalMetricResponse]]
    """

    kwargs = _get_kwargs(
        sort_by=sort_by,
        order=order,
        field=field,
        metric_signal=metric_signal,
        limit=limit,
        offset=offset,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    sort_by: str | Unset = "nif",
    order: str | Unset = "desc",
    field: None | str | Unset = UNSET,
    metric_signal: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> HTTPValidationError | list[JournalMetricResponse] | None:
    """List Journals

    Args:
        sort_by (str | Unset):  Default: 'nif'.
        order (str | Unset):  Default: 'desc'.
        field (None | str | Unset):
        metric_signal (None | str | Unset):
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[JournalMetricResponse]
    """

    return sync_detailed(
        client=client,
        sort_by=sort_by,
        order=order,
        field=field,
        metric_signal=metric_signal,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    sort_by: str | Unset = "nif",
    order: str | Unset = "desc",
    field: None | str | Unset = UNSET,
    metric_signal: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> Response[HTTPValidationError | list[JournalMetricResponse]]:
    """List Journals

    Args:
        sort_by (str | Unset):  Default: 'nif'.
        order (str | Unset):  Default: 'desc'.
        field (None | str | Unset):
        metric_signal (None | str | Unset):
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[JournalMetricResponse]]
    """

    kwargs = _get_kwargs(
        sort_by=sort_by,
        order=order,
        field=field,
        metric_signal=metric_signal,
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    sort_by: str | Unset = "nif",
    order: str | Unset = "desc",
    field: None | str | Unset = UNSET,
    metric_signal: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> HTTPValidationError | list[JournalMetricResponse] | None:
    """List Journals

    Args:
        sort_by (str | Unset):  Default: 'nif'.
        order (str | Unset):  Default: 'desc'.
        field (None | str | Unset):
        metric_signal (None | str | Unset):
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[JournalMetricResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            sort_by=sort_by,
            order=order,
            field=field,
            metric_signal=metric_signal,
            limit=limit,
            offset=offset,
        )
    ).parsed
