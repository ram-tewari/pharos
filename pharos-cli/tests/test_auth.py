"""Integration tests for authentication commands."""

import pytest
from unittest.mock import MagicMock, patch
from typing import Generator
from pathlib import Path
import sys

# Add pharos_cli to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typer.testing import CliRunner
from pharos_cli.cli import app


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def mock_config(tmp_path, monkeypatch):
    """Create a mock config for testing."""
    import yaml
    from pharos_cli.config.settings import Config, Profile

    # Create a temporary config file
    config_dir = tmp_path / "pharos"
    config_dir.mkdir()
    config_file = config_dir / "config.yaml"

    config = Config(
        active_profile="default",
        profiles={"default": Profile(api_url="http://localhost:8000")}
    )

    config_file.write_text(yaml.dump(config.to_dict()))

    # Monkeypatch the config path
    from pharos_cli.config import settings
    monkeypatch.setattr(settings, "get_config_path", lambda: config_file)

    return config_file


class TestAuthLogin:
    """Tests for the login command."""

    def test_login_with_api_key(self, cli_runner, mock_config, monkeypatch):
        """Test login with API key."""
        # Mock keyring
        mock_keyring = MagicMock()
        monkeypatch.setattr("keyring.set_password", mock_keyring)

        # Mock the API client
        mock_client = MagicMock()
        mock_client.get.return_value = {"username": "testuser", "email": "test@example.com"}
        monkeypatch.setattr(
            "pharos_cli.commands.auth.get_api_client",
            lambda config: mock_client
        )

        result = cli_runner.invoke(app, [
            "auth", "login",
            "--api-key", "test-api-key-123"
        ])

        assert result.exit_code == 0
        assert "testuser" in result.stdout
        assert "API key saved securely" in result.stdout

    def test_login_with_api_key_verification_failure(self, cli_runner, mock_config, monkeypatch):
        """Test login with API key when verification fails."""
        from pharos_cli.client.exceptions import AuthenticationError

        # Mock keyring
        mock_keyring = MagicMock()
        monkeypatch.setattr("keyring.set_password", mock_keyring)

        # Mock the API client to raise AuthenticationError
        mock_client = MagicMock()
        mock_client.get.side_effect = AuthenticationError("Invalid token")
        monkeypatch.setattr(
            "pharos_cli.commands.auth.get_api_client",
            lambda config: mock_client
        )

        result = cli_runner.invoke(app, [
            "auth", "login",
            "--api-key", "invalid-key"
        ])

        assert result.exit_code == 1
        assert "Authentication failed" in result.stdout

    def test_login_with_url_option(self, cli_runner, mock_config, monkeypatch):
        """Test login with URL option."""
        mock_keyring = MagicMock()
        monkeypatch.setattr("keyring.set_password", mock_keyring)

        mock_client = MagicMock()
        mock_client.get.return_value = {"username": "testuser"}
        monkeypatch.setattr(
            "pharos_cli.commands.auth.get_api_client",
            lambda config: mock_client
        )

        result = cli_runner.invoke(app, [
            "auth", "login",
            "--api-key", "test-key",
            "--url", "https://pharos.example.com"
        ])

        assert result.exit_code == 0
        assert "https://pharos.example.com" in result.stdout

    def test_login_without_credentials(self, cli_runner, mock_config):
        """Test login without providing credentials."""
        result = cli_runner.invoke(app, ["auth", "login"])

        assert result.exit_code == 1
        assert "No authentication method specified" in result.stdout

    def test_login_oauth_flag_requires_browser(self, cli_runner, mock_config, monkeypatch):
        """Test that --oauth flag is recognized."""
        # This test just checks that the option is accepted
        # Full OAuth flow testing would require a mock server

        # Mock the callback server to fail
        mock_server = MagicMock()
        mock_server.serve_forever.side_effect = OSError("Port in use")
        monkeypatch.setattr(
            "pharos_cli.commands.auth.start_callback_server",
            lambda port: (_ for _ in ()).throw(OSError("Port in use"))
        )

        result = cli_runner.invoke(app, [
            "auth", "login",
            "--oauth"
        ])

        # Should fail with port error, not with unrecognized option
        assert "Failed to start callback server" in result.stdout or "Port" in result.stdout


