"""Unit tests for the keyring store module."""

import pytest
from unittest.mock import MagicMock, patch
from typing import Generator
import sys
from pathlib import Path

# Add pharos_cli to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestKeyringCredentials:
    """Tests for KeyringCredentials dataclass."""

    def test_credentials_creation(self):
        """Test creating credentials with profile name and API key."""
        from pharos_cli.config.keyring_store import KeyringCredentials

        creds = KeyringCredentials(profile_name="default", api_key="test-key-123")
        assert creds.profile_name == "default"
        assert creds.api_key == "test-key-123"

    def test_credentials_is_stored_with_key(self):
        """Test is_stored returns True when API key is present."""
        from pharos_cli.config.keyring_store import KeyringCredentials

        creds = KeyringCredentials(profile_name="default", api_key="test-key")
        assert creds.is_stored() is True

    def test_credentials_is_stored_without_key(self):
        """Test is_stored returns False when API key is None."""
        from pharos_cli.config.keyring_store import KeyringCredentials

        creds = KeyringCredentials(profile_name="default", api_key=None)
        assert creds.is_stored() is False


class TestKeyringStore:
    """Tests for KeyringStore class."""

    @pytest.fixture
    def mock_keyring(self) -> Generator[MagicMock, None, None]:
        """Create a mock keyring module."""
        import keyring.errors
        
        mock = MagicMock()
        mock.errors = keyring.errors
        mock.get_password.return_value = None
        mock.set_password.return_value = None
        mock.delete_password.return_value = None
        yield mock

    def test_get_credential_name(self, mock_keyring: MagicMock):
        """Test credential name generation for a profile."""
        with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring):
            from pharos_cli.config.keyring_store import KeyringStore

            store = KeyringStore(service_name="pharos-cli-test")
            assert store._get_credential_name("default") == "pharos-default"
            assert store._get_credential_name("production") == "pharos-production"
            assert store._get_credential_name("custom-profile") == "pharos-custom-profile"

    def test_set_api_key_success(self, mock_keyring: MagicMock):
        """Test successfully setting an API key."""
        with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring):
            from pharos_cli.config.keyring_store import KeyringStore

            store = KeyringStore(service_name="pharos-cli-test")
            store.set_api_key("default", "test-api-key-123")

            mock_keyring.set_password.assert_called_once_with(
                service_name="pharos-cli-test",
                username="pharos-default",
                password="test-api-key-123",
            )

    def test_set_api_key_failure(self, mock_keyring: MagicMock):
        """Test handling of keyring errors when setting API key."""
        import keyring.errors

        mock_keyring.set_password.side_effect = keyring.errors.KeyringError("Storage error")

        with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring):
            from pharos_cli.config.keyring_store import KeyringStore, KeyringStorageError

            store = KeyringStore(service_name="pharos-cli-test")

            with pytest.raises(KeyringStorageError) as exc_info:
                store.set_api_key("default", "test-key")

            assert "default" in str(exc_info.value)
            assert "Storage error" in str(exc_info.value)

    def test_get_api_key_success(self, mock_keyring: MagicMock):
        """Test successfully retrieving an API key."""
        mock_keyring.get_password.return_value = "test-api-key-456"

        with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring):
            from pharos_cli.config.keyring_store import KeyringStore

            store = KeyringStore(service_name="pharos-cli-test")
            result = store.get_api_key("production")

            assert result == "test-api-key-456"
            mock_keyring.get_password.assert_called_once_with(
                service_name="pharos-cli-test",
                username="pharos-production",
            )

    def test_get_api_key_not_found(self, mock_keyring: MagicMock):
        """Test retrieving a non-existent API key returns None."""
        mock_keyring.get_password.return_value = None

        with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring):
            from pharos_cli.config.keyring_store import KeyringStore

            store = KeyringStore(service_name="pharos-cli-test")
            result = store.get_api_key("nonexistent")

            assert result is None

    def test_get_api_key_failure(self, mock_keyring: MagicMock):
        """Test handling of keyring errors when retrieving API key."""
        import keyring.errors

        mock_keyring.get_password.side_effect = keyring.errors.KeyringError("Retrieval error")

        with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring):
            from pharos_cli.config.keyring_store import KeyringStore, KeyringStorageError

            store = KeyringStore(service_name="pharos-cli-test")

            with pytest.raises(KeyringStorageError) as exc_info:
                store.get_api_key("default")

            assert "default" in str(exc_info.value)
            assert "Retrieval error" in str(exc_info.value)

    def test_delete_api_key_success(self, mock_keyring: MagicMock):
        """Test successfully deleting an API key."""
        mock_keyring.get_password.return_value = "existing-key"
        mock_keyring.delete_password.return_value = None

        with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring):
            from pharos_cli.config.keyring_store import KeyringStore

            store = KeyringStore(service_name="pharos-cli-test")
            result = store.delete_api_key("default")

            assert result is True
            mock_keyring.delete_password.assert_called_once_with(
                service_name="pharos-cli-test",
                username="pharos-default",
            )

    def test_delete_api_key_not_found(self, mock_keyring: MagicMock):
        """Test deleting a non-existent API key returns False."""
        mock_keyring.get_password.return_value = None

        with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring):
            from pharos_cli.config.keyring_store import KeyringStore

            store = KeyringStore(service_name="pharos-cli-test")
            result = store.delete_api_key("nonexistent")

            assert result is False
            mock_keyring.delete_password.assert_not_called()

    def test_delete_api_key_failure(self, mock_keyring: MagicMock):
        """Test handling of keyring errors when deleting API key."""
        import keyring.errors

        mock_keyring.get_password.return_value = "existing-key"
        # Use KeyringError instead of DeleteError (which may not exist in all versions)
        mock_keyring.delete_password.side_effect = keyring.errors.KeyringError("Delete error")

        with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring):
            from pharos_cli.config.keyring_store import KeyringStore, KeyringDeleteError

            store = KeyringStore(service_name="pharos-cli-test")

            with pytest.raises(KeyringDeleteError) as exc_info:
                store.delete_api_key("default")

            assert "default" in str(exc_info.value)
            assert "Delete error" in str(exc_info.value)

    def test_has_api_key_true(self, mock_keyring: MagicMock):
        """Test has_api_key returns True when key exists."""
        mock_keyring.get_password.return_value = "test-key"

        with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring):
            from pharos_cli.config.keyring_store import KeyringStore

            store = KeyringStore(service_name="pharos-cli-test")
            result = store.has_api_key("default")

            assert result is True

    def test_has_api_key_false(self, mock_keyring: MagicMock):
        """Test has_api_key returns False when key doesn't exist."""
        mock_keyring.get_password.return_value = None

        with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring):
            from pharos_cli.config.keyring_store import KeyringStore

            store = KeyringStore(service_name="pharos-cli-test")
            result = store.has_api_key("default")

            assert result is False

    def test_has_api_key_error(self, mock_keyring: MagicMock):
        """Test has_api_key returns False when keyring error occurs."""
        import keyring.errors

        mock_keyring.get_password.side_effect = keyring.errors.KeyringError("Error")

        with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring):
            from pharos_cli.config.keyring_store import KeyringStore

            store = KeyringStore(service_name="pharos-cli-test")
            result = store.has_api_key("default")

            assert result is False

    def test_get_credentials(self, mock_keyring: MagicMock):
        """Test getting credentials object."""
        from pharos_cli.config.keyring_store import KeyringCredentials

        mock_keyring.get_password.return_value = "secret-key"

        with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring):
            from pharos_cli.config.keyring_store import KeyringStore

            store = KeyringStore(service_name="pharos-cli-test")
            creds = store.get_credentials("production")

            assert isinstance(creds, KeyringCredentials)
            assert creds.profile_name == "production"
            assert creds.api_key == "secret-key"
            assert creds.is_stored() is True


