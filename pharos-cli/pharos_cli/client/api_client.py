"""Base API client for Pharos CLI."""

import asyncio
import json
import logging
import random
import time
from typing import Any, Dict, Optional, Tuple, Union, Callable
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel

from pharos_cli.version import __version__
from pharos_cli.client.exceptions import APIError, NetworkError, AuthenticationError
from pharos_cli.utils.console import get_console

logger = logging.getLogger(__name__)


# Retry configuration constants
DEFAULT_MAX_RETRIES = 3
DEFAULT_INITIAL_DELAY = 1.0  # seconds
DEFAULT_MAX_DELAY = 60.0  # seconds
DEFAULT_BACKOFF_MULTIPLIER = 2.0
DEFAULT_JITTER = 0.1  # 10% jitter

# HTTP status codes that should trigger a retry
RETRY_STATUS_CODES = {429, 500, 502, 503, 504}


class APIResponse(BaseModel):
    """Generic API response wrapper."""

    data: Any
    status_code: int
    headers: Dict[str, str]


class PaginatedResponse(BaseModel):
    """Paginated API response."""

    items: list
    total: int
    page: int
    per_page: int
    has_more: bool


class APIClient:
    """Asynchronous HTTP client for Pharos API."""

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        verify_ssl: bool = True,
        max_retries: int = DEFAULT_MAX_RETRIES,
        initial_delay: float = DEFAULT_INITIAL_DELAY,
        max_delay: float = DEFAULT_MAX_DELAY,
        backoff_multiplier: float = DEFAULT_BACKOFF_MULTIPLIER,
        jitter: float = DEFAULT_JITTER,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        # Retry configuration
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            verify=verify_ssl,
            headers=self._get_headers(),
        )

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {
            "User-Agent": f"pharos-cli/{__version__}",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _should_retry(self, status_code: int) -> bool:
        """Check if request should be retried based on status code."""
        return status_code in RETRY_STATUS_CODES

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter."""
        delay = self.initial_delay * (self.backoff_multiplier ** attempt)
        delay = min(delay, self.max_delay)
        # Add jitter (random variation)
        jitter_amount = delay * self.jitter
        delay = delay + random.uniform(-jitter_amount, jitter_amount)
        return max(0, delay)

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle HTTP response and raise appropriate errors."""
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                message = error_data.get("detail", str(e))
                details = error_data
            except Exception:
                message = str(e)
                details = {}

            raise APIError(
                status_code=e.response.status_code,
                message=message,
                details=details,
            )
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}")

    async def request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> Any:
        """Make async HTTP request with retry logic and exponential backoff."""
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.request(method, url, **kwargs)

                # Check if we should retry
                if self._should_retry(response.status_code) and attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"Request failed with status {response.status_code}, "
                        f"retrying in {delay:.2f}s (attempt {attempt + 1}/{self.max_retries + 1})"
                    )
                    await asyncio.sleep(delay)
                    continue

                return self._handle_response(response)

            except (httpx.RequestError, NetworkError) as e:
                last_exception = e

                # Check if we should retry network errors
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"Network error: {e}, retrying in {delay:.2f}s "
                        f"(attempt {attempt + 1}/{self.max_retries + 1})"
                    )
                    await asyncio.sleep(delay)
                else:
                    raise NetworkError(f"Network error after {self.max_retries + 1} attempts: {e}")

        # This should not be reached, but raise last exception if it was
        if last_exception:
            raise last_exception
        raise NetworkError("Unknown network error")

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make GET request."""
        return await self.request("GET", endpoint, params=params)

    async def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Any] = None,
    ) -> Any:
        """Make POST request."""
        return await self.request("POST", endpoint, json=json, data=data, files=files)

    async def put(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make PUT request."""
        return await self.request("PUT", endpoint, json=json)

    async def patch(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make PATCH request."""
        return await self.request("PATCH", endpoint, json=json)

    async def delete(
        self,
        endpoint: str,
    ) -> Any:
        """Make DELETE request."""
        return await self.request("DELETE", endpoint)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "APIClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()


class SyncAPIClient:
    """Synchronous HTTP client for Pharos API."""

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        refresh_token: Optional[str] = None,
        token_expires_at: Optional[int] = None,
        timeout: int = 30,
        verify_ssl: bool = True,
        max_retries: int = DEFAULT_MAX_RETRIES,
        initial_delay: float = DEFAULT_INITIAL_DELAY,
        max_delay: float = DEFAULT_MAX_DELAY,
        backoff_multiplier: float = DEFAULT_BACKOFF_MULTIPLIER,
        jitter: float = DEFAULT_JITTER,
        on_token_refresh: Optional[Callable[[str, str, int], None]] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self._api_key = api_key
        self.refresh_token = refresh_token
        self.token_expires_at = token_expires_at
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        # Retry configuration
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter

        # Callback for token refresh events
        self._on_token_refresh = on_token_refresh

        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            verify=verify_ssl,
            headers=self._get_headers(),
        )

    @property
    def api_key(self) -> Optional[str]:
        """Get the current API key."""
        return self._api_key

    @api_key.setter
    def api_key(self, value: Optional[str]) -> None:
        """Set the API key and update headers."""
        self._api_key = value
        self._client.headers.update(self._get_headers())

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {
            "User-Agent": f"pharos-cli/{__version__}",
            "Accept": "application/json",
        }
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    def _should_retry(self, status_code: int) -> bool:
        """Check if request should be retried based on status code."""
        return status_code in RETRY_STATUS_CODES

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter."""
        delay = self.initial_delay * (self.backoff_multiplier ** attempt)
        delay = min(delay, self.max_delay)
        # Add jitter (random variation)
        jitter_amount = delay * self.jitter
        delay = delay + random.uniform(-jitter_amount, jitter_amount)
        return max(0, delay)

    def _is_token_expired(self) -> bool:
        """Check if the access token is expired or will expire soon."""
        if self.token_expires_at is None:
            return False
        # Refresh if token expires in less than 5 minutes
        import time as time_module
        return time_module.time() + 300 > self.token_expires_at

    def _refresh_access_token(self) -> bool:
        """Refresh the access token using the refresh token.

        Returns True if refresh was successful, False otherwise.
        """
        if not self.refresh_token:
            logger.warning("No refresh token available")
            return False

        url = urljoin(self.base_url + "/", "auth/refresh")
        try:
            response = self._client.post(
                "auth/refresh",
                headers={"Authorization": f"Bearer {self.refresh_token}"}
            )

            if response.status_code == 200:
                data = response.json()
                self._api_key = data.get("access_token")
                self.refresh_token = data.get("refresh_token", self.refresh_token)

                # Update token expiration if provided
                expires_in = data.get("expires_in", 1800)
                import time as time_module
                self.token_expires_at = int(time_module.time()) + expires_in

                # Update headers with new access token
                self._client.headers.update(self._get_headers())

                # Notify callback
                if self._on_token_refresh:
                    self._on_token_refresh(
                        self._api_key,
                        self.refresh_token,
                        self.token_expires_at
                    )

                logger.info("Access token refreshed successfully")
                return True
            else:
                logger.warning(f"Token refresh failed with status {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return False

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle HTTP response and raise appropriate errors."""
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                message = error_data.get("detail", str(e))
                details = error_data
            except Exception:
                message = str(e)
                details = {}

            raise APIError(
                status_code=e.response.status_code,
                message=message,
                details=details,
            )
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}")

    def request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> Any:
        """Make HTTP request with retry logic and exponential backoff."""
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))
        last_exception = None
        token_refreshed = False

        for attempt in range(self.max_retries + 1):
            try:
                response = self._client.request(method, url, **kwargs)

                # Check if we should retry
                if self._should_retry(response.status_code) and attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"Request failed with status {response.status_code}, "
                        f"retrying in {delay:.2f}s (attempt {attempt + 1}/{self.max_retries + 1})"
                    )
                    time.sleep(delay)
                    continue

                # Handle 401 Unauthorized - try to refresh token
                if response.status_code == 401 and not token_refreshed and self.refresh_token:
                    logger.info("Received 401, attempting token refresh...")
                    if self._refresh_access_token():
                        token_refreshed = True
                        # Retry the request with the new token
                        continue
                    else:
                        # Refresh failed, try to get new credentials
                        raise AuthenticationError("Authentication failed. Please login again.")

                return self._handle_response(response)

            except (httpx.RequestError, NetworkError) as e:
                last_exception = e

                # Check if we should retry network errors
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"Network error: {e}, retrying in {delay:.2f}s "
                        f"(attempt {attempt + 1}/{self.max_retries + 1})"
                    )
                    time.sleep(delay)
                else:
                    raise NetworkError(f"Network error after {self.max_retries + 1} attempts: {e}")

        # This should not be reached, but raise last exception if it was
        if last_exception:
            raise last_exception
        raise NetworkError("Unknown network error")

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make GET request."""
        return self.request("GET", endpoint, params=params)

    def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Any] = None,
    ) -> Any:
        """Make POST request."""
        return self.request("POST", endpoint, json=json, data=data, files=files)

    def put(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make PUT request."""
        return self.request("PUT", endpoint, json=json)

    def patch(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make PATCH request."""
        return self.request("PATCH", endpoint, json=json)

    def delete(
        self,
        endpoint: str,
    ) -> Any:
        """Make DELETE request."""
        return self.request("DELETE", endpoint)

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> "SyncAPIClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


def get_api_client(config=None) -> SyncAPIClient:
    """Get an API client instance from config."""
    from pharos_cli.config.settings import load_config, apply_env_overrides

    if config is None:
        config = load_config()
        config = apply_env_overrides(config)

    profile = config.get_active_profile()
    return SyncAPIClient(
        base_url=profile.api_url,
        api_key=profile.api_key,
        refresh_token=profile.refresh_token,
        token_expires_at=profile.token_expires_at,
        timeout=profile.timeout,
        verify_ssl=profile.verify_ssl,
    )


def save_tokens_to_config(
    access_token: str,
    refresh_token: str,
    expires_in: int,
    config=None
) -> None:
    """Save authentication tokens to the config file.

    Args:
        access_token: The JWT access token
        refresh_token: The refresh token for obtaining new access tokens
        expires_in: Number of seconds until the access token expires
        config: Optional config object, will load from file if not provided
    """
    import time as time_module

    from pharos_cli.config.settings import load_config, save_config

    if config is None:
        config = load_config()

    profile = config.get_active_profile()
    profile.api_key = access_token
    profile.refresh_token = refresh_token
    profile.token_expires_at = int(time_module.time()) + expires_in

    save_config(config)