class TestAuthLogout:
    """Tests for the logout command."""

    def test_logout_clears_credentials(self, cli_runner, mock_config, monkeypatch):
        """Test that logout clears credentials."""
        from pharos_cli.config.settings import load_config, save_config, Config, Profile
        from unittest.mock import patch

        # Clear the config cache
        load_config.cache_clear()

        # Create config with API key
        config = Config(
            active_profile="default",
            profiles={"default": Profile(api_url="http://localhost:8000", api_key="test-key")}
        )
        save_config(config)

        # Mock keyring.delete_password
        mock_delete = MagicMock()
        mock_keyring = MagicMock()
        mock_keyring.delete_password = mock_delete

        # Mock the API client for server-side logout
        mock_client = MagicMock()

        # Patch keyring module where it's imported in the function
        with patch.dict("sys.modules", {"keyring": mock_keyring}):
            monkeypatch.setattr(
                "pharos_cli.commands.auth.get_api_client",
                lambda config=None: mock_client
            )
            result = cli_runner.invoke(app, ["auth", "logout"])

        assert result.exit_code == 0
        assert "Logged out successfully" in result.stdout
        mock_delete.assert_called_once()

    def test_logout_handles_keyring_error(self, cli_runner, mock_config, monkeypatch):
        """Test logout handles keyring errors gracefully."""
        import keyring.errors

        mock_keyring = MagicMock()
        mock_keyring.delete_password.side_effect = keyring.errors.KeyringError("Error")
        monkeypatch.setattr("keyring.delete_password", mock_keyring)

        mock_client = MagicMock()
        monkeypatch.setattr(
            "pharos_cli.commands.auth.get_api_client",
            lambda config: mock_client
        )

        result = cli_runner.invoke(app, ["auth", "logout"])

        # Should still succeed even if keyring fails
        assert result.exit_code == 0


class TestAuthWhoami:
    """Tests for the whoami command."""

    def test_whoami_shows_user_info(self, cli_runner, mock_config, monkeypatch):
        """Test that whoami shows user information."""
        from pharos_cli.config.settings import load_config, save_config, Config, Profile
        import time

        # Create config with API key
        config = Config(
            active_profile="default",
            profiles={"default": Profile(
                api_url="http://localhost:8000",
                api_key="test-key",
                token_expires_at=int(time.time()) + 3600
            )}
        )
        save_config(config)

        mock_client = MagicMock()
        mock_client.get.return_value = {
            "username": "testuser",
            "email": "test@example.com",
            "id": 123
        }
        monkeypatch.setattr(
            "pharos_cli.commands.auth.get_api_client",
            lambda config=None: mock_client
        )

        result = cli_runner.invoke(app, ["auth", "whoami"])

        assert result.exit_code == 0
        assert "testuser" in result.stdout
        assert "test@example.com" in result.stdout
        assert "123" in result.stdout

    def test_whoami_not_authenticated(self, cli_runner, mock_config, monkeypatch):
        """Test whoami when not authenticated."""
        from pharos_cli.client.exceptions import AuthenticationError

        mock_client = MagicMock()
        mock_client.get.side_effect = AuthenticationError("Not authenticated")
        monkeypatch.setattr(
            "pharos_cli.commands.auth.get_api_client",
            lambda config=None: mock_client
        )

        result = cli_runner.invoke(app, ["auth", "whoami"])

        assert result.exit_code == 1
        assert "Not authenticated" in result.stdout


