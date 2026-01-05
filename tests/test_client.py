"""Tests for PostHog API client"""

import pytest
from unittest.mock import Mock, patch

import httpx

from piglet.client import PostHogClient
from piglet.exceptions import (
    AuthenticationError,
    NotFoundError,
    PostHogAPIError,
    RateLimitError,
)


@pytest.fixture
def client():
    """Create a test client"""
    return PostHogClient(api_key="test_key", host="https://us.posthog.com")


class TestPostHogClientInit:
    """Tests for client initialization"""

    def test_init_sets_api_key(self, client):
        assert client.api_key == "test_key"

    def test_init_sets_host(self, client):
        assert client.host == "https://us.posthog.com"

    def test_init_strips_trailing_slash(self):
        client = PostHogClient(api_key="key", host="https://example.com/")
        assert client.host == "https://example.com"

    def test_client_property_creates_httpx_client(self, client):
        with patch.object(httpx, "Client") as mock_client:
            mock_client.return_value = Mock()
            _ = client.client
            mock_client.assert_called_once()


class TestHandleResponse:
    """Tests for _handle_response method"""

    def test_401_raises_authentication_error(self, client):
        response = Mock()
        response.status_code = 401
        with pytest.raises(AuthenticationError):
            client._handle_response(response)

    def test_404_raises_not_found_error(self, client):
        response = Mock()
        response.status_code = 404
        with pytest.raises(NotFoundError):
            client._handle_response(response)

    def test_429_raises_rate_limit_error(self, client):
        response = Mock()
        response.status_code = 429
        with pytest.raises(RateLimitError):
            client._handle_response(response)

    def test_500_raises_api_error(self, client):
        response = Mock()
        response.status_code = 500
        response.text = "Internal Server Error"
        with pytest.raises(PostHogAPIError):
            client._handle_response(response)

    def test_200_returns_json(self, client):
        response = Mock()
        response.status_code = 200
        response.content = b'{"key": "value"}'
        response.json.return_value = {"key": "value"}
        result = client._handle_response(response)
        assert result == {"key": "value"}

    def test_204_returns_empty_dict(self, client):
        response = Mock()
        response.status_code = 204
        response.content = b""
        result = client._handle_response(response)
        assert result == {}


class TestClientMethods:
    """Tests for client HTTP methods"""

    def test_get_makes_get_request(self, client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"data": "test"}'
        mock_response.json.return_value = {"data": "test"}

        mock_http_client = Mock()
        mock_http_client.get.return_value = mock_response
        client._client = mock_http_client

        result = client.get("/api/test/")
        mock_http_client.get.assert_called_once_with("/api/test/", params=None)
        assert result == {"data": "test"}

    def test_post_makes_post_request(self, client):
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.content = b'{"id": 1}'
        mock_response.json.return_value = {"id": 1}

        mock_http_client = Mock()
        mock_http_client.post.return_value = mock_response
        client._client = mock_http_client

        result = client.post("/api/test/", {"name": "test"})
        mock_http_client.post.assert_called_once_with("/api/test/", json={"name": "test"})
        assert result == {"id": 1}

    def test_patch_makes_patch_request(self, client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"id": 1, "name": "updated"}'
        mock_response.json.return_value = {"id": 1, "name": "updated"}

        mock_http_client = Mock()
        mock_http_client.patch.return_value = mock_response
        client._client = mock_http_client

        result = client.patch("/api/test/1/", {"name": "updated"})
        mock_http_client.patch.assert_called_once_with("/api/test/1/", json={"name": "updated"})
        assert result == {"id": 1, "name": "updated"}

    def test_delete_makes_delete_request(self, client):
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.content = b""

        mock_http_client = Mock()
        mock_http_client.delete.return_value = mock_response
        client._client = mock_http_client

        result = client.delete("/api/test/1/")
        mock_http_client.delete.assert_called_once_with("/api/test/1/")
        assert result == {}


class TestFeatureFlagMethods:
    """Tests for feature flag API methods"""

    def test_list_feature_flags(self, client):
        with patch.object(client, "get") as mock_get:
            mock_get.return_value = {"results": []}
            result = client.list_feature_flags(123)
            mock_get.assert_called_once_with("/api/projects/123/feature_flags/")
            assert result == {"results": []}

    def test_get_feature_flag(self, client):
        with patch.object(client, "get") as mock_get:
            mock_get.return_value = {"id": 1, "key": "test"}
            result = client.get_feature_flag(123, 1)
            mock_get.assert_called_once_with("/api/projects/123/feature_flags/1/")
            assert result == {"id": 1, "key": "test"}

    def test_create_feature_flag(self, client):
        with patch.object(client, "post") as mock_post:
            mock_post.return_value = {"id": 1, "key": "new-flag"}
            result = client.create_feature_flag(123, {"key": "new-flag"})
            mock_post.assert_called_once_with(
                "/api/projects/123/feature_flags/",
                {"key": "new-flag"}
            )
            assert result == {"id": 1, "key": "new-flag"}

    def test_update_feature_flag(self, client):
        with patch.object(client, "patch") as mock_patch:
            mock_patch.return_value = {"id": 1, "active": False}
            result = client.update_feature_flag(123, 1, {"active": False})
            mock_patch.assert_called_once_with(
                "/api/projects/123/feature_flags/1/",
                {"active": False}
            )
            assert result == {"id": 1, "active": False}

    def test_delete_feature_flag_uses_soft_delete(self, client):
        with patch.object(client, "patch") as mock_patch:
            mock_patch.return_value = {"id": 1, "deleted": True}
            result = client.delete_feature_flag(123, 1)
            mock_patch.assert_called_once_with(
                "/api/projects/123/feature_flags/1/",
                {"deleted": True}
            )
            assert result == {"id": 1, "deleted": True}


class TestCohortMethods:
    """Tests for cohort API methods"""

    def test_list_cohorts(self, client):
        with patch.object(client, "get") as mock_get:
            mock_get.return_value = {"results": []}
            result = client.list_cohorts(123)
            mock_get.assert_called_once_with("/api/projects/123/cohorts/")

    def test_delete_cohort_uses_soft_delete(self, client):
        with patch.object(client, "patch") as mock_patch:
            mock_patch.return_value = {"id": 1, "deleted": True}
            result = client.delete_cohort(123, 1)
            mock_patch.assert_called_once_with(
                "/api/projects/123/cohorts/1/",
                {"deleted": True}
            )
