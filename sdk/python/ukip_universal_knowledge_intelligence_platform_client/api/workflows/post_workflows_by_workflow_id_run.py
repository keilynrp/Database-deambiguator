from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.manual_run_request import ManualRunRequest
from ...types import Response


def _get_kwargs(
    workflow_id: int,
    *,
    body: ManualRunRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/workflows/{workflow_id}/run".format(
            workflow_id=quote(str(workflow_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | None:
    if response.status_code == 201:
        response_201 = response.json()
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
) -> Response[Any | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    workflow_id: int,
    *,
    client: AuthenticatedClient,
    body: ManualRunRequest,
) -> Response[Any | HTTPValidationError]:
    """Manual Run

     Manually trigger a workflow against a specific entity.

    Args:
        workflow_id (int):
        body (ManualRunRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        workflow_id=workflow_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    workflow_id: int,
    *,
    client: AuthenticatedClient,
    body: ManualRunRequest,
) -> Any | HTTPValidationError | None:
    """Manual Run

     Manually trigger a workflow against a specific entity.

    Args:
        workflow_id (int):
        body (ManualRunRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        workflow_id=workflow_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    workflow_id: int,
    *,
    client: AuthenticatedClient,
    body: ManualRunRequest,
) -> Response[Any | HTTPValidationError]:
    """Manual Run

     Manually trigger a workflow against a specific entity.

    Args:
        workflow_id (int):
        body (ManualRunRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        workflow_id=workflow_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workflow_id: int,
    *,
    client: AuthenticatedClient,
    body: ManualRunRequest,
) -> Any | HTTPValidationError | None:
    """Manual Run

     Manually trigger a workflow against a specific entity.

    Args:
        workflow_id (int):
        body (ManualRunRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            workflow_id=workflow_id,
            client=client,
            body=body,
        )
    ).parsed
