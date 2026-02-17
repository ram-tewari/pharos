"""Tests for API client module."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import httpx

from pharos_cli.client.api_client import (
    SyncAPIClient,
    APIClient,
    DEFAULT_MAX_RETRIES,
    DEFAULT_INITIAL_DELAY,
    DEFAULT_MAX_DELAY,
    DEFAULT_BACKOFF_MULTIPLIER,
    DEFAULT_JITTER,
    RETRY_STATUS_CODES,
)
from pharos_cli.client.exceptions import APIError, NetworkError


class TestSyncAPIClient:
    """Tests for SyncAPIClient."""

    def test_init(self):
        """Test client initialization."""
        client = SyncAPIClient(
            base_url="http://localhost:8000",
            api_key="test-key",
            timeout=30,
            verify_ssl=True,
        )
        assert client.base_url == "http://localhost:8000"
        assert client.api_key == "test-key"
        assert client.timeout == 30
        assert client.verify_ssl is True

    def test_init_with_retry_config(self):
        """Test client initialization with custom retry configuration."""
        client = SyncAPIClient(
            base_url="http://localhost:8000",
            max_retries=5,
            initial_delay=2.0,
            max_delay=120.0,
            backoff_multiplier=3.0,
            jitter=0.2,
        )
        assert client.max_retries == 5
        assert client.initial_delay == 2.0
        assert client.max_delay == 120.0
        assert client.backoff_multiplier == 3.0
        assert client.jitter == 0.2

    def test_get_headers_without_key(self):
        """Test headers without API key."""
        client = SyncAPIClient(base_url="http://localhost:8000")
        headers = client._get_headers()
        assert "User-Agent" in headers
        assert "Authorization" not in headers

    def test_get_headers_with_key(self):
        """Test headers with API key."""
        client = SyncAPIClient(
            base_url="http://localhost:8000",
            api_key="test-key",
        )
        headers = client._get_headers()
        assert headers["Authorization"] == "Bearer test-key"

    def test_get_success(self, mock_api_client):
        """Test successful GET request."""
        mock_api_client.get.return_value = {"id": 1, "title": "Test"}

        result = mock_api_client.get("/api/v1/resources/1")

        assert result["id"] == 1
        assert result["title"] == "Test"
        mock_api_client.get.assert_called_once()

    def test_post_success(self, mock_api_client):
        """Test successful POST request."""
        mock_api_client.post.return_value = {"id": 1, "title": "Created"}

        result = mock_api_client.post("/api/v1/resources", json={"title": "Test"})

        assert result["id"] == 1
        mock_api_client.post.assert_called_once()

    def test_put_success(self, mock_api_client):
        """Test successful PUT request."""
        mock_api_client.put.return_value = {"id": 1, "title": "Updated"}

        result = mock_api_client.put("/api/v1/resources/1", json={"title": "Updated"})

        assert result["title"] == "Updated"
        mock_api_client.put.assert_called_once()

    def test_delete_success(self, mock_api_client):
        """Test successful DELETE request."""
        mock_api_client.delete.return_value = {"success": True}

        result = mock_api_client.delete("/api/v1/resources/1")

        assert result["success"] is True
        mock_api_client.delete.assert_called_once()

    def test_api_error(self, mock_api_client):
        """Test API error handling."""
        import httpx

        mock_api_client.get.side_effect = APIError(
            status_code=404,
            message="Resource not found",
            details={"id": 1},
        )

        with pytest.raises(APIError) as exc_info:
            mock_api_client.get("/api/v1/resources/1")

        assert exc_info.value.status_code == 404
        assert "Resource not found" in str(exc_info.value)

    def test_network_error(self, mock_api_client):
        """Test network error handling."""
        mock_api_client.get.side_effect = NetworkError("Connection refused")

        with pytest.raises(NetworkError) as exc_info:
            mock_api_client.get("/api/v1/resources/1")

        assert "Connection refused" in str(exc_info.value)


class TestRetryLogic:
    """Tests for retry logic with exponential backoff."""

    def test_should_retry_5xx_errors(self):
        """Test that 5xx errors trigger retry."""
        client = SyncAPIClient(base_url="http://localhost:8000")
        for status_code in [500, 502, 503, 504]:
            assert client._should_retry(status_code) is True

    def test_should_retry_429(self):
        """Test that 429 (rate limit) triggers retry."""
        client = SyncAPIClient(base_url="http://localhost:8000")
        assert client._should_retry(429) is True

    def test_should_not_retry_4xx_errors(self):
        """Test that 4xx errors (except 429) don't trigger retry."""
        client = SyncAPIClient(base_url="http://localhost:8000")
        for status_code in [400, 401, 403, 404, 422]:
            assert client._should_retry(status_code) is False

    def test_exponential_backoff_calculation(self):
        """Test exponential backoff delay calculation."""
        client = SyncAPIClient(
            base_url="http://localhost:8000",
            initial_delay=1.0,
            max_delay=60.0,
            backoff_multiplier=2.0,
            jitter=0.0,  # No jitter for predictable tests
        )

        # Attempt 0: delay = 1.0 * 2^0 = 1.0
        delay = client._calculate_delay(0)
        assert delay == 1.0

        # Attempt 1: delay = 1.0 * 2^1 = 2.0
        delay = client._calculate_delay(1)
        assert delay == 2.0

        # Attempt 2: delay = 1.0 * 2^2 = 4.0
        delay = client._calculate_delay(2)
        assert delay == 4.0

        # Attempt 3: delay = 1.0 * 2^3 = 8.0
        delay = client._calculate_delay(3)
        assert delay == 8.0

    def test_max_delay_cap(self):
        """Test that delay is capped at max_delay."""
        client = SyncAPIClient(
            base_url="http://localhost:8000",
            initial_delay=10.0,
            max_delay=30.0,
            backoff_multiplier=2.0,
            jitter=0.0,
        )

        # Attempt 2: would be 40.0, but capped at 30.0
        delay = client._calculate_delay(2)
        assert delay == 30.0

        # Attempt 3: would be 80.0, but capped at 30.0
        delay = client._calculate_delay(3)
        assert delay == 30.0

    def test_jitter_variation(self):
        """Test that jitter adds variation to delay."""
        client = SyncAPIClient(
            base_url="http://localhost:8000",
            initial_delay=1.0,
            max_delay=60.0,
            backoff_multiplier=2.0,
            jitter=0.1,  # 10% jitter
        )

        # Get multiple delays and verify they vary slightly
        delays = [client._calculate_delay(0) for _ in range(10)]
        base_delay = 1.0

        # All delays should be close to base_delay (within 10%)
        for delay in delays:
            assert 0.9 <= delay <= 1.1

        # At least some should be different (jitter is working)
        assert len(set(delays)) > 1

    def test_retry_on_500_error(self):
        """Test retry on 500 server error using mocks."""
        # Create mock client
        with patch("pharos_cli.client.api_client.httpx.Client") as mock_client_class:
            # First response is 500
            mock_response_500 = MagicMock()
            mock_response_500.status_code = 500
            mock_response_500.raise_for_status = MagicMock(
                side_effect=httpx.HTTPStatusError(
                    "Server Error",
                    request=MagicMock(),
                    response=mock_response_500,
                )
            )

            # Second response is success
            mock_response_200 = MagicMock()
            mock_response_200.status_code = 200
            mock_response_200.json.return_value = {"id": 1, "title": "Test"}
            mock_response_200.raise_for_status = MagicMock()

            mock_client = MagicMock()
            mock_client.request = MagicMock(
                side_effect=[mock_response_500, mock_response_200]
            )
            mock_client_class.return_value = mock_client

            client = SyncAPIClient(
                base_url="http://localhost:8000",
                max_retries=3,
                initial_delay=0.01,
            )

            result = client.get("/api/v1/resources/1")
            assert result["id"] == 1
            assert result["title"] == "Test"
            assert mock_client.request.call_count == 2

    def test_retry_on_503_error(self):
        """Test retry on 503 service unavailable."""
        with patch("pharos_cli.client.api_client.httpx.Client") as mock_client_class:
            mock_response_503 = MagicMock()
            mock_response_503.status_code = 503
            mock_response_503.raise_for_status = MagicMock(
                side_effect=httpx.HTTPStatusError(
                    "Service Unavailable",
                    request=MagicMock(),
                    response=mock_response_503,
                )
            )

            mock_response_200 = MagicMock()
            mock_response_200.status_code = 200
            mock_response_200.json.return_value = {"id": 1, "title": "Test"}
            mock_response_200.raise_for_status = MagicMock()

            mock_client = MagicMock()
            mock_client.request = MagicMock(
                side_effect=[mock_response_503, mock_response_200]
            )
            mock_client_class.return_value = mock_client

            client = SyncAPIClient(
                base_url="http://localhost:8000",
                max_retries=3,
                initial_delay=0.01,
            )

            result = client.get("/api/v1/resources/1")
            assert result["id"] == 1
            assert mock_client.request.call_count == 2

    def test_retry_on_429_error(self):
        """Test retry on 429 rate limiting."""
        with patch("pharos_cli.client.api_client.httpx.Client") as mock_client_class:
            mock_response_429 = MagicMock()
            mock_response_429.status_code = 429
            mock_response_429.raise_for_status = MagicMock(
                side_effect=httpx.HTTPStatusError(
                    "Too Many Requests",
                    request=MagicMock(),
                    response=mock_response_429,
                )
            )

            mock_response_200 = MagicMock()
            mock_response_200.status_code = 200
            mock_response_200.json.return_value = {"id": 1, "title": "Test"}
            mock_response_200.raise_for_status = MagicMock()

            mock_client = MagicMock()
            mock_client.request = MagicMock(
                side_effect=[mock_response_429, mock_response_200]
            )
            mock_client_class.return_value = mock_client

            client = SyncAPIClient(
                base_url="http://localhost:8000",
                max_retries=3,
                initial_delay=0.01,
            )

            result = client.get("/api/v1/resources/1")
            assert result["id"] == 1
            assert mock_client.request.call_count == 2

    def test_no_retry_on_404_error(self):
        """Test that 404 errors are not retried."""
        with patch("pharos_cli.client.api_client.httpx.Client") as mock_client_class:
            mock_response_404 = MagicMock()
            mock_response_404.status_code = 404
            mock_response_404.json.return_value = {"detail": "Resource not found"}
            mock_response_404.raise_for_status = MagicMock(
                side_effect=httpx.HTTPStatusError(
                    "Not Found",
                    request=MagicMock(),
                    response=mock_response_404,
                )
            )

            mock_client = MagicMock()
            mock_client.request = MagicMock(return_value=mock_response_404)
            mock_client_class.return_value = mock_client

            client = SyncAPIClient(
                base_url="http://localhost:8000",
                max_retries=3,
                initial_delay=0.01,
            )

            with pytest.raises(APIError) as exc_info:
                client.get("/api/v1/resources/999")

            assert exc_info.value.status_code == 404
            # Should only be called once (no retry on 404)
            assert mock_client.request.call_count == 1

    def test_max_retries_exceeded(self):
        """Test that after max retries, an error is raised."""
        with patch("pharos_cli.client.api_client.httpx.Client") as mock_client_class:
            mock_response_500 = MagicMock()
            mock_response_500.status_code = 500
            mock_response_500.raise_for_status = MagicMock(
                side_effect=httpx.HTTPStatusError(
                    "Server Error",
                    request=MagicMock(),
                    response=mock_response_500,
                )
            )

            mock_client = MagicMock()
            mock_client.request = MagicMock(return_value=mock_response_500)
            mock_client_class.return_value = mock_client

            client = SyncAPIClient(
                base_url="http://localhost:8000",
                max_retries=3,
                initial_delay=0.01,
            )

            with pytest.raises(APIError) as exc_info:
                client.get("/api/v1/resources/1")

            assert exc_info.value.status_code == 500
            # Should be called 4 times (max_retries + 1)
            assert mock_client.request.call_count == 4

    def test_retry_on_network_error(self):
        """Test retry on network errors."""
        with patch("pharos_cli.client.api_client.httpx.Client") as mock_client_class:
            mock_response_200 = MagicMock()
            mock_response_200.status_code = 200
            mock_response_200.json.return_value = {"id": 1, "title": "Test"}
            mock_response_200.raise_for_status = MagicMock()

            mock_client = MagicMock()
            mock_client.request = MagicMock(
                side_effect=[httpx.RequestError("Connection refused"), mock_response_200]
            )
            mock_client_class.return_value = mock_client

            client = SyncAPIClient(
                base_url="http://localhost:8000",
                max_retries=3,
                initial_delay=0.01,
            )

            result = client.get("/api/v1/resources/1")
            assert result["id"] == 1
            assert mock_client.request.call_count == 2

    def test_disable_retries(self):
        """Test that retries can be disabled with max_retries=0."""
        with patch("pharos_cli.client.api_client.httpx.Client") as mock_client_class:
            mock_response_500 = MagicMock()
            mock_response_500.status_code = 500
            mock_response_500.raise_for_status = MagicMock(
                side_effect=httpx.HTTPStatusError(
                    "Server Error",
                    request=MagicMock(),
                    response=mock_response_500,
                )
            )

            mock_client = MagicMock()
            mock_client.request = MagicMock(return_value=mock_response_500)
            mock_client_class.return_value = mock_client

            client = SyncAPIClient(
                base_url="http://localhost:8000",
                max_retries=0,
                initial_delay=0.01,
            )

            with pytest.raises(APIError) as exc_info:
                client.get("/api/v1/resources/1")

            assert exc_info.value.status_code == 500
            # Should only be called once (no retries)
            assert mock_client.request.call_count == 1


