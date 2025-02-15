from __future__ import annotations

import base64
from typing import TYPE_CHECKING
from urllib.parse import unquote

if TYPE_CHECKING:
    from django.http import HttpRequest


class BaseHeadersParser:
    def __init__(self, request: HttpRequest):
        self.request = request


class HttpBearer(BaseHeadersParser):
    def authorize(self, token: str): ...


class BasicAuth(BaseHeadersParser):
    def parse_request(self) -> tuple[str, str]:
        auth_header_content = self.request.META.get("HTTP_AUTHORIZATION")

        if not auth_header_content:
            raise ValueError("No Auhtorization header found !")

        try:
            auth_type, credentials = auth_header_content.split()
        except (AttributeError, ValueError):
            raise

        # Handle BasicAuth
        if auth_type.lower() == "basic":
            uname, passwd = base64.b64decode(credentials).decode("utf-8").split(":")
            # django_user = authenticate(username=uname, password=passwd)
            # if django_user is not None:
            #     login(request, django_user)
            return unquote(uname), unquote(passwd)
        raise ValueError("Missing required header content!")

    def authorize(self, username: str, password: str): ...


class BaseAuth:
    auth_klass = BasicAuth

    def __call__(self, request: HttpRequest):
        auth = self.auth_klass(request)
        data = auth.parse_request()
        return auth.authorize(*data)
