from __future__ import annotations

import base64
import functools
from typing import TYPE_CHECKING, Callable
from urllib.parse import unquote

if TYPE_CHECKING:
    from django.http import HttpRequest


def extract_header(request: HttpRequest, header_name: str) -> str:
    """Extract a header from a request object or raise a ValueError when it is not found"""
    try:
        return request.headers[header_name]
    except Exception as exc:
        raise ValueError(f'Unable to find "{header_name}" header in request') from exc


def extract_generic_token(request: HttpRequest, header_name: str, auth_type: str) -> str:
    """
    Extract a generic token from a request object and raise a ValueError when it is not found

    :param request: HTTP request containing the headers
    :param header_name: Header to lookup for authentication data (ex: Authorization)
    :param auth_type: Type of authentication information to extract (ex: Bearer, Basic, etc.)
    :return: Authentication data
    """
    auth_header = extract_header(request, header_name)
    current_auth_type, credentials = auth_header.split()

    if current_auth_type.lower() != auth_type.lower():
        raise ValueError(f'Invalid authentication type. Expected "{auth_type}", found "{current_auth_type}"')

    return unquote(credentials)


def extract_http_basic_auth(request: HttpRequest) -> tuple[str, str]:
    """Extract HTTP Basic Auth credentials from a request object. Return a tuple with username and password"""
    credentials = extract_generic_token(request, "Authorization", "Basic")

    uname, passwd = base64.b64decode(credentials).decode("utf-8").split(":")
    return unquote(uname), unquote(passwd)


extract_bearer_token: Callable[[HttpRequest], str] = functools.partial(
    extract_generic_token, header_name="Authorization", auth_type="Bearer"
)
extract_bearer_token.__doc__ = """
Extract a Bearer token from a request object. Return the token.

:param request: HTTP request containing the headers
:return: Token string
"""
