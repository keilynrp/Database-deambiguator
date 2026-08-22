from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    slug: str,
    *,
    skip: int | Unset = 0,
    limit: int | Unset = 24,
    search: None | str | Unset = UNSET,
    min_quality: float | None | Unset = UNSET,
    max_quality: float | None | Unset = UNSET,
    ft_entity_type: None | str | Unset = UNSET,
    ft_validation_status: None | str | Unset = UNSET,
    ft_enrichment_status: None | str | Unset = UNSET,
    ft_source: None | str | Unset = UNSET,
    ft_journal_metric_signal: None | str | Unset = UNSET,
    sort_by: None | str | Unset = UNSET,
    order: None | str | Unset = UNSET,
    language: None | str | Unset = UNSET,
    accept_language: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(accept_language, Unset):
        headers["accept-language"] = accept_language

    params: dict[str, Any] = {}

    params["skip"] = skip

    params["limit"] = limit

    json_search: None | str | Unset
    if isinstance(search, Unset):
        json_search = UNSET
    else:
        json_search = search
    params["search"] = json_search

    json_min_quality: float | None | Unset
    if isinstance(min_quality, Unset):
        json_min_quality = UNSET
    else:
        json_min_quality = min_quality
    params["min_quality"] = json_min_quality

    json_max_quality: float | None | Unset
    if isinstance(max_quality, Unset):
        json_max_quality = UNSET
    else:
        json_max_quality = max_quality
    params["max_quality"] = json_max_quality

    json_ft_entity_type: None | str | Unset
    if isinstance(ft_entity_type, Unset):
        json_ft_entity_type = UNSET
    else:
        json_ft_entity_type = ft_entity_type
    params["ft_entity_type"] = json_ft_entity_type

    json_ft_validation_status: None | str | Unset
    if isinstance(ft_validation_status, Unset):
        json_ft_validation_status = UNSET
    else:
        json_ft_validation_status = ft_validation_status
    params["ft_validation_status"] = json_ft_validation_status

    json_ft_enrichment_status: None | str | Unset
    if isinstance(ft_enrichment_status, Unset):
        json_ft_enrichment_status = UNSET
    else:
        json_ft_enrichment_status = ft_enrichment_status
    params["ft_enrichment_status"] = json_ft_enrichment_status

    json_ft_source: None | str | Unset
    if isinstance(ft_source, Unset):
        json_ft_source = UNSET
    else:
        json_ft_source = ft_source
    params["ft_source"] = json_ft_source

    json_ft_journal_metric_signal: None | str | Unset
    if isinstance(ft_journal_metric_signal, Unset):
        json_ft_journal_metric_signal = UNSET
    else:
        json_ft_journal_metric_signal = ft_journal_metric_signal
    params["ft_journal_metric_signal"] = json_ft_journal_metric_signal

    json_sort_by: None | str | Unset
    if isinstance(sort_by, Unset):
        json_sort_by = UNSET
    else:
        json_sort_by = sort_by
    params["sort_by"] = json_sort_by

    json_order: None | str | Unset
    if isinstance(order, Unset):
        json_order = UNSET
    else:
        json_order = order
    params["order"] = json_order

    json_language: None | str | Unset
    if isinstance(language, Unset):
        json_language = UNSET
    else:
        json_language = language
    params["language"] = json_language

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/catalogs/{slug}/results".format(
            slug=quote(str(slug), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
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
    slug: str,
    *,
    client: AuthenticatedClient,
    skip: int | Unset = 0,
    limit: int | Unset = 24,
    search: None | str | Unset = UNSET,
    min_quality: float | None | Unset = UNSET,
    max_quality: float | None | Unset = UNSET,
    ft_entity_type: None | str | Unset = UNSET,
    ft_validation_status: None | str | Unset = UNSET,
    ft_enrichment_status: None | str | Unset = UNSET,
    ft_source: None | str | Unset = UNSET,
    ft_journal_metric_signal: None | str | Unset = UNSET,
    sort_by: None | str | Unset = UNSET,
    order: None | str | Unset = UNSET,
    language: None | str | Unset = UNSET,
    accept_language: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Get Catalog Results

    Args:
        slug (str):
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 24.
        search (None | str | Unset):
        min_quality (float | None | Unset):
        max_quality (float | None | Unset):
        ft_entity_type (None | str | Unset):
        ft_validation_status (None | str | Unset):
        ft_enrichment_status (None | str | Unset):
        ft_source (None | str | Unset):
        ft_journal_metric_signal (None | str | Unset):
        sort_by (None | str | Unset):
        order (None | str | Unset):
        language (None | str | Unset): Language for catalog-sourced text (en, es). Falls back to
            Accept-Language, then English.
        accept_language (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        slug=slug,
        skip=skip,
        limit=limit,
        search=search,
        min_quality=min_quality,
        max_quality=max_quality,
        ft_entity_type=ft_entity_type,
        ft_validation_status=ft_validation_status,
        ft_enrichment_status=ft_enrichment_status,
        ft_source=ft_source,
        ft_journal_metric_signal=ft_journal_metric_signal,
        sort_by=sort_by,
        order=order,
        language=language,
        accept_language=accept_language,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    slug: str,
    *,
    client: AuthenticatedClient,
    skip: int | Unset = 0,
    limit: int | Unset = 24,
    search: None | str | Unset = UNSET,
    min_quality: float | None | Unset = UNSET,
    max_quality: float | None | Unset = UNSET,
    ft_entity_type: None | str | Unset = UNSET,
    ft_validation_status: None | str | Unset = UNSET,
    ft_enrichment_status: None | str | Unset = UNSET,
    ft_source: None | str | Unset = UNSET,
    ft_journal_metric_signal: None | str | Unset = UNSET,
    sort_by: None | str | Unset = UNSET,
    order: None | str | Unset = UNSET,
    language: None | str | Unset = UNSET,
    accept_language: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Get Catalog Results

    Args:
        slug (str):
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 24.
        search (None | str | Unset):
        min_quality (float | None | Unset):
        max_quality (float | None | Unset):
        ft_entity_type (None | str | Unset):
        ft_validation_status (None | str | Unset):
        ft_enrichment_status (None | str | Unset):
        ft_source (None | str | Unset):
        ft_journal_metric_signal (None | str | Unset):
        sort_by (None | str | Unset):
        order (None | str | Unset):
        language (None | str | Unset): Language for catalog-sourced text (en, es). Falls back to
            Accept-Language, then English.
        accept_language (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        slug=slug,
        client=client,
        skip=skip,
        limit=limit,
        search=search,
        min_quality=min_quality,
        max_quality=max_quality,
        ft_entity_type=ft_entity_type,
        ft_validation_status=ft_validation_status,
        ft_enrichment_status=ft_enrichment_status,
        ft_source=ft_source,
        ft_journal_metric_signal=ft_journal_metric_signal,
        sort_by=sort_by,
        order=order,
        language=language,
        accept_language=accept_language,
    ).parsed


async def asyncio_detailed(
    slug: str,
    *,
    client: AuthenticatedClient,
    skip: int | Unset = 0,
    limit: int | Unset = 24,
    search: None | str | Unset = UNSET,
    min_quality: float | None | Unset = UNSET,
    max_quality: float | None | Unset = UNSET,
    ft_entity_type: None | str | Unset = UNSET,
    ft_validation_status: None | str | Unset = UNSET,
    ft_enrichment_status: None | str | Unset = UNSET,
    ft_source: None | str | Unset = UNSET,
    ft_journal_metric_signal: None | str | Unset = UNSET,
    sort_by: None | str | Unset = UNSET,
    order: None | str | Unset = UNSET,
    language: None | str | Unset = UNSET,
    accept_language: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Get Catalog Results

    Args:
        slug (str):
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 24.
        search (None | str | Unset):
        min_quality (float | None | Unset):
        max_quality (float | None | Unset):
        ft_entity_type (None | str | Unset):
        ft_validation_status (None | str | Unset):
        ft_enrichment_status (None | str | Unset):
        ft_source (None | str | Unset):
        ft_journal_metric_signal (None | str | Unset):
        sort_by (None | str | Unset):
        order (None | str | Unset):
        language (None | str | Unset): Language for catalog-sourced text (en, es). Falls back to
            Accept-Language, then English.
        accept_language (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        slug=slug,
        skip=skip,
        limit=limit,
        search=search,
        min_quality=min_quality,
        max_quality=max_quality,
        ft_entity_type=ft_entity_type,
        ft_validation_status=ft_validation_status,
        ft_enrichment_status=ft_enrichment_status,
        ft_source=ft_source,
        ft_journal_metric_signal=ft_journal_metric_signal,
        sort_by=sort_by,
        order=order,
        language=language,
        accept_language=accept_language,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    slug: str,
    *,
    client: AuthenticatedClient,
    skip: int | Unset = 0,
    limit: int | Unset = 24,
    search: None | str | Unset = UNSET,
    min_quality: float | None | Unset = UNSET,
    max_quality: float | None | Unset = UNSET,
    ft_entity_type: None | str | Unset = UNSET,
    ft_validation_status: None | str | Unset = UNSET,
    ft_enrichment_status: None | str | Unset = UNSET,
    ft_source: None | str | Unset = UNSET,
    ft_journal_metric_signal: None | str | Unset = UNSET,
    sort_by: None | str | Unset = UNSET,
    order: None | str | Unset = UNSET,
    language: None | str | Unset = UNSET,
    accept_language: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Get Catalog Results

    Args:
        slug (str):
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 24.
        search (None | str | Unset):
        min_quality (float | None | Unset):
        max_quality (float | None | Unset):
        ft_entity_type (None | str | Unset):
        ft_validation_status (None | str | Unset):
        ft_enrichment_status (None | str | Unset):
        ft_source (None | str | Unset):
        ft_journal_metric_signal (None | str | Unset):
        sort_by (None | str | Unset):
        order (None | str | Unset):
        language (None | str | Unset): Language for catalog-sourced text (en, es). Falls back to
            Accept-Language, then English.
        accept_language (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            slug=slug,
            client=client,
            skip=skip,
            limit=limit,
            search=search,
            min_quality=min_quality,
            max_quality=max_quality,
            ft_entity_type=ft_entity_type,
            ft_validation_status=ft_validation_status,
            ft_enrichment_status=ft_enrichment_status,
            ft_source=ft_source,
            ft_journal_metric_signal=ft_journal_metric_signal,
            sort_by=sort_by,
            order=order,
            language=language,
            accept_language=accept_language,
        )
    ).parsed
