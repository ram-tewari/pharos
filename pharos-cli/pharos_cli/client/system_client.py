"""System client for Pharos CLI - health, stats, and backup operations."""

import json
import time
from typing import Any, Dict, Optional
from pathlib import Path

import httpx

from pharos_cli.client.api_client import SyncAPIClient
from pharos_cli.client.exceptions import APIError, NetworkError


class SystemClient:
    """Client for system operations: health, stats, backup, restore."""

    def __init__(self, api_client: SyncAPIClient):
        """Initialize the system client.
        
        Args:
            api_client: The sync API client for making HTTP requests.
        """
        self.api = api_client

    def health_check(self) -> Dict[str, Any]:
        """Check the health of the Pharos API.
        
        Returns:
            Dict containing health status information.
            
        Raises:
            APIError: If the API returns an error.
            NetworkError: If there's a network issue.
        """
        try:
            return self.api.get("/api/v1/health")
        except APIError as e:
            # Return a structured error response
            return {
                "status": "error",
                "message": e.message,
                "status_code": e.status_code,
            }
        except Exception as e:
            # Return a structured error response for other exceptions
            return {
                "status": "error",
                "message": str(e),
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics.
        
        Returns:
            Dict containing system statistics.
            
        Raises:
            APIError: If the API returns an error.
            NetworkError: If there's a network issue.
        """
        return self.api.get("/api/v1/stats")

    def get_version(self) -> Dict[str, Any]:
        """Get version information.
        
        Returns:
            Dict containing version information.
            
        Raises:
            APIError: If the API returns an error.
            NetworkError: If there's a network issue.
        """
        return self.api.get("/api/v1/version")

    def backup_create(self, output_path: Path) -> Dict[str, Any]:
        """Create a backup of the database.
        
        Args:
            output_path: Path where the backup file will be saved.
            
        Returns:
            Dict containing backup information.
            
        Raises:
            APIError: If the API returns an error.
            NetworkError: If there's a network issue.
            IOError: If the backup file cannot be written.
        """
        # Request backup from API
        response = self.api.post("/api/v1/system/backup")
        
        # The API should return the backup data
        if isinstance(response, dict) and "data" in response:
            backup_data = response["data"]
        else:
            backup_data = response
        
        # Write backup to file
        if isinstance(backup_data, str):
            # Backup is returned as a string (JSON or SQL)
            content = backup_data
        else:
            # Backup is returned as a dict, serialize to JSON
            content = json.dumps(backup_data, indent=2, default=str)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write backup file
        output_path.write_text(content, encoding="utf-8")
        
        return {
            "status": "success",
            "file_path": str(output_path),
            "size_bytes": len(content),
        }

    def backup_verify(self, backup_path: Path) -> Dict[str, Any]:
        """Verify a backup file.
        
        Args:
            backup_path: Path to the backup file.
            
        Returns:
            Dict containing verification result.
        """
        result = {
            "file_path": str(backup_path),
            "exists": False,
            "valid": False,
            "size_bytes": 0,
            "error": None,
        }
        
        try:
            # Check if file exists
            if not backup_path.exists():
                result["error"] = "Backup file not found"
                return result
            
            result["exists"] = True
            
            # Get file size
            result["size_bytes"] = backup_path.stat().st_size
            
            # Try to parse as JSON
            content = backup_path.read_text(encoding="utf-8")
            
            try:
                json.loads(content)
                result["valid"] = True
                result["format"] = "json"
            except json.JSONDecodeError:
                # Check if it's valid SQL
                if content.strip().upper().startswith("BEGIN") or "CREATE TABLE" in content.upper():
                    result["valid"] = True
                    result["format"] = "sql"
                else:
                    result["error"] = "Invalid backup format"
            
            return result
            
        except IOError as e:
            result["error"] = f"Could not read backup file: {e}"
            return result
        except Exception as e:
            result["error"] = f"Verification failed: {e}"
            return result

    def restore(self, backup_path: Path) -> Dict[str, Any]:
        """Restore the database from a backup file.
        
        Args:
            backup_path: Path to the backup file.
            
        Returns:
            Dict containing restore result.
            
        Raises:
            APIError: If the API returns an error.
            NetworkError: If there's a network issue.
            IOError: If the backup file cannot be read.
        """
        # Read backup file
        if not backup_path.exists():
            raise IOError(f"Backup file not found: {backup_path}")
        
        content = backup_path.read_text(encoding="utf-8")
        
        # Try to parse as JSON first
        try:
            data = json.loads(content)
            # Send as JSON
            return self.api.post("/api/v1/system/restore", json=data)
        except json.JSONDecodeError:
            # Send as raw SQL
            return self.api.post("/api/v1/system/restore", data=content)

    def clear_cache(self) -> Dict[str, Any]:
        """Clear the system cache.
        
        Returns:
            Dict containing cache clear result.
            
        Raises:
            APIError: If the API returns an error.
            NetworkError: If there's a network issue.
        """
        return self.api.post("/api/v1/system/cache/clear")

    def run_migrations(self) -> Dict[str, Any]:
        """Run database migrations.
        
        Returns:
            Dict containing migration result.
            
        Raises:
            APIError: If the API returns an error.
            NetworkError: If there's a network issue.
        """
        return self.api.post("/api/v1/system/migrate")