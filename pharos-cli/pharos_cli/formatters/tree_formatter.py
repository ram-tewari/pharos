"""Tree formatter for Pharos CLI."""

from typing import Any, List, Dict, Optional
from rich.tree import Tree
from rich.text import Text
from rich.console import Console
from rich.style import Style
from rich.color import Color

from pharos_cli.formatters.base import Formatter
from pharos_cli.utils.console import get_console


class TreeFormatter(Formatter):
    """Tree output formatter for hierarchical data using Rich."""

    # Color scheme for different node types
    COLORS = {
        "root": "bold magenta",
        "branch": "bold blue",
        "leaf": "green",
        "key": "cyan",
        "value": "white",
        "error": "red",
        "warning": "yellow",
        "number": "green",
        "boolean": "green",
        "null": "dim",
        "list_index": "yellow",
    }

    def __init__(
        self,
        console: Optional[Console] = None,
        show_keys: bool = True,
        show_values: bool = True,
        indent: int = 2,
        collapse_empty: bool = True,
        max_depth: Optional[int] = None,
    ):
        """Initialize the tree formatter.

        Args:
            console: Rich console instance (default: get_console())
            show_keys: Whether to show keys in the tree (default: True)
            show_values: Whether to show values in the tree (default: True)
            indent: Number of spaces for indentation (default: 2)
            collapse_empty: Whether to collapse empty containers (default: True)
            max_depth: Maximum depth to render (None for unlimited)
        """
        self.console = console or get_console()
        self.show_keys = show_keys
        self.show_values = show_values
        self.indent = indent
        self.collapse_empty = collapse_empty
        self.max_depth = max_depth

    def format(self, data: Any, label: str = "Root") -> str:
        """Format hierarchical data as a tree.

        Args:
            data: The hierarchical data to format (dict, list, or primitive)
            label: The label for the root node (default: "Root")

        Returns:
            Formatted tree as string
        """
        tree = Tree(label, style=self.COLORS["root"])
        self._build_tree(tree, data, depth=0)

        with self.console.capture() as capture:
            self.console.print(tree)

        return capture.get()

    def format_list(self, items: List[Dict]) -> str:
        """Format list of items as a tree.

        Args:
            items: List of dictionaries to format

        Returns:
            Formatted tree as string
        """
        if not items:
            return "No results found."

        if len(items) == 1:
            return self.format(items[0], "Item")

        tree = Tree(f"Items ({len(items)})", style=self.COLORS["root"])
        for i, item in enumerate(items):
            if isinstance(item, dict):
                label = str(item.get("id", item.get("title", f"[{i}]")))
                branch = tree.add(label, style=self.COLORS["branch"])
                self._build_tree(branch, item, depth=1)
            else:
                tree.add(str(item), style=self.COLORS["leaf"])

        with self.console.capture() as capture:
            self.console.print(tree)

        return capture.get()

    def format_error(self, error: Exception) -> str:
        """Format error as a tree.

        Args:
            error: The exception to format

        Returns:
            Formatted error as string
        """
        from rich.panel import Panel

        panel = Panel(
            f"[{self.COLORS['error']}]{error}[/{self.COLORS['error']}]",
            title="Error",
            border_style=self.COLORS["error"],
        )

        with self.console.capture() as capture:
            self.console.print(panel)

        return capture.get()

    def _build_tree(self, tree: Tree, data: Any, depth: int = 0) -> None:
        """Build the tree structure recursively.

        Args:
            tree: The Rich Tree to build
            data: The data to add to the tree
            depth: Current recursion depth
        """
        # Check max depth
        if self.max_depth is not None and depth >= self.max_depth:
            if data is not None:
                tree.add(self._format_value(data))
            return

        if data is None:
            return

        if isinstance(data, dict):
            self._build_dict(tree, data, depth)
        elif isinstance(data, list):
            self._build_list(tree, data, depth)
        elif isinstance(data, (tuple, set)):
            # Convert to list for display
            self._build_list(tree, list(data), depth)
        else:
            # Primitive value
            tree.add(self._format_value(data))

    def _build_dict(self, tree: Tree, data: Dict, depth: int) -> None:
        """Build tree from dictionary.

        Args:
            tree: The Rich Tree to add to
            data: The dictionary to process
            depth: Current recursion depth
        """
        for key, value in data.items():
            if isinstance(value, (dict, list)) and value:
                # Non-empty container - create a branch
                key_text = Text(str(key), style=self.COLORS["key"])
                branch = tree.add(key_text, style=self.COLORS["branch"])
                self._build_tree(branch, value, depth + 1)
            elif self.collapse_empty and isinstance(value, (dict, list)) and not value:
                # Empty container - show as collapsed
                key_text = Text(str(key), style=self.COLORS["key"])
                tree.add(f"{key_text}: [empty]", style=self.COLORS["null"])
            elif self.show_values and value is not None:
                # Leaf value
                key_text = Text(str(key), style=self.COLORS["key"])
                value_text = self._format_value(value)
                tree.add(f"{key_text}: {value_text}")
            elif self.show_keys:
                # Key only (no value)
                key_text = Text(str(key), style=self.COLORS["key"])
                tree.add(key_text)

    def _build_list(self, tree: Tree, data: List, depth: int) -> None:
        """Build tree from list.

        Args:
            tree: The Rich Tree to add to
            data: The list to process
            depth: Current recursion depth
        """
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)) and item:
                # Non-empty container
                index_text = Text(f"[{i}]", style=self.COLORS["list_index"])
                branch = tree.add(index_text, style=self.COLORS["branch"])
                self._build_tree(branch, item, depth + 1)
            elif self.collapse_empty and isinstance(item, (dict, list)) and not item:
                # Empty container
                index_text = Text(f"[{i}]", style=self.COLORS["list_index"])
                tree.add(f"{index_text}: [empty]", style=self.COLORS["null"])
            else:
                # Leaf item
                index_text = Text(f"[{i}]", style=self.COLORS["list_index"])
                tree.add(f"{index_text} {self._format_value(item)}", style=self.COLORS["leaf"])

    def _format_value(self, value: Any) -> str:
        """Format a value for display in the tree.

        Args:
            value: The value to format

        Returns:
            Formatted value string with Rich markup
        """
        if value is None:
            return f"[{self.COLORS['null']}]null[/{self.COLORS['null']}]"
        elif isinstance(value, bool):
            return f"[{self.COLORS['boolean']}]{value}[/{self.COLORS['boolean']}]"
        elif isinstance(value, (int, float)):
            formatted = str(value)
            if isinstance(value, float):
                # Limit decimal places
                if abs(value) < 0.01 and value != 0:
                    formatted = f"{value:.2e}"
                else:
                    formatted = f"{value:.4f}".rstrip("0").rstrip(".")
            return f"[{self.COLORS['number']}]{formatted}[/{self.COLORS['number']}]"
        elif isinstance(value, str):
            # Escape Rich markup
            escaped = value.replace("[", "\\[").replace("]", "\\]")
            # Truncate long strings
            if len(escaped) > 100:
                escaped = escaped[:97] + "..."
            return f"[{self.COLORS['value']}]{escaped}[/{self.COLORS['value']}]"
        else:
            # Fallback for other types
            escaped = str(value).replace("[", "\\[").replace("]", "\\]")
            return f"[{self.COLORS['value']}]{escaped}[/{self.COLORS['value']}]"

    def format_with_style(
        self,
        data: Any,
        label: str = "Root",
        root_style: Optional[str] = None,
        branch_style: Optional[str] = None,
        leaf_style: Optional[str] = None,
    ) -> str:
        """Format data as tree with custom styles.

        Args:
            data: The hierarchical data to format
            label: The label for the root node
            root_style: Custom style for root node
            branch_style: Custom style for branch nodes
            leaf_style: Custom style for leaf nodes

        Returns:
            Formatted tree as string
        """
        # Save original styles
        original_root = self.COLORS["root"]
        original_branch = self.COLORS["branch"]
        original_leaf = self.COLORS["leaf"]

        # Apply custom styles
        if root_style:
            self.COLORS["root"] = root_style
        if branch_style:
            self.COLORS["branch"] = branch_style
        if leaf_style:
            self.COLORS["leaf"] = leaf_style

        try:
            result = self.format(data, label)
        finally:
            # Restore original styles
            self.COLORS["root"] = original_root
            self.COLORS["branch"] = original_branch
            self.COLORS["leaf"] = original_leaf

        return result

    def format_resource_tree(self, resource: Dict) -> str:
        """Format a resource as a tree with common fields highlighted.

        Args:
            resource: The resource dictionary

        Returns:
            Formatted tree as string
        """
        tree = Tree("Resource", style=self.COLORS["root"])

        # Add common fields with special styling
        for key, value in resource.items():
            if key in ("id", "title", "type", "quality_score"):
                key_text = Text(str(key), style="bold yellow")
                value_text = self._format_value(value)
                tree.add(f"{key_text}: {value_text}")
            elif isinstance(value, (dict, list)) and value:
                key_text = Text(str(key), style=self.COLORS["key"])
                branch = tree.add(key_text, style=self.COLORS["branch"])
                self._build_tree(branch, value, depth=1)
            else:
                key_text = Text(str(key), style=self.COLORS["key"])
                tree.add(f"{key_text}: {self._format_value(value)}")

        with self.console.capture() as capture:
            self.console.print(tree)

        return capture.get()

    def format_collection_tree(self, collection: Dict, resources: List[Dict] = None) -> str:
        """Format a collection as a tree with optional resources.

        Args:
            collection: The collection dictionary
            resources: Optional list of resources in the collection

        Returns:
            Formatted tree as string
        """
        tree = Tree(f"Collection: {collection.get('name', 'Unknown')}", style=self.COLORS["root"])

        # Collection metadata
        meta_branch = tree.add("Metadata", style=self.COLORS["branch"])
        for key, value in collection.items():
            if key != "name":
                meta_branch.add(f"{key}: {self._format_value(value)}")

        # Resources if provided
        if resources:
            resources_branch = tree.add(f"Resources ({len(resources)})", style=self.COLORS["branch"])
            for i, resource in enumerate(resources):
                res_label = resource.get("title", resource.get("id", f"[{i}]"))
                res_branch = resources_branch.add(res_label, style=self.COLORS["branch"])
                # Show key fields
                for key, value in list(resource.items())[:5]:  # Limit to 5 fields
                    res_branch.add(f"{key}: {self._format_value(value)}")

        with self.console.capture() as capture:
            self.console.print(tree)

        return capture.get()