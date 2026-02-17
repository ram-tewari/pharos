"""JSON formatter for Pharos CLI."""

import json
from typing import Any, List, Dict

from pharos_cli.formatters.base import Formatter


class JSONFormatter(Formatter):
    """JSON output formatter."""

    def __init__(self, indent: int = 2):
        self.indent = indent

    def format(self, data: Any) -> str:
        """Format data as JSON."""
        return json.dumps(data, indent=self.indent, default=str, ensure_ascii=False)

    def format_list(self, items: List[Dict]) -> str:
        """Format list of items as JSON."""
        return self.format(items)

    def format_error(self, error: Exception) -> str:
        """Format error as JSON."""
        return json.dumps(
            {
                "error": str(error),
                "type": type(error).__name__,
            },
            indent=self.indent,
        )