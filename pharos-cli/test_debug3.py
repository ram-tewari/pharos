"""Test to debug the issue."""
import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add pharos_cli to path
sys.path.insert(0, str(Path(__file__).parent))

def test_set_api_key_failure():
    """Test handling of keyring errors when setting API key."""
    import keyring.errors
    
    mock_keyring = MagicMock()
    mock_keyring.errors = keyring.errors
    mock_keyring.set_password.side_effect = keyring.errors.KeyringError("Storage error")

    with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring):
        from pharos_cli.config.keyring_store import KeyringStore, KeyringStorageError

        store = KeyringStore(service_name="pharos-cli-test")

        try:
            store.set_api_key("default", "test-key")
            print("NO EXCEPTION RAISED!")
        except KeyringStorageError as exc:
            print(f"SUCCESS: {exc}")
            assert "default" in str(exc)
            assert "Storage error" in str(exc)

if __name__ == "__main__":
    test_set_api_key_failure()
