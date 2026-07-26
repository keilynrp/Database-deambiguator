from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    view: str,
    *,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    order_by: None | str | Unset = UNSET,
    order: str | Unset = "desc",
    issn_l: None | str | Unset = UNSET,
    field: None | str | Unset = UNSET,
    year_min: int | None | Unset = UNSET,
    year_max: int | None | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    json_order_by: None | str | Unset
    if isinstance(order_by, Unset):
        json_order_by = UNSET
    else:
        json_order_by = order_by
    params["order_by"] = json_order_by

    params["order"] = order

    json_issn_l: None | str | Unset
    if isinstance(issn_l, Unset):
        json_issn_l = UNSET
    else:
        json_issn_l = issn_l
    params["issn_l"] = json_issn_l

    json_field: None | str | Unset
    if isinstance(field, Unset):
        json_field = UNSET
    else:
        json_field = field
    params["field"] = json_field

    json_year_min: int | None | Unset
    if isinstance(year_min, Unset):
        json_year_min = UNSET
    else:
        json_year_min = year_min
    params["year_min"] = json_year_min

    json_year_max: int | None | Unset
    if isinstance(year_max, Unset):
        json_year_max = UNSET
    else:
        json_year_max = year_max
    params["year_max"] = json_year_max

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/openalex-lake/query/{view}".format(
            view=quote(str(view), safe=""),
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
    view: str,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    order_by: None | str | Unset = UNSET,
    order: str | Unset = "desc",
    issn_l: None | str | Unset = UNSET,
    field: None | str | Unset = UNSET,
    year_min: int | None | Unset = UNSET,
    year_max: int | None | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    r"""Query Openalex Lake View

     Bounded, parameterized read of one whitelisted analysis view.

    Filters apply only where the view has the column (harmless elsewhere).
    Friendly non-error states mirror /status: {\"lake\": \"not_initialized\"} and
    {\"lake\": \"locked\"} come back as 200 so the UI renders them as states.

    Args:
        view (str):
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.
        order_by (None | str | Unset):
        order (str | Unset):  Default: 'desc'.
        issn_l (None | str | Unset):
        field (None | str | Unset):
        year_min (int | None | Unset):
        year_max (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        view=view,
        limit=limit,
        offset=offset,
        order_by=order_by,
        order=order,
        issn_l=issn_l,
        field=field,
        year_min=year_min,
        year_max=year_max,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    view: str,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    order_by: None | str | Unset = UNSET,
    order: str | Unset = "desc",
    issn_l: None | str | Unset = UNSET,
    field: None | str | Unset = UNSET,
    year_min: int | None | Unset = UNSET,
    year_max: int | None | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    r"""Query Openalex Lake View

     Bounded, parameterized read of one whitelisted analysis view.

    Filters apply only where the view has the column (harmless elsewhere).
    Friendly non-error states mirror /status: {\"lake\": \"not_initialized\"} and
    {\"lake\": \"locked\"} come back as 200 so the UI renders them as states.

    Args:
        view (str):
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.
        order_by (None | str | Unset):
        order (str | Unset):  Default: 'desc'.
        issn_l (None | str | Unset):
        field (None | str | Unset):
        year_min (int | None | Unset):
        year_max (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        view=view,
        client=client,
        limit=limit,
        offset=offset,
        order_by=order_by,
        order=order,
        issn_l=issn_l,
        field=field,
        year_min=year_min,
        year_max=year_max,
    ).parsed


async def asyncio_detailed(
    view: str,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    order_by: None | str | Unset = UNSET,
    order: str | Unset = "desc",
    issn_l: None | str | Unset = UNSET,
    field: None | str | Unset = UNSET,
    year_min: int | None | Unset = UNSET,
    year_max: int | None | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    r"""Query Openalex Lake View

     Bounded, parameterized read of one whitelisted analysis view.

    Filters apply only where the view has the column (harmless elsewhere).
    Friendly non-error states mirror /status: {\"lake\": \"not_initialized\"} and
    {\"lake\": \"locked\"} come back as 200 so the UI renders them as states.

    Args:
        view (str):
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.
        order_by (None | str | Unset):
        order (str | Unset):  Default: 'desc'.
        issn_l (None | str | Unset):
        field (None | str | Unset):
        year_min (int | None | Unset):
        year_max (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        view=view,
        limit=limit,
        offset=offset,
        order_by=order_by,
        order=order,
        issn_l=issn_l,
        field=field,
        year_min=year_min,
        year_max=year_max,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    view: str,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    order_by: None | str | Unset = UNSET,
    order: str | Unset = "desc",
    issn_l: None | str | Unset = UNSET,
    field: None | str | Unset = UNSET,
    year_min: int | None | Unset = UNSET,
    year_max: int | None | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    r"""Query Openalex Lake View

     Bounded, parameterized read of one whitelisted analysis view.

    Filters apply only where the view has the column (harmless elsewhere).
    Friendly non-error states mirror /status: {\"lake\": \"not_initialized\"} and
    {\"lake\": \"locked\"} come back as 200 so the UI renders them as states.

    Args:
        view (str):
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.
        order_by (None | str | Unset):
        order (str | Unset):  Default: 'desc'.
        issn_l (None | str | Unset):
        field (None | str | Unset):
        year_min (int | None | Unset):
        year_max (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            view=view,
            client=client,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order=order,
            issn_l=issn_l,
            field=field,
            year_min=year_min,
            year_max=year_max,
        )
    ).parsed