class TestAPIClientAsync:
    """Tests for async APIClient."""

    @pytest.mark.asyncio
    async def test_init(self):
        """Test async client initialization."""
        client = APIClient(
            base_url="http://localhost:8000",
            api_key="test-key",
            timeout=30,
            verify_ssl=True,
        )
        assert client.base_url == "http://localhost:8000"
        assert client.api_key == "test-key"
        await client.close()

    @pytest.mark.asyncio
    async def test_init_with_retry_config(self):
        """Test async client initialization with custom retry configuration."""
        client = APIClient(
            base_url="http://localhost:8000",
            max_retries=5,
            initial_delay=2.0,
            max_delay=120.0,
        )
        assert client.max_retries == 5
        assert client.initial_delay == 2.0
        assert client.max_delay == 120.0
        await client.close()

    @pytest.mark.asyncio
    async def test_get_success(self):
        """Test successful async GET request."""
        with patch("pharos_cli.client.api_client.httpx.AsyncClient") as mock_client_class:
            mock_response = MagicMock()
            mock_response.json.return_value = {"id": 1, "title": "Test"}
            mock_response.raise_for_status = MagicMock()

            mock_client = MagicMock()
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock()
            mock_client_class.return_value = mock_client

            client = APIClient(base_url="http://localhost:8000")
            result = await client.get("/api/v1/resources/1")

            assert result["id"] == 1
            await client.close()

    @pytest.mark.asyncio
    async def test_async_retry_on_500(self):
        """Test async client retry on 500 error."""
        with patch("pharos_cli.client.api_client.httpx.AsyncClient") as mock_client_class:
            mock_response_500 = MagicMock()
            mock_response_500.status_code = 500
            mock_response_500.raise_for_status = MagicMock(
                side_effect=httpx.HTTPStatusError(
                    "Server Error",
                    request=MagicMock(),
                    response=mock_response_500,
                )
            )

            mock_response_200 = MagicMock()
            mock_response_200.status_code = 200
            mock_response_200.json.return_value = {"id": 1, "title": "Test"}
            mock_response_200.raise_for_status = MagicMock()

            mock_client = MagicMock()
            mock_client.request = AsyncMock(
                side_effect=[mock_response_500, mock_response_200]
            )
            mock_client.aclose = AsyncMock()
            mock_client_class.return_value = mock_client

            client = APIClient(
                base_url="http://localhost:8000",
                max_retries=3,
                initial_delay=0.01,
            )
            result = await client.get("/api/v1/resources/1")

            assert result["id"] == 1
            assert mock_client.request.call_count == 2
            await client.close()