class TestAuthStatus:
    """Tests for the auth status command."""

    def test_status_authenticated(self, cli_runner, mock_config, monkeypatch):
        """Test status when authenticated."""
        from pharos_cli.config.settings import load_config, save_config, Config, Profile
        import time

        # Clear the config cache
        load_config.cache_clear()

        # Create config with API key
        config = Config(
            active_profile="default",
            profiles={"default": Profile(
                api_url="http://localhost:8000",
                api_key="test-key",
                token_expires_at=int(time.time()) + 3600
            )}
        )
        save_config(config)

        result = cli_runner.invoke(app, ["auth", "status"])

        assert result.exit_code == 0
        assert "Authenticated" in result.stdout

    def test_status_not_authenticated(self, cli_runner, mock_config, monkeypatch):
        """Test status when not authenticated."""
        from pharos_cli.config.settings import load_config, save_config, Config, Profile

        # Clear the config cache
        load_config.cache_clear()

        # Create a config without API key
        config = Config(
            active_profile="default",
            profiles={"default": Profile(api_url="http://localhost:8000", api_key=None)}
        )
        save_config(config)

        result = cli_runner.invoke(app, ["auth", "status"])

        assert result.exit_code == 0
        assert "Not authenticated" in result.stdout


class TestAuthHelp:
    """Tests for auth command help."""

    def test_auth_help(self, cli_runner):
        """Test that auth help shows available commands."""
        result = cli_runner.invoke(app, ["auth", "--help"])

        assert result.exit_code == 0
        assert "login" in result.stdout
        assert "logout" in result.stdout
        assert "whoami" in result.stdout
        assert "status" in result.stdout

    def test_login_help(self, cli_runner):
        """Test that login help shows all options."""
        result = cli_runner.invoke(app, ["auth", "login", "--help"])

        assert result.exit_code == 0
        assert "--api-key" in result.stdout or "api-key" in result.stdout
        assert "--oauth" in result.stdout or "oauth" in result.stdout
        assert "--provider" in result.stdout or "provider" in result.stdout


class TestOAuthFlow:
    """Tests for OAuth2 flow components."""

    def test_oauth_callback_handler(self):
        """Test the OAuth callback handler."""
        from pharos_cli.commands.auth import OAuthCallbackHandler

        # Reset the handler
        OAuthCallbackHandler.reset()

        # Create a mock request
        handler = OAuthCallbackHandler.__new__(OAuthCallbackHandler)
        handler.path = "/callback?code=test123&state=abc"
        handler.wfile = MagicMock()
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()

        # Process the request
        handler.do_GET()

        # Verify the response
        handler.send_response.assert_called_with(200)
        assert OAuthCallbackHandler.auth_code == "test123"

    def test_oauth_callback_handler_with_error(self):
        """Test the OAuth callback handler with error."""
        from pharos_cli.commands.auth import OAuthCallbackHandler

        # Reset the handler
        OAuthCallbackHandler.reset()

        # Create a mock request with error
        handler = OAuthCallbackHandler.__new__(OAuthCallbackHandler)
        handler.path = "/callback?error=access_denied&error_description=User+denied+access"
        handler.wfile = MagicMock()
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()

        # Process the request
        handler.do_GET()

        # Verify the error was captured
        assert OAuthCallbackHandler.error == "access_denied"
        assert OAuthCallbackHandler.error_description == "User denied access"

    def test_start_callback_server(self):
        """Test starting the callback server."""
        from pharos_cli.commands.auth import start_callback_server

        server = start_callback_server(8766)

        # Server should be running
        assert server is not None

        # Shutdown the server
        server.shutdown()


