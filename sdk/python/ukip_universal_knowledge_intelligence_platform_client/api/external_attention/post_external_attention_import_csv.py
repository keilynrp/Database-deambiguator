from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.body_post_external_attention_import_csv import BodyPostExternalAttentionImportCsv
from ...models.bulk_import_response import BulkImportResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    *,
    body: BodyPostExternalAttentionImportCsv,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/external-attention/import/csv",
    }

    _kwargs["files"] = body.to_multipart()

    headers["Content-Type"] = "multipart/form-data; boundary=+++"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> BulkImportResponse | HTTPValidationError | None:
    if response.status_code == 201:
        response_201 = BulkImportResponse.from_dict(response.json())

        return response_201

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[BulkImportResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: BodyPostExternalAttentionImportCsv,
) -> Response[BulkImportResponse | HTTPValidationError]:
    """Bulk Import Observations Csv

     Import external attention observations from a CSV file.

    Expected columns: entity_id, source_type, mention_count, last_seen_at, title, url, snippet
    Only entity_id and source_type are required.

    Args:
        body (BodyPostExternalAttentionImportCsv):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BulkImportResponse | HTTPValidationError]
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
    body: BodyPostExternalAttentionImportCsv,
) -> BulkImportResponse | HTTPValidationError | None:
    """Bulk Import Observations Csv

     Import external attention observations from a CSV file.

    Expected columns: entity_id, source_type, mention_count, last_seen_at, title, url, snippet
    Only entity_id and source_type are required.

    Args:
        body (BodyPostExternalAttentionImportCsv):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BulkImportResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: BodyPostExternalAttentionImportCsv,
) -> Response[BulkImportResponse | HTTPValidationError]:
    """Bulk Import Observations Csv

     Import external attention observations from a CSV file.

    Expected columns: entity_id, source_type, mention_count, last_seen_at, title, url, snippet
    Only entity_id and source_type are required.

    Args:
        body (BodyPostExternalAttentionImportCsv):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BulkImportResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: BodyPostExternalAttentionImportCsv,
) -> BulkImportResponse | HTTPValidationError | None:
    """Bulk Import Observations Csv

     Import external attention observations from a CSV file.

    Expected columns: entity_id, source_type, mention_count, last_seen_at, title, url, snippet
    Only entity_id and source_type are required.

    Args:
        body (BodyPostExternalAttentionImportCsv):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BulkImportResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