class TestKeyringExceptions:
    """Tests for keyring exception classes."""

    def test_keyring_error(self):
        """Test KeyringError exception."""
        from pharos_cli.config.keyring_store import KeyringError

        error = KeyringError("Test error", "default")
        assert str(error) == "Test error"
        assert error.profile_name == "default"

    def test_keyring_not_available_error(self):
        """Test KeyringNotAvailableError exception."""
        from pharos_cli.config.keyring_store import KeyringNotAvailableError

        error = KeyringNotAvailableError("production")
        assert "not available" in str(error)
        assert error.profile_name == "production"

    def test_keyring_storage_error(self):
        """Test KeyringStorageError exception."""
        from pharos_cli.config.keyring_store import KeyringStorageError

        error = KeyringStorageError("Storage failed", "default")
        assert "Storage failed" in str(error)
        assert error.profile_name == "default"

    def test_keyring_delete_error(self):
        """Test KeyringDeleteError exception."""
        from pharos_cli.config.keyring_store import KeyringDeleteError

        error = KeyringDeleteError("Delete failed", "production")
        assert "Delete failed" in str(error)
        assert error.profile_name == "production"


class TestGetKeyringStore:
    """Tests for get_keyring_store function."""

    def test_get_keyring_store_singleton(self, mock_keyring: MagicMock):
        """Test that get_keyring_store returns the same instance."""
        from pharos_cli.config import keyring_store as ks_module

        # Reset the global store
        original_store = ks_module._keyring_store
        ks_module._keyring_store = None

        try:
            with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring):
                from pharos_cli.config.keyring_store import get_keyring_store, KeyringStore

                store1 = get_keyring_store()
                store2 = get_keyring_store()

                assert isinstance(store1, KeyringStore)
                assert store1 is store2
        finally:
            # Restore original store
            ks_module._keyring_store = original_store