class TestTokenRefresh:
    """Tests for token refresh functionality."""

    def test_sync_api_client_token_refresh(self):
        """Test that SyncAPIClient can refresh tokens."""
        from pharos_cli.client.api_client import SyncAPIClient

        # Create a client with refresh token
        client = SyncAPIClient(
            base_url="http://localhost:8000",
            api_key="old-access-token",
            refresh_token="test-refresh-token",
            token_expires_at=0  # Already expired
        )

        # Mock the HTTP client to return new tokens
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new-access-token",
            "refresh_token": "new-refresh-token",
            "expires_in": 1800
        }
        client._client.post = MagicMock(return_value=mock_response)

        # Attempt to refresh
        result = client._refresh_access_token()

        # Verify refresh was successful
        assert result is True
        assert client.api_key == "new-access-token"
        assert client.refresh_token == "new-refresh-token"

    def test_sync_api_client_token_expiry_check(self):
        """Test token expiry checking."""
        from pharos_cli.client.api_client import SyncAPIClient
        import time

        # Create a client with non-expired token
        client = SyncAPIClient(
            base_url="http://localhost:8000",
            api_key="test-token",
            token_expires_at=int(time.time()) + 3600  # Expires in 1 hour
        )

        # Token should not be expired
        assert client._is_token_expired() is False

        # Create a client with expired token
        client2 = SyncAPIClient(
            base_url="http://localhost:8000",
            api_key="test-token",
            token_expires_at=int(time.time()) - 100  # Expired 100 seconds ago
        )

        # Token should be expired
        assert client2._is_token_expired() is True

    def test_save_tokens_to_config(self, mock_config, monkeypatch):
        """Test saving tokens to config."""
        from pharos_cli.client.api_client import save_tokens_to_config
        import time

        # Save tokens
        save_tokens_to_config(
            access_token="new-access-token",
            refresh_token="new-refresh-token",
            expires_in=1800
        )

        # Load config and verify
        from pharos_cli.config.settings import load_config
        config = load_config()
        profile = config.get_active_profile()

        assert profile.api_key == "new-access-token"
        assert profile.refresh_token == "new-refresh-token"
        assert profile.token_expires_at is not None
        assert abs(profile.token_expires_at - (int(time.time()) + 1800)) < 5


class TestAuthEdgeCases:
    """Edge case tests for auth commands."""

    def test_login_with_invalid_oauth_provider(self, cli_runner, mock_config):
        """Test login with invalid OAuth provider."""
        result = cli_runner.invoke(app, [
            "auth", "login",
            "--oauth",
            "--provider", "invalid-provider"
        ])

        assert result.exit_code == 1
        assert "Invalid OAuth provider" in result.stdout

    def test_whoami_with_network_error(self, cli_runner, mock_config, monkeypatch):
        """Test whoami when network error occurs."""
        from pharos_cli.client.exceptions import NetworkError
        from pharos_cli.config.settings import load_config, save_config, Config, Profile
        import time

        # Create config with API key
        config = Config(
            active_profile="default",
            profiles={"default": Profile(
                api_url="http://localhost:8000",
                api_key="test-key",
                token_expires_at=int(time.time()) + 3600
            )}
        )
        save_config(config)

        mock_client = MagicMock()
        mock_client.get.side_effect = NetworkError("Connection failed")
        monkeypatch.setattr(
            "pharos_cli.commands.auth.get_api_client",
            lambda config=None: mock_client
        )

        result = cli_runner.invoke(app, ["auth", "whoami"])

        assert result.exit_code == 1
        assert "Connection failed" in result.stdout

    def test_status_with_refresh_token(self, cli_runner, mock_config, monkeypatch):
        """Test status shows refresh token info."""
        import time
        from pharos_cli.config.settings import load_config, save_config, Config, Profile

        # Create config with refresh token
        config = Config(
            active_profile="default",
            profiles={
                "default": Profile(
                    api_url="http://localhost:8000",
                    api_key="test-key",
                    refresh_token="test-refresh",
                    token_expires_at=int(time.time()) + 1800
                )
            }
        )
        save_config(config)

        result = cli_runner.invoke(app, ["auth", "status"])

        assert result.exit_code == 0
        assert "OAuth2" in result.stdout