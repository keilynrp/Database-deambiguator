"""A client library for accessing UKIP — Universal Knowledge Intelligence Platform"""

from .client import AuthenticatedClient, Client

__all__ = (
    "AuthenticatedClient",
    "Client",
)
