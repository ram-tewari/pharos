from unittest.mock import MagicMock, patch
import keyring.errors

mock = MagicMock()
mock.errors = keyring.errors
mock.set_password.side_effect = keyring.errors.KeyringError("Storage error")

with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock):
    from pharos_cli.config.keyring_store import KeyringStore, KeyringStorageError
    
    store = KeyringStore(service_name="pharos-cli-test")
    
    try:
        store.set_api_key("default", "test-key")
        print("NO EXCEPTION RAISED!")
    except KeyringStorageError as e:
        print(f"SUCCESS: Caught KeyringStorageError: {e}")
    except Exception as e:
        print(f"ERROR: Caught unexpected exception: {type(e).__name__}: {e}")
