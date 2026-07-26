from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.body_post_branding_favicon import BodyPostBrandingFavicon
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    *,
    body: BodyPostBrandingFavicon,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/branding/favicon",
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
    body: BodyPostBrandingFavicon,
) -> Response[Any | HTTPValidationError]:
    r"""Upload Favicon

     Upload a custom favicon.
    Accepts ICO, PNG, SVG up to 512 KB.
    Saves to static/favicon_<token>.<ext>, updates branding_settings.favicon_url.
    The frontend FaviconInjector component reads this URL and dynamically
    updates <link rel=\"icon\"> in the browser <head>.

    Args:
        body (BodyPostBrandingFavicon):

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
    body: BodyPostBrandingFavicon,
) -> Any | HTTPValidationError | None:
    r"""Upload Favicon

     Upload a custom favicon.
    Accepts ICO, PNG, SVG up to 512 KB.
    Saves to static/favicon_<token>.<ext>, updates branding_settings.favicon_url.
    The frontend FaviconInjector component reads this URL and dynamically
    updates <link rel=\"icon\"> in the browser <head>.

    Args:
        body (BodyPostBrandingFavicon):

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
    body: BodyPostBrandingFavicon,
) -> Response[Any | HTTPValidationError]:
    r"""Upload Favicon

     Upload a custom favicon.
    Accepts ICO, PNG, SVG up to 512 KB.
    Saves to static/favicon_<token>.<ext>, updates branding_settings.favicon_url.
    The frontend FaviconInjector component reads this URL and dynamically
    updates <link rel=\"icon\"> in the browser <head>.

    Args:
        body (BodyPostBrandingFavicon):

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
    body: BodyPostBrandingFavicon,
) -> Any | HTTPValidationError | None:
    r"""Upload Favicon

     Upload a custom favicon.
    Accepts ICO, PNG, SVG up to 512 KB.
    Saves to static/favicon_<token>.<ext>, updates branding_settings.favicon_url.
    The frontend FaviconInjector component reads this URL and dynamically
    updates <link rel=\"icon\"> in the browser <head>.

    Args:
        body (BodyPostBrandingFavicon):

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
