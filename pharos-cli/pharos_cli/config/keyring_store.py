"""Secure credential storage using keyring library."""

from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass

from pharos_cli.utils.console import get_console

if TYPE_CHECKING:
    import keyring as KeyringModule

# Service name for keyring
SERVICE_NAME = "pharos-cli"


def _get_keyring() -> "KeyringModule":
    """Get the keyring module.

    This function exists to allow mocking in tests.
    Uses dynamic import to support mocking.
    """
    import keyring
    return keyring


@dataclass
class KeyringCredentials:
    """Represents stored credentials."""

    profile_name: str
    api_key: Optional[str] = None

    def is_stored(self) -> bool:
        """Check if credentials are stored."""
        return self.api_key is not None


class KeyringError(Exception):
    """Base exception for keyring operations."""

    def __init__(self, message: str, profile_name: str = None):
        self.profile_name = profile_name
        super().__init__(message)


class KeyringNotAvailableError(KeyringError):
    """Raised when keyring is not available."""

    def __init__(self, profile_name: str = None):
        message = "Keyring backend is not available on this system"
        super().__init__(message, profile_name)


class KeyringStorageError(KeyringError):
    """Raised when keyring storage operation fails."""

    def __init__(self, message: str, profile_name: str = None):
        super().__init__(message, profile_name)


class KeyringDeleteError(KeyringError):
    """Raised when deleting credentials fails."""

    def __init__(self, message: str, profile_name: str = None):
        super().__init__(message, profile_name)


class KeyringStore:
    """
    Secure credential storage using the system keyring.

    This class provides a secure way to store and retrieve API keys
    using the system's native credential storage mechanism:
    - macOS: Keychain
    - Linux: SecretService (GNOME Keyring, KWallet)
    - Windows: Credential Manager

    Attributes:
        service_name: The service name used in the keyring.
    """

    def __init__(self, service_name: str = SERVICE_NAME):
        """Initialize the keyring store.

        Args:
            service_name: The service name for credential storage.
        """
        self.service_name = service_name

    def _get_credential_name(self, profile_name: str) -> str:
        """Get the credential name for a profile.

        Args:
            profile_name: The profile name.

        Returns:
            The credential name for the keyring.
        """
        return f"pharos-{profile_name}"

    def set_api_key(self, profile_name: str, api_key: str) -> None:
        """Store an API key securely in the keyring.

        Args:
            profile_name: The profile name to store the key for.
            api_key: The API key to store.

        Raises:
            KeyringNotAvailableError: If keyring is not available.
            KeyringStorageError: If storage operation fails.
        """
        credential_name = self._get_credential_name(profile_name)
        kr = _get_keyring()

        try:
            kr.set_password(
                service_name=self.service_name,
                username=credential_name,
                password=api_key,
            )
        except Exception as e:
            # Check if it's a keyring error by class name
            if 'KeyringError' in type(e).__name__ or 'keyring.errors' in str(type(e).__module__):
                console = get_console()
                console.print(f"[yellow]Warning:[/yellow] Could not store API key: {e}")
                raise KeyringStorageError(
                    f"Failed to store API key for profile '{profile_name}': {e}",
                    profile_name,
                )
            # Re-raise as storage error for any other exception
            console = get_console()
            console.print(f"[yellow]Warning:[/yellow] Unexpected keyring error: {e}")
            raise KeyringStorageError(
                f"Unexpected error storing API key for profile '{profile_name}': {e}",
                profile_name,
            )

    def get_api_key(self, profile_name: str) -> Optional[str]:
        """Retrieve an API key from the keyring.

        Args:
            profile_name: The profile name to retrieve the key for.

        Returns:
            The API key if found, None otherwise.

        Raises:
            KeyringNotAvailableError: If keyring is not available.
            KeyringError: If retrieval operation fails.
        """
        credential_name = self._get_credential_name(profile_name)
        kr = _get_keyring()

        try:
            api_key = kr.get_password(
                service_name=self.service_name,
                username=credential_name,
            )
            return api_key
        except Exception as e:
            # Check if it's a keyring error by class name
            if 'KeyringError' in type(e).__name__ or 'keyring.errors' in str(type(e).__module__):
                console = get_console()
                console.print(f"[yellow]Warning:[/yellow] Could not retrieve API key: {e}")
                raise KeyringStorageError(
                    f"Failed to retrieve API key for profile '{profile_name}': {e}",
                    profile_name,
                )
            # Re-raise as storage error for any other exception
            console = get_console()
            console.print(f"[yellow]Warning:[/yellow] Unexpected keyring error: {e}")
            raise KeyringStorageError(
                f"Unexpected error retrieving API key for profile '{profile_name}': {e}",
                profile_name,
            )

    def delete_api_key(self, profile_name: str) -> bool:
        """Delete an API key from the keyring.

        Args:
            profile_name: The profile name to delete the key for.

        Returns:
            True if the key was deleted, False if it didn't exist.

        Raises:
            KeyringDeleteError: If deletion operation fails.
        """
        credential_name = self._get_credential_name(profile_name)
        kr = _get_keyring()

        try:
            # Check if the credential exists first
            existing = kr.get_password(
                service_name=self.service_name,
                username=credential_name,
            )

            if existing is None:
                return False

            # Delete the credential
            kr.delete_password(
                service_name=self.service_name,
                username=credential_name,
            )
            return True

        except Exception as e:
            # Check if it's a keyring error by class name
            if 'KeyringError' in type(e).__name__ or 'DeleteError' in type(e).__name__ or 'keyring.errors' in str(type(e).__module__):
                console = get_console()
                console.print(f"[yellow]Warning:[/yellow] Could not delete API key: {e}")
                raise KeyringDeleteError(
                    f"Failed to delete API key for profile '{profile_name}': {e}",
                    profile_name,
                )
            # Re-raise as delete error for any other exception
            console = get_console()
            console.print(f"[yellow]Warning:[/yellow] Unexpected keyring error: {e}")
            raise KeyringDeleteError(
                f"Unexpected error deleting API key for profile '{profile_name}': {e}",
                profile_name,
            )

    def has_api_key(self, profile_name: str) -> bool:
        """Check if an API key is stored for a profile.

        Args:
            profile_name: The profile name to check.

        Returns:
            True if an API key is stored, False otherwise.
        """
        try:
            api_key = self.get_api_key(profile_name)
            return api_key is not None
        except KeyringError:
            return False

    def get_credentials(self, profile_name: str) -> KeyringCredentials:
        """Get credentials for a profile.

        Args:
            profile_name: The profile name to get credentials for.

        Returns:
            KeyringCredentials with the API key if stored.
        """
        api_key = self.get_api_key(profile_name)
        return KeyringCredentials(profile_name=profile_name, api_key=api_key)

    def clear_all(self) -> int:
        """Clear all stored credentials for this service.

        Returns:
            The number of credentials deleted.
        """
        # Note: This is a best-effort operation as keyring doesn't
        # provide a way to list all credentials
        deleted = 0
        console = get_console()
        console.print(
            "[yellow]Note:[/yellow] Cannot enumerate keyring credentials. "
            "Please remove manually via system keyring manager."
        )
        return deleted


# Global keyring store instance
_keyring_store: Optional[KeyringStore] = None


def get_keyring_store() -> KeyringStore:
    """Get the global keyring store instance.

    Returns:
        The global KeyringStore instance.
    """
    global _keyring_store
    if _keyring_store is None:
        _keyring_store = KeyringStore()
    return _keyring_store