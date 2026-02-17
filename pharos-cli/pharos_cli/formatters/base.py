"""Base formatter interface for Pharos CLI."""

from abc import ABC, abstractmethod
from typing import Any, List, Dict


class Formatter(ABC):
    """Base formatter interface."""

    @abstractmethod
    def format(self, data: Any) -> str:
        """Format data for output."""
        pass

    @abstractmethod
    def format_list(self, items: List[Dict]) -> str:
        """Format list of items."""
        pass

    @abstractmethod
    def format_error(self, error: Exception) -> str:
        """Format error message."""
        pass


def get_formatter(format_type: str) -> Formatter:
    """Get formatter by type."""
    from pharos_cli.formatters.json_formatter import JSONFormatter
    from pharos_cli.formatters.table_formatter import TableFormatter
    from pharos_cli.formatters.tree_formatter import TreeFormatter
    from pharos_cli.formatters.csv_formatter import CSVFormatter

    formatters = {
        "json": JSONFormatter(),
        "table": TableFormatter(),
        "tree": TreeFormatter(),
        "csv": CSVFormatter(),
    }

    return formatters.get(format_type, TableFormatter())