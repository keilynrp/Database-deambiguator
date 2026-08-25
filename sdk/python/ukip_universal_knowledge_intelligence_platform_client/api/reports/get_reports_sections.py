from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    language: None | str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_language: None | str | Unset
    if isinstance(language, Unset):
        json_language = UNSET
    else:
        json_language = language
    params["language"] = json_language

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/reports/sections",
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
    language: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """List Report Sections

     Return available report sections with per-format availability, so a caller
    can see before exporting which formats render each section (the omission
    header reports it after the fact).

    The label is resolved from the same `report.section.<id>` catalog key
    `assemble_report_document()` substitutes for every section title, so this
    endpoint and a generated report can never name a section differently
    (#268). Section `id` values and the `formats` shape are unchanged —
    `language` is additive and optional.

    Args:
        language (None | str | Unset): Language for the returned section labels (en, es). Omitted
            means English — existing callers are unaffected. Uses the same resolve_report_language()
            semantics as report generation, so this endpoint never consults Accept-Language either.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        language=language,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    language: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """List Report Sections

     Return available report sections with per-format availability, so a caller
    can see before exporting which formats render each section (the omission
    header reports it after the fact).

    The label is resolved from the same `report.section.<id>` catalog key
    `assemble_report_document()` substitutes for every section title, so this
    endpoint and a generated report can never name a section differently
    (#268). Section `id` values and the `formats` shape are unchanged —
    `language` is additive and optional.

    Args:
        language (None | str | Unset): Language for the returned section labels (en, es). Omitted
            means English — existing callers are unaffected. Uses the same resolve_report_language()
            semantics as report generation, so this endpoint never consults Accept-Language either.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        language=language,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    language: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """List Report Sections

     Return available report sections with per-format availability, so a caller
    can see before exporting which formats render each section (the omission
    header reports it after the fact).

    The label is resolved from the same `report.section.<id>` catalog key
    `assemble_report_document()` substitutes for every section title, so this
    endpoint and a generated report can never name a section differently
    (#268). Section `id` values and the `formats` shape are unchanged —
    `language` is additive and optional.

    Args:
        language (None | str | Unset): Language for the returned section labels (en, es). Omitted
            means English — existing callers are unaffected. Uses the same resolve_report_language()
            semantics as report generation, so this endpoint never consults Accept-Language either.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        language=language,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    language: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """List Report Sections

     Return available report sections with per-format availability, so a caller
    can see before exporting which formats render each section (the omission
    header reports it after the fact).

    The label is resolved from the same `report.section.<id>` catalog key
    `assemble_report_document()` substitutes for every section title, so this
    endpoint and a generated report can never name a section differently
    (#268). Section `id` values and the `formats` shape are unchanged —
    `language` is additive and optional.

    Args:
        language (None | str | Unset): Language for the returned section labels (en, es). Omitted
            means English — existing callers are unaffected. Uses the same resolve_report_language()
            semantics as report generation, so this endpoint never consults Accept-Language either.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            language=language,
        )
    ).parsed
