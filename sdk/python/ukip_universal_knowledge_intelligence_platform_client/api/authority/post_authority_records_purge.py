from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    field_name: None | str | Unset = UNSET,
    status: str | Unset = "pending",
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_field_name: None | str | Unset
    if isinstance(field_name, Unset):
        json_field_name = UNSET
    else:
        json_field_name = field_name
    params["field_name"] = json_field_name

    params["status"] = status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/authority/records/purge",
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
    field_name: None | str | Unset = UNSET,
    status: str | Unset = "pending",
) -> Response[Any | HTTPValidationError]:
    """Purge Authority Records

     Bulk-delete unreviewed records so they can be re-resolved (e.g. after
    enabling orcid_hint). Only ``pending``/``rejected`` are ever deletable —
    ``confirmed`` records are never touched. Optionally scoped to ``field_name``.

    Args:
        field_name (None | str | Unset):
        status (str | Unset):  Default: 'pending'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        field_name=field_name,
        status=status,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    field_name: None | str | Unset = UNSET,
    status: str | Unset = "pending",
) -> Any | HTTPValidationError | None:
    """Purge Authority Records

     Bulk-delete unreviewed records so they can be re-resolved (e.g. after
    enabling orcid_hint). Only ``pending``/``rejected`` are ever deletable —
    ``confirmed`` records are never touched. Optionally scoped to ``field_name``.

    Args:
        field_name (None | str | Unset):
        status (str | Unset):  Default: 'pending'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        field_name=field_name,
        status=status,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    field_name: None | str | Unset = UNSET,
    status: str | Unset = "pending",
) -> Response[Any | HTTPValidationError]:
    """Purge Authority Records

     Bulk-delete unreviewed records so they can be re-resolved (e.g. after
    enabling orcid_hint). Only ``pending``/``rejected`` are ever deletable —
    ``confirmed`` records are never touched. Optionally scoped to ``field_name``.

    Args:
        field_name (None | str | Unset):
        status (str | Unset):  Default: 'pending'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        field_name=field_name,
        status=status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    field_name: None | str | Unset = UNSET,
    status: str | Unset = "pending",
) -> Any | HTTPValidationError | None:
    """Purge Authority Records

     Bulk-delete unreviewed records so they can be re-resolved (e.g. after
    enabling orcid_hint). Only ``pending``/``rejected`` are ever deletable —
    ``confirmed`` records are never touched. Optionally scoped to ``field_name``.

    Args:
        field_name (None | str | Unset):
        status (str | Unset):  Default: 'pending'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            field_name=field_name,
            status=status,
        )
    ).parsed
