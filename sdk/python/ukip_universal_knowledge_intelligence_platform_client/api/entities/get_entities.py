from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.entity import Entity
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    search: str | Unset = UNSET,
    sort_by: str | Unset = "id",
    order: str | Unset = "asc",
    min_quality: float | Unset = UNSET,
    max_quality: float | Unset = UNSET,
    ft_entity_type: None | str | Unset = UNSET,
    ft_domain: None | str | Unset = UNSET,
    ft_validation_status: None | str | Unset = UNSET,
    ft_enrichment_status: None | str | Unset = UNSET,
    ft_source: None | str | Unset = UNSET,
    ft_work_type: None | str | Unset = UNSET,
    ft_journal_metric_signal: None | str | Unset = UNSET,
    concept: None | str | Unset = UNSET,
    language: None | str | Unset = UNSET,
    accept_language: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(accept_language, Unset):
        headers["accept-language"] = accept_language

    params: dict[str, Any] = {}

    params["skip"] = skip

    params["limit"] = limit

    params["search"] = search

    params["sort_by"] = sort_by

    params["order"] = order

    params["min_quality"] = min_quality

    params["max_quality"] = max_quality

    json_ft_entity_type: None | str | Unset
    if isinstance(ft_entity_type, Unset):
        json_ft_entity_type = UNSET
    else:
        json_ft_entity_type = ft_entity_type
    params["ft_entity_type"] = json_ft_entity_type

    json_ft_domain: None | str | Unset
    if isinstance(ft_domain, Unset):
        json_ft_domain = UNSET
    else:
        json_ft_domain = ft_domain
    params["ft_domain"] = json_ft_domain

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

    json_ft_work_type: None | str | Unset
    if isinstance(ft_work_type, Unset):
        json_ft_work_type = UNSET
    else:
        json_ft_work_type = ft_work_type
    params["ft_work_type"] = json_ft_work_type

    json_ft_journal_metric_signal: None | str | Unset
    if isinstance(ft_journal_metric_signal, Unset):
        json_ft_journal_metric_signal = UNSET
    else:
        json_ft_journal_metric_signal = ft_journal_metric_signal
    params["ft_journal_metric_signal"] = json_ft_journal_metric_signal

    json_concept: None | str | Unset
    if isinstance(concept, Unset):
        json_concept = UNSET
    else:
        json_concept = concept
    params["concept"] = json_concept

    json_language: None | str | Unset
    if isinstance(language, Unset):
        json_language = UNSET
    else:
        json_language = language
    params["language"] = json_language

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/entities",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | list[Entity] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Entity.from_dict(response_200_item_data)

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
) -> Response[HTTPValidationError | list[Entity]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    search: str | Unset = UNSET,
    sort_by: str | Unset = "id",
    order: str | Unset = "asc",
    min_quality: float | Unset = UNSET,
    max_quality: float | Unset = UNSET,
    ft_entity_type: None | str | Unset = UNSET,
    ft_domain: None | str | Unset = UNSET,
    ft_validation_status: None | str | Unset = UNSET,
    ft_enrichment_status: None | str | Unset = UNSET,
    ft_source: None | str | Unset = UNSET,
    ft_work_type: None | str | Unset = UNSET,
    ft_journal_metric_signal: None | str | Unset = UNSET,
    concept: None | str | Unset = UNSET,
    language: None | str | Unset = UNSET,
    accept_language: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | list[Entity]]:
    """Get Entities

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        search (str | Unset):
        sort_by (str | Unset):  Default: 'id'.
        order (str | Unset):  Default: 'asc'.
        min_quality (float | Unset):
        max_quality (float | Unset):
        ft_entity_type (None | str | Unset):
        ft_domain (None | str | Unset):
        ft_validation_status (None | str | Unset):
        ft_enrichment_status (None | str | Unset):
        ft_source (None | str | Unset):
        ft_work_type (None | str | Unset):
        ft_journal_metric_signal (None | str | Unset):
        concept (None | str | Unset):
        language (None | str | Unset): Language for catalog-sourced text (en, es). Falls back to
            Accept-Language, then English.
        accept_language (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[Entity]]
    """

    kwargs = _get_kwargs(
        skip=skip,
        limit=limit,
        search=search,
        sort_by=sort_by,
        order=order,
        min_quality=min_quality,
        max_quality=max_quality,
        ft_entity_type=ft_entity_type,
        ft_domain=ft_domain,
        ft_validation_status=ft_validation_status,
        ft_enrichment_status=ft_enrichment_status,
        ft_source=ft_source,
        ft_work_type=ft_work_type,
        ft_journal_metric_signal=ft_journal_metric_signal,
        concept=concept,
        language=language,
        accept_language=accept_language,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    search: str | Unset = UNSET,
    sort_by: str | Unset = "id",
    order: str | Unset = "asc",
    min_quality: float | Unset = UNSET,
    max_quality: float | Unset = UNSET,
    ft_entity_type: None | str | Unset = UNSET,
    ft_domain: None | str | Unset = UNSET,
    ft_validation_status: None | str | Unset = UNSET,
    ft_enrichment_status: None | str | Unset = UNSET,
    ft_source: None | str | Unset = UNSET,
    ft_work_type: None | str | Unset = UNSET,
    ft_journal_metric_signal: None | str | Unset = UNSET,
    concept: None | str | Unset = UNSET,
    language: None | str | Unset = UNSET,
    accept_language: None | str | Unset = UNSET,
) -> HTTPValidationError | list[Entity] | None:
    """Get Entities

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        search (str | Unset):
        sort_by (str | Unset):  Default: 'id'.
        order (str | Unset):  Default: 'asc'.
        min_quality (float | Unset):
        max_quality (float | Unset):
        ft_entity_type (None | str | Unset):
        ft_domain (None | str | Unset):
        ft_validation_status (None | str | Unset):
        ft_enrichment_status (None | str | Unset):
        ft_source (None | str | Unset):
        ft_work_type (None | str | Unset):
        ft_journal_metric_signal (None | str | Unset):
        concept (None | str | Unset):
        language (None | str | Unset): Language for catalog-sourced text (en, es). Falls back to
            Accept-Language, then English.
        accept_language (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[Entity]
    """

    return sync_detailed(
        client=client,
        skip=skip,
        limit=limit,
        search=search,
        sort_by=sort_by,
        order=order,
        min_quality=min_quality,
        max_quality=max_quality,
        ft_entity_type=ft_entity_type,
        ft_domain=ft_domain,
        ft_validation_status=ft_validation_status,
        ft_enrichment_status=ft_enrichment_status,
        ft_source=ft_source,
        ft_work_type=ft_work_type,
        ft_journal_metric_signal=ft_journal_metric_signal,
        concept=concept,
        language=language,
        accept_language=accept_language,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    search: str | Unset = UNSET,
    sort_by: str | Unset = "id",
    order: str | Unset = "asc",
    min_quality: float | Unset = UNSET,
    max_quality: float | Unset = UNSET,
    ft_entity_type: None | str | Unset = UNSET,
    ft_domain: None | str | Unset = UNSET,
    ft_validation_status: None | str | Unset = UNSET,
    ft_enrichment_status: None | str | Unset = UNSET,
    ft_source: None | str | Unset = UNSET,
    ft_work_type: None | str | Unset = UNSET,
    ft_journal_metric_signal: None | str | Unset = UNSET,
    concept: None | str | Unset = UNSET,
    language: None | str | Unset = UNSET,
    accept_language: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | list[Entity]]:
    """Get Entities

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        search (str | Unset):
        sort_by (str | Unset):  Default: 'id'.
        order (str | Unset):  Default: 'asc'.
        min_quality (float | Unset):
        max_quality (float | Unset):
        ft_entity_type (None | str | Unset):
        ft_domain (None | str | Unset):
        ft_validation_status (None | str | Unset):
        ft_enrichment_status (None | str | Unset):
        ft_source (None | str | Unset):
        ft_work_type (None | str | Unset):
        ft_journal_metric_signal (None | str | Unset):
        concept (None | str | Unset):
        language (None | str | Unset): Language for catalog-sourced text (en, es). Falls back to
            Accept-Language, then English.
        accept_language (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[Entity]]
    """

    kwargs = _get_kwargs(
        skip=skip,
        limit=limit,
        search=search,
        sort_by=sort_by,
        order=order,
        min_quality=min_quality,
        max_quality=max_quality,
        ft_entity_type=ft_entity_type,
        ft_domain=ft_domain,
        ft_validation_status=ft_validation_status,
        ft_enrichment_status=ft_enrichment_status,
        ft_source=ft_source,
        ft_work_type=ft_work_type,
        ft_journal_metric_signal=ft_journal_metric_signal,
        concept=concept,
        language=language,
        accept_language=accept_language,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    search: str | Unset = UNSET,
    sort_by: str | Unset = "id",
    order: str | Unset = "asc",
    min_quality: float | Unset = UNSET,
    max_quality: float | Unset = UNSET,
    ft_entity_type: None | str | Unset = UNSET,
    ft_domain: None | str | Unset = UNSET,
    ft_validation_status: None | str | Unset = UNSET,
    ft_enrichment_status: None | str | Unset = UNSET,
    ft_source: None | str | Unset = UNSET,
    ft_work_type: None | str | Unset = UNSET,
    ft_journal_metric_signal: None | str | Unset = UNSET,
    concept: None | str | Unset = UNSET,
    language: None | str | Unset = UNSET,
    accept_language: None | str | Unset = UNSET,
) -> HTTPValidationError | list[Entity] | None:
    """Get Entities

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        search (str | Unset):
        sort_by (str | Unset):  Default: 'id'.
        order (str | Unset):  Default: 'asc'.
        min_quality (float | Unset):
        max_quality (float | Unset):
        ft_entity_type (None | str | Unset):
        ft_domain (None | str | Unset):
        ft_validation_status (None | str | Unset):
        ft_enrichment_status (None | str | Unset):
        ft_source (None | str | Unset):
        ft_work_type (None | str | Unset):
        ft_journal_metric_signal (None | str | Unset):
        concept (None | str | Unset):
        language (None | str | Unset): Language for catalog-sourced text (en, es). Falls back to
            Accept-Language, then English.
        accept_language (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[Entity]
    """

    return (
        await asyncio_detailed(
            client=client,
            skip=skip,
            limit=limit,
            search=search,
            sort_by=sort_by,
            order=order,
            min_quality=min_quality,
            max_quality=max_quality,
            ft_entity_type=ft_entity_type,
            ft_domain=ft_domain,
            ft_validation_status=ft_validation_status,
            ft_enrichment_status=ft_enrichment_status,
            ft_source=ft_source,
            ft_work_type=ft_work_type,
            ft_journal_metric_signal=ft_journal_metric_signal,
            concept=concept,
            language=language,
            accept_language=accept_language,
        )
    ).parsed