class TestKeyringStoreIntegration:
    """Integration tests for KeyringStore with real keyring (if available)."""

    def test_service_name_default(self):
        """Test default service name."""
        from pharos_cli.config.keyring_store import KeyringStore, SERVICE_NAME

        store = KeyringStore()
        assert store.service_name == SERVICE_NAME
        assert SERVICE_NAME == "pharos-cli"

    def test_custom_service_name(self):
        """Test custom service name."""
        from pharos_cli.config.keyring_store import KeyringStore

        store = KeyringStore(service_name="my-app")
        assert store.service_name == "my-app"

    def test_credential_name_format(self):
        """Test credential name format is consistent."""
        from pharos_cli.config.keyring_store import KeyringStore

        store = KeyringStore()

        # Test various profile names
        test_cases = [
            ("default", "pharos-default"),
            ("prod", "pharos-prod"),
            ("dev-environment", "pharos-dev-environment"),
            ("profile.with.dots", "pharos-profile.with.dots"),
        ]

        for profile_name, expected in test_cases:
            result = store._get_credential_name(profile_name)
            assert result == expected, f"Expected {expected}, got {result}"


class TestKeyringStoreEdgeCases:
    """Edge case tests for KeyringStore."""

    @pytest.fixture
    def mock_keyring(self) -> Generator[MagicMock, None, None]:
        """Create a mock keyring module."""
        import keyring.errors
        
        mock = MagicMock()
        mock.errors = keyring.errors
        mock.get_password.return_value = None
        mock.set_password.return_value = None
        mock.delete_password.return_value = None
        yield mock

    def test_set_api_key_with_special_characters(self, mock_keyring: MagicMock):
        """Test storing API key with special characters."""
        special_key = "sk-abc123!@#$%^&*()_+-=[]{}|;':\",./<>?"

        with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring):
            from pharos_cli.config.keyring_store import KeyringStore

            store = KeyringStore(service_name="pharos-cli-test")
            store.set_api_key("default", special_key)

            mock_keyring.set_password.assert_called_once_with(
                service_name="pharos-cli-test",
                username="pharos-default",
                password=special_key,
            )

    def test_set_api_key_with_empty_key(self, mock_keyring: MagicMock):
        """Test storing empty API key."""
        with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring):
            from pharos_cli.config.keyring_store import KeyringStore

            store = KeyringStore(service_name="pharos-cli-test")
            store.set_api_key("default", "")

            mock_keyring.set_password.assert_called_once_with(
                service_name="pharos-cli-test",
                username="pharos-default",
                password="",
            )

    def test_get_api_key_with_unicode(self, mock_keyring: MagicMock):
        """Test retrieving API key with unicode characters."""
        unicode_key = "sk-密钥测试🔑"
        mock_keyring.get_password.return_value = unicode_key

        with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring):
            from pharos_cli.config.keyring_store import KeyringStore

            store = KeyringStore(service_name="pharos-cli-test")
            result = store.get_api_key("default")

            assert result == unicode_key

    def test_delete_api_key_with_nonexistent_credential(self, mock_keyring: MagicMock):
        """Test deleting a credential that doesn't exist returns False."""
        mock_keyring.get_password.return_value = None

        with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring):
            from pharos_cli.config.keyring_store import KeyringStore

            store = KeyringStore(service_name="pharos-cli-test")
            result = store.delete_api_key("nonexistent")

            assert result is False
            mock_keyring.delete_password.assert_not_called()

    def test_set_api_key_unexpected_exception(self, mock_keyring: MagicMock):
        """Test handling of unexpected exceptions when setting API key."""
        mock_keyring.set_password.side_effect = RuntimeError("Unexpected error")

        with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring):
            from pharos_cli.config.keyring_store import KeyringStore, KeyringStorageError

            store = KeyringStore(service_name="pharos-cli-test")

            with pytest.raises(KeyringStorageError) as exc_info:
                store.set_api_key("default", "test-key")

            assert "Unexpected error" in str(exc_info.value)

    def test_get_api_key_unexpected_exception(self, mock_keyring: MagicMock):
        """Test handling of unexpected exceptions when getting API key."""
        mock_keyring.get_password.side_effect = RuntimeError("Unexpected error")

        with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring):
            from pharos_cli.config.keyring_store import KeyringStore, KeyringStorageError

            store = KeyringStore(service_name="pharos-cli-test")

            with pytest.raises(KeyringStorageError) as exc_info:
                store.get_api_key("default")

            assert "Unexpected error" in str(exc_info.value)

    def test_delete_api_key_unexpected_exception(self, mock_keyring: MagicMock):
        """Test handling of unexpected exceptions when deleting API key."""
        mock_keyring.get_password.return_value = "existing-key"
        mock_keyring.delete_password.side_effect = RuntimeError("Unexpected error")

        with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring):
            from pharos_cli.config.keyring_store import KeyringStore, KeyringDeleteError

            store = KeyringStore(service_name="pharos-cli-test")

            with pytest.raises(KeyringDeleteError) as exc_info:
                store.delete_api_key("default")

            assert "Unexpected error" in str(exc_info.value)