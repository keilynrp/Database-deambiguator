from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    fields: str
    | Unset = "entity_type,domain,validation_status,enrichment_status,source,work_type,journal_metric_signal",
    search: None | str | Unset = UNSET,
    min_quality: float | None | Unset = UNSET,
    max_quality: float | None | Unset = UNSET,
    ft_entity_type: None | str | Unset = UNSET,
    ft_domain: None | str | Unset = UNSET,
    ft_validation_status: None | str | Unset = UNSET,
    ft_enrichment_status: None | str | Unset = UNSET,
    ft_source: None | str | Unset = UNSET,
    ft_work_type: None | str | Unset = UNSET,
    ft_journal_metric_signal: None | str | Unset = UNSET,
    concept: None | str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["fields"] = fields

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

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/entities/facets",
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
    fields: str
    | Unset = "entity_type,domain,validation_status,enrichment_status,source,work_type,journal_metric_signal",
    search: None | str | Unset = UNSET,
    min_quality: float | None | Unset = UNSET,
    max_quality: float | None | Unset = UNSET,
    ft_entity_type: None | str | Unset = UNSET,
    ft_domain: None | str | Unset = UNSET,
    ft_validation_status: None | str | Unset = UNSET,
    ft_enrichment_status: None | str | Unset = UNSET,
    ft_source: None | str | Unset = UNSET,
    ft_work_type: None | str | Unset = UNSET,
    ft_journal_metric_signal: None | str | Unset = UNSET,
    concept: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Get Entity Facets

     Returns value counts for the requested facet fields.
    Response: { field: [{value, count}, ...], ... }
    Unknown fields are silently ignored.

    Args:
        fields (str | Unset):  Default: 'entity_type,domain,validation_status,enrichment_status,so
            urce,work_type,journal_metric_signal'.
        search (None | str | Unset):
        min_quality (float | None | Unset):
        max_quality (float | None | Unset):
        ft_entity_type (None | str | Unset):
        ft_domain (None | str | Unset):
        ft_validation_status (None | str | Unset):
        ft_enrichment_status (None | str | Unset):
        ft_source (None | str | Unset):
        ft_work_type (None | str | Unset):
        ft_journal_metric_signal (None | str | Unset):
        concept (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        fields=fields,
        search=search,
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
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    fields: str
    | Unset = "entity_type,domain,validation_status,enrichment_status,source,work_type,journal_metric_signal",
    search: None | str | Unset = UNSET,
    min_quality: float | None | Unset = UNSET,
    max_quality: float | None | Unset = UNSET,
    ft_entity_type: None | str | Unset = UNSET,
    ft_domain: None | str | Unset = UNSET,
    ft_validation_status: None | str | Unset = UNSET,
    ft_enrichment_status: None | str | Unset = UNSET,
    ft_source: None | str | Unset = UNSET,
    ft_work_type: None | str | Unset = UNSET,
    ft_journal_metric_signal: None | str | Unset = UNSET,
    concept: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Get Entity Facets

     Returns value counts for the requested facet fields.
    Response: { field: [{value, count}, ...], ... }
    Unknown fields are silently ignored.

    Args:
        fields (str | Unset):  Default: 'entity_type,domain,validation_status,enrichment_status,so
            urce,work_type,journal_metric_signal'.
        search (None | str | Unset):
        min_quality (float | None | Unset):
        max_quality (float | None | Unset):
        ft_entity_type (None | str | Unset):
        ft_domain (None | str | Unset):
        ft_validation_status (None | str | Unset):
        ft_enrichment_status (None | str | Unset):
        ft_source (None | str | Unset):
        ft_work_type (None | str | Unset):
        ft_journal_metric_signal (None | str | Unset):
        concept (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        fields=fields,
        search=search,
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
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    fields: str
    | Unset = "entity_type,domain,validation_status,enrichment_status,source,work_type,journal_metric_signal",
    search: None | str | Unset = UNSET,
    min_quality: float | None | Unset = UNSET,
    max_quality: float | None | Unset = UNSET,
    ft_entity_type: None | str | Unset = UNSET,
    ft_domain: None | str | Unset = UNSET,
    ft_validation_status: None | str | Unset = UNSET,
    ft_enrichment_status: None | str | Unset = UNSET,
    ft_source: None | str | Unset = UNSET,
    ft_work_type: None | str | Unset = UNSET,
    ft_journal_metric_signal: None | str | Unset = UNSET,
    concept: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Get Entity Facets

     Returns value counts for the requested facet fields.
    Response: { field: [{value, count}, ...], ... }
    Unknown fields are silently ignored.

    Args:
        fields (str | Unset):  Default: 'entity_type,domain,validation_status,enrichment_status,so
            urce,work_type,journal_metric_signal'.
        search (None | str | Unset):
        min_quality (float | None | Unset):
        max_quality (float | None | Unset):
        ft_entity_type (None | str | Unset):
        ft_domain (None | str | Unset):
        ft_validation_status (None | str | Unset):
        ft_enrichment_status (None | str | Unset):
        ft_source (None | str | Unset):
        ft_work_type (None | str | Unset):
        ft_journal_metric_signal (None | str | Unset):
        concept (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        fields=fields,
        search=search,
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
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    fields: str
    | Unset = "entity_type,domain,validation_status,enrichment_status,source,work_type,journal_metric_signal",
    search: None | str | Unset = UNSET,
    min_quality: float | None | Unset = UNSET,
    max_quality: float | None | Unset = UNSET,
    ft_entity_type: None | str | Unset = UNSET,
    ft_domain: None | str | Unset = UNSET,
    ft_validation_status: None | str | Unset = UNSET,
    ft_enrichment_status: None | str | Unset = UNSET,
    ft_source: None | str | Unset = UNSET,
    ft_work_type: None | str | Unset = UNSET,
    ft_journal_metric_signal: None | str | Unset = UNSET,
    concept: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Get Entity Facets

     Returns value counts for the requested facet fields.
    Response: { field: [{value, count}, ...], ... }
    Unknown fields are silently ignored.

    Args:
        fields (str | Unset):  Default: 'entity_type,domain,validation_status,enrichment_status,so
            urce,work_type,journal_metric_signal'.
        search (None | str | Unset):
        min_quality (float | None | Unset):
        max_quality (float | None | Unset):
        ft_entity_type (None | str | Unset):
        ft_domain (None | str | Unset):
        ft_validation_status (None | str | Unset):
        ft_enrichment_status (None | str | Unset):
        ft_source (None | str | Unset):
        ft_work_type (None | str | Unset):
        ft_journal_metric_signal (None | str | Unset):
        concept (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            fields=fields,
            search=search,
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
        )
    ).parsed
