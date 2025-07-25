"""Tests for the auth helper functions in modernrpc.auth module."""

import base64
from urllib.parse import quote

import pytest

from modernrpc.auth import (
    extract_bearer_token,
    extract_generic_token,
    extract_header,
    extract_http_basic_auth,
)


class TestExtractHeader:
    """Test the extract_header function."""

    def test_extract_existing_header(self, rf):
        """Test that extract_header returns the correct value for an existing header."""
        request = rf.get("/", headers={"X-Test-Header": "test-value"})

        result = extract_header(request, "X-Test-Header")

        assert result == "test-value"

    def test_extract_missing_header(self, rf):
        """Test that extract_header raises ValueError when the header is missing."""
        request = rf.get("/")

        with pytest.raises(ValueError, match='Unable to find "X-Test-Header" header in request'):
            extract_header(request, "X-Test-Header")


class TestExtractGenericToken:
    """Test the extract_generic_token function."""

    def test_extract_valid_token(self, rf):
        """Test that extract_generic_token returns the correct token for valid input."""
        request = rf.get("/", headers={"Authorization": "Bearer my-token"})

        result = extract_generic_token(request, "Authorization", "Bearer")

        assert result == "my-token"

    def test_extract_quoted_token(self, rf):
        """Test that extract_generic_token handles URL-encoded tokens correctly."""
        token = quote("token with spaces")
        request = rf.get("/", headers={"Authorization": f"Bearer {token}"})

        result = extract_generic_token(request, "Authorization", "Bearer")

        assert result == "token with spaces"

    def test_missing_header(self, rf):
        """Test that extract_generic_token raises ValueError when the header is missing."""
        request = rf.get("/")

        with pytest.raises(ValueError, match='Unable to find "Authorization" header in request'):
            extract_generic_token(request, "Authorization", "Bearer")

    def test_invalid_auth_type(self, rf):
        """Test that extract_generic_token raises ValueError when the auth type is invalid."""
        request = rf.get("/", headers={"Authorization": "Basic dXNlcjpwYXNzd29yZA=="})

        with pytest.raises(ValueError, match='Invalid authentication type. Expected "Bearer", found "Basic"'):
            extract_generic_token(request, "Authorization", "Bearer")


class TestExtractHttpBasicAuth:
    """Test the extract_http_basic_auth function."""

    def test_extract_valid_credentials(self, rf):
        """Test that extract_http_basic_auth returns the correct credentials for valid input."""
        username = "user"
        password = "password"
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode("utf-8")
        request = rf.get("/", headers={"Authorization": f"Basic {credentials}"})

        result_username, result_password = extract_http_basic_auth(request)

        assert result_username == username
        assert result_password == password

    def test_extract_quoted_credentials(self, rf):
        """Test that extract_http_basic_auth handles URL-encoded credentials correctly."""
        username = quote("user with spaces")
        password = quote("password with spaces")
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode("utf-8")
        request = rf.get("/", headers={"Authorization": f"Basic {credentials}"})

        result_username, result_password = extract_http_basic_auth(request)

        assert result_username == "user with spaces"
        assert result_password == "password with spaces"

    def test_missing_header(self, rf):
        """Test that extract_http_basic_auth raises ValueError when the header is missing."""
        request = rf.get("/")

        with pytest.raises(ValueError, match='Unable to find "Authorization" header in request'):
            extract_http_basic_auth(request)

    def test_invalid_auth_type(self, rf):
        """Test that extract_http_basic_auth raises ValueError when the auth type is invalid."""
        request = rf.get("/", headers={"Authorization": "Bearer token"})

        with pytest.raises(ValueError, match='Invalid authentication type. Expected "Basic", found "Bearer"'):
            extract_http_basic_auth(request)

    def test_invalid_credentials_format(self, rf):
        """Test that extract_http_basic_auth raises ValueError when the credential format is invalid."""
        # Missing colon in credentials
        credentials = base64.b64encode(b"userpassword").decode("utf-8")
        request = rf.get("/", headers={"Authorization": f"Basic {credentials}"})

        with pytest.raises(ValueError, match="not enough values to unpack"):
            extract_http_basic_auth(request)


class TestExtractBearerToken:
    """Test the extract_bearer_token function."""

    def test_extract_valid_token(self, rf):
        """Test that extract_bearer_token returns the correct token for valid input."""
        request = rf.get("/", headers={"Authorization": "Bearer my-token"})

        result = extract_bearer_token(request)

        assert result == "my-token"

    def test_extract_quoted_token(self, rf):
        """Test that extract_bearer_token handles URL-encoded tokens correctly."""
        token = quote("token with spaces")
        request = rf.get("/", headers={"Authorization": f"Bearer {token}"})

        result = extract_bearer_token(request)

        assert result == "token with spaces"

    def test_missing_header(self, rf):
        """Test that extract_bearer_token raises ValueError when the header is missing."""
        request = rf.get("/")

        with pytest.raises(ValueError, match='Unable to find "Authorization" header in request'):
            extract_bearer_token(request)

    def test_invalid_auth_type(self, rf):
        """Test that extract_bearer_token raises ValueError when the auth type is invalid."""
        request = rf.get("/", headers={"Authorization": "Basic dXNlcjpwYXNzd29yZA=="})

        with pytest.raises(ValueError, match='Invalid authentication type. Expected "Bearer", found "Basic"'):
            extract_bearer_token(request)
