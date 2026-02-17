"""Pytest configuration and fixtures for Pharos CLI tests."""

import pytest
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from typing import Generator, List, Dict, Any
import sys
from pathlib import Path


@pytest.fixture
def runner() -> Generator[CliRunner, None, None]:
    """Create a CLI runner for testing commands."""
    yield CliRunner()


@pytest.fixture
def mock_api_client() -> Generator[MagicMock, None, None]:
    """Create a mock API client for testing."""
    mock = MagicMock()
    mock.get.return_value = {}
    mock.post.return_value = {}
    mock.put.return_value = {}
    mock.delete.return_value = {}
    return mock


@pytest.fixture
def sample_resources() -> List[Dict[str, Any]]:
    """Create sample resources for testing formatters."""
    return [
        {"id": 1, "title": "Resource 1", "type": "paper", "quality_score": 0.85},
        {"id": 2, "title": "Resource 2", "type": "code", "quality_score": 0.72},
        {"id": 3, "title": "Resource 3", "type": "documentation", "quality_score": 0.91},
    ]


@pytest.fixture
def mock_keyring_module() -> Generator[MagicMock, None, None]:
    """Create a mock keyring module for testing."""
    import keyring.errors
    
    mock = MagicMock()
    # Properly set up the errors attribute to use real exception classes
    mock.errors = keyring.errors
    
    # Set up default return values
    mock.get_password.return_value = None
    mock.set_password.return_value = None
    mock.delete_password.return_value = None
    
    return mock


@pytest.fixture
def patched_keyring(mock_keyring_module: MagicMock) -> Generator[MagicMock, None, None]:
    """Patch the keyring module for testing.
    
    This fixture patches the keyring module at the module level
    to ensure all imports use the mock.
    """
    with patch("pharos_cli.config.keyring_store._get_keyring", return_value=mock_keyring_module):
        yield mock_keyring_module