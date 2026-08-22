from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.catalog_portal_response import CatalogPortalResponse
from ...models.catalog_portal_update import CatalogPortalUpdate
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    slug: str,
    *,
    body: CatalogPortalUpdate,
    language: None | str | Unset = UNSET,
    accept_language: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(accept_language, Unset):
        headers["accept-language"] = accept_language

    params: dict[str, Any] = {}

    json_language: None | str | Unset
    if isinstance(language, Unset):
        json_language = UNSET
    else:
        json_language = language
    params["language"] = json_language

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/catalogs/{slug}".format(
            slug=quote(str(slug), safe=""),
        ),
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CatalogPortalResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = CatalogPortalResponse.from_dict(response.json())

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
) -> Response[CatalogPortalResponse | HTTPValidationError]:
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
    body: CatalogPortalUpdate,
    language: None | str | Unset = UNSET,
    accept_language: None | str | Unset = UNSET,
) -> Response[CatalogPortalResponse | HTTPValidationError]:
    """Update Catalog Portal

    Args:
        slug (str):
        language (None | str | Unset): Language for catalog-sourced text (en, es). Falls back to
            Accept-Language, then English.
        accept_language (None | str | Unset):
        body (CatalogPortalUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CatalogPortalResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        slug=slug,
        body=body,
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
    body: CatalogPortalUpdate,
    language: None | str | Unset = UNSET,
    accept_language: None | str | Unset = UNSET,
) -> CatalogPortalResponse | HTTPValidationError | None:
    """Update Catalog Portal

    Args:
        slug (str):
        language (None | str | Unset): Language for catalog-sourced text (en, es). Falls back to
            Accept-Language, then English.
        accept_language (None | str | Unset):
        body (CatalogPortalUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CatalogPortalResponse | HTTPValidationError
    """

    return sync_detailed(
        slug=slug,
        client=client,
        body=body,
        language=language,
        accept_language=accept_language,
    ).parsed


async def asyncio_detailed(
    slug: str,
    *,
    client: AuthenticatedClient,
    body: CatalogPortalUpdate,
    language: None | str | Unset = UNSET,
    accept_language: None | str | Unset = UNSET,
) -> Response[CatalogPortalResponse | HTTPValidationError]:
    """Update Catalog Portal

    Args:
        slug (str):
        language (None | str | Unset): Language for catalog-sourced text (en, es). Falls back to
            Accept-Language, then English.
        accept_language (None | str | Unset):
        body (CatalogPortalUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CatalogPortalResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        slug=slug,
        body=body,
        language=language,
        accept_language=accept_language,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    slug: str,
    *,
    client: AuthenticatedClient,
    body: CatalogPortalUpdate,
    language: None | str | Unset = UNSET,
    accept_language: None | str | Unset = UNSET,
) -> CatalogPortalResponse | HTTPValidationError | None:
    """Update Catalog Portal

    Args:
        slug (str):
        language (None | str | Unset): Language for catalog-sourced text (en, es). Falls back to
            Accept-Language, then English.
        accept_language (None | str | Unset):
        body (CatalogPortalUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CatalogPortalResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            slug=slug,
            client=client,
            body=body,
            language=language,
            accept_language=accept_language,
        )
    ).parsed
