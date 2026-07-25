from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.body_post_branding_logo import BodyPostBrandingLogo
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    *,
    body: BodyPostBrandingLogo,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/branding/logo",
    }

    _kwargs["files"] = body.to_multipart()

    headers["Content-Type"] = "multipart/form-data; boundary=+++"

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
    *,
    client: AuthenticatedClient,
    body: BodyPostBrandingLogo,
) -> Response[Any | HTTPValidationError]:
    """Upload Logo

     Sprint 76 — Upload a logo image via drag & drop.
    Accepts PNG, JPG, SVG, WebP, GIF up to 2 MB.
    Saves to static/logo.<ext>, updates branding_settings.logo_url,
    and returns the public URL path.

    Args:
        body (BodyPostBrandingLogo):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: BodyPostBrandingLogo,
) -> Any | HTTPValidationError | None:
    """Upload Logo

     Sprint 76 — Upload a logo image via drag & drop.
    Accepts PNG, JPG, SVG, WebP, GIF up to 2 MB.
    Saves to static/logo.<ext>, updates branding_settings.logo_url,
    and returns the public URL path.

    Args:
        body (BodyPostBrandingLogo):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: BodyPostBrandingLogo,
) -> Response[Any | HTTPValidationError]:
    """Upload Logo

     Sprint 76 — Upload a logo image via drag & drop.
    Accepts PNG, JPG, SVG, WebP, GIF up to 2 MB.
    Saves to static/logo.<ext>, updates branding_settings.logo_url,
    and returns the public URL path.

    Args:
        body (BodyPostBrandingLogo):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: BodyPostBrandingLogo,
) -> Any | HTTPValidationError | None:
    """Upload Logo

     Sprint 76 — Upload a logo image via drag & drop.
    Accepts PNG, JPG, SVG, WebP, GIF up to 2 MB.
    Saves to static/logo.<ext>, updates branding_settings.logo_url,
    and returns the public URL path.

    Args:
        body (BodyPostBrandingLogo):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