class TestAPIError:
    """Tests for APIError exception."""

    def test_api_error_creation(self):
        """Test APIError creation."""
        error = APIError(
            status_code=400,
            message="Bad request",
            details={"field": "error"},
        )
        assert error.status_code == 400
        assert "Bad request" in str(error)
        assert error.details["field"] == "error"

    def test_api_error_from_response(self):
        """Test creating APIError from HTTP response."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"detail": "Internal server error"}
        mock_response.text = "Internal server error"

        error = APIError.from_response(mock_response)

        assert error.status_code == 500
        assert "Internal server error" in str(error)


class TestNetworkError:
    """Tests for NetworkError exception."""

    def test_network_error_creation(self):
        """Test NetworkError creation."""
        error = NetworkError("Connection refused")
        assert "Connection refused" in str(error)


class TestRetryConstants:
    """Tests for retry configuration constants."""

    def test_default_max_retries(self):
        """Test default max retries value."""
        assert DEFAULT_MAX_RETRIES == 3

    def test_default_initial_delay(self):
        """Test default initial delay value."""
        assert DEFAULT_INITIAL_DELAY == 1.0

    def test_default_max_delay(self):
        """Test default max delay value."""
        assert DEFAULT_MAX_DELAY == 60.0

    def test_default_backoff_multiplier(self):
        """Test default backoff multiplier value."""
        assert DEFAULT_BACKOFF_MULTIPLIER == 2.0

    def test_default_jitter(self):
        """Test default jitter value."""
        assert DEFAULT_JITTER == 0.1

    def test_retry_status_codes(self):
        """Test retry status codes set."""
        assert 429 in RETRY_STATUS_CODES
        assert 500 in RETRY_STATUS_CODES
        assert 502 in RETRY_STATUS_CODES
        assert 503 in RETRY_STATUS_CODES
        assert 504 in RETRY_STATUS_CODES
        assert 400 not in RETRY_STATUS_CODES
        assert 404 not in RETRY_STATUS_CODES