"""Resource commands for Pharos CLI."""

import sys
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

import typer
from rich import print
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.console import Console

from pharos_cli.client.api_client import get_api_client
from pharos_cli.client.resource_client import ResourceClient
from pharos_cli.client.exceptions import ResourceNotFoundError, APIError, NetworkError
from pharos_cli.config.settings import load_config, apply_env_overrides
from pharos_cli.formatters.base import get_formatter
from pharos_cli.utils.console import get_console
from pharos_cli.utils.validators import validate_file_path, validate_url, validate_limit, validate_per_page
from pharos_cli.utils.helpers import format_score, truncate, format_duration, format_number


class ImportStrategy(str, Enum):
    """Strategy for handling duplicate resources during import."""
    SKIP = "skip"
    OVERWRITE = "overwrite"
    FAIL = "fail"


@dataclass
class ImportResult:
    """Result of importing a single file."""
    file_path: Path
    success: bool
    resource_id: Optional[int] = None
    error: Optional[str] = None


@dataclass
class ExportResult:
    """Result of exporting a resource."""
    resource_id: int
    success: bool
    file_path: Optional[Path] = None
    error: Optional[str] = None

resource_app = typer.Typer(
    name="resource",
    help="Resource management commands for Pharos CLI",
)


def get_resource_client() -> ResourceClient:
    """Get a ResourceClient instance."""
    config = load_config()
    api_client = get_api_client(config)
    return ResourceClient(api_client)


@resource_app.command("add")
def add_resource(
    file: Optional[Path] = typer.Argument(
        None,
        help="File path to add as a resource",
        exists=False,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    url: Optional[str] = typer.Option(
        None,
        "--url",
        "-u",
        help="URL to add as a resource",
    ),
    title: Optional[str] = typer.Option(
        None,
        "--title",
        "-t",
        help="Title for the resource (auto-detected from file/URL if not provided)",
    ),
    resource_type: Optional[str] = typer.Option(
        None,
        "--type",
        "-T",
        help="Resource type (code, paper, documentation, article, book, video, audio, image, archive, other)",
    ),
    language: Optional[str] = typer.Option(
        None,
        "--language",
        "-l",
        help="Programming language or natural language",
    ),
    stdin: bool = typer.Option(
        False,
        "--stdin",
        "-s",
        help="Read content from stdin",
    ),
    content: Optional[str] = typer.Option(
        None,
        "--content",
        "-c",
        help="Content directly (for small text resources)",
    ),
) -> None:
    """Add a new resource from file, URL, or stdin.

    Examples:
        pharos resource add ./myfile.py
        pharos resource add ./myfile.py --type code --language python
        pharos resource add --url https://example.com/paper.pdf --type paper
        cat file.txt | pharos resource add --stdin --title "My Note"
    """
    console = get_console()

    # Handle stdin input first - check if stdin flag is set and has content
    stdin_content = None
    if stdin:
        stdin_content = sys.stdin.read()
        if not stdin_content:
            console.print("[red]Error:[/red] No content received from stdin")
            raise typer.Exit(1)

    # Validate input sources (stdin only counts if it has content)
    input_sources = [file, url, content]
    if stdin_content is not None:
        input_sources.append("stdin")  # stdin with content counts as input
    input_count = sum(1 for x in input_sources if x is not None and x != "stdin")
    if stdin_content is not None:
        input_count += 1

    if input_count == 0:
        console.print("[red]Error:[/red] Must specify --file, --url, --stdin, or --content")
        console.print("Use 'pharos resource add --help' for usage information")
        raise typer.Exit(1)

    if input_count > 1:
        console.print("[red]Error:[/red] Cannot specify multiple input sources (file, url, stdin, content)")
        raise typer.Exit(1)

    # Handle stdin input
    if stdin_content is not None:
        resource_content = stdin_content

        if title is None:
            title = "Stdin Input"

        # Auto-detect type for stdin
        if resource_type is None:
            # Check if it looks like code
            code_indicators = ["def ", "class ", "import ", "from ", "function ", "const ", "let ", "var "]
            if any(indicator in resource_content for indicator in code_indicators):
                resource_type = "code"
            else:
                resource_type = "documentation"

        # Auto-detect language for stdin
        if language is None:
            if resource_type == "code":
                # Try to detect language from content
                if "def " in resource_content or "import " in resource_content or "from " in resource_content:
                    language = "python"
                elif "function " in resource_content or "const " in resource_content:
                    language = "javascript"
                elif "class " in resource_content and "{" in resource_content:
                    language = "java"

        try:
            client = get_resource_client()
            result = client.create(
                title=title,
                content=resource_content,
                resource_type=resource_type,
                language=language,
            )
            console.print(f"[green]Resource created successfully![/green]")
            console.print(f"  ID: {result['id']}")
            console.print(f"  Title: {result['title']}")
            if result.get('resource_type'):
                console.print(f"  Type: {result['resource_type']}")
            if result.get('language'):
                console.print(f"  Language: {result['language']}")
        except APIError as e:
            console.print(f"[red]API Error:[/red] {e.message}")
            raise typer.Exit(1)
        except NetworkError as e:
            console.print(f"[red]Network Error:[/red] {e}")
            raise typer.Exit(1)
        return

    # Handle content option
    if content:
        if title is None:
            console.print("[red]Error:[/red] --title is required when using --content")
            raise typer.Exit(1)

        try:
            client = get_resource_client()
            result = client.create(
                title=title,
                content=content,
                resource_type=resource_type,
                language=language,
            )
            console.print(f"[green]Resource created successfully![/green]")
            console.print(f"  ID: {result['id']}")
            console.print(f"  Title: {result['title']}")
        except APIError as e:
            console.print(f"[red]API Error:[/red] {e.message}")
            raise typer.Exit(1)
        except NetworkError as e:
            console.print(f"[red]Network Error:[/red] {e}")
            raise typer.Exit(1)
        return

    # Handle file input
    if file:
        if not file.exists():
            console.print(f"[red]Error:[/red] File not found: {file}")
            raise typer.Exit(1)

        try:
            file_content = file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            console.print(f"[red]Error:[/red] Could not read file (not UTF-8 encoded): {file}")
            raise typer.Exit(1)
        except IOError as e:
            console.print(f"[red]Error:[/red] Could not read file: {e}")
            raise typer.Exit(1)

        # Auto-detect title from filename if not provided
        if title is None:
            title = file.stem.replace("_", " ").replace("-", " ").title()

        # Auto-detect type from extension if not provided
        if resource_type is None:
            code_extensions = {".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".cs", ".go", ".rs", ".rb", ".php"}
            doc_extensions = {".md", ".txt", ".rst", ".tex", ".pdf", ".html", ".xml", ".json", ".yaml", ".yml"}
            paper_extensions = {".pdf", ".ps", ".eps"}

            ext = file.suffix.lower()
            if ext in code_extensions:
                resource_type = "code"
            elif ext in doc_extensions:
                resource_type = "documentation"
            elif ext in paper_extensions:
                resource_type = "paper"
            else:
                resource_type = "code"  # Default to code for unknown extensions

        # Auto-detect language from extension if not provided
        if language is None and resource_type == "code":
            ext_to_language = {
                ".py": "python",
                ".js": "javascript",
                ".ts": "typescript",
                ".java": "java",
                ".c": "c",
                ".cpp": "cpp",
                ".h": "c",
                ".cs": "csharp",
                ".go": "go",
                ".rs": "rust",
                ".rb": "ruby",
                ".php": "php",
                ".swift": "swift",
                ".kt": "kotlin",
                ".scala": "scala",
                ".r": "r",
                ".jl": "julia",
                ".m": "matlab",
                ".sh": "shell",
                ".html": "html",
                ".css": "css",
                ".sql": "sql",
                ".md": "markdown",
                ".json": "json",
                ".yaml": "yaml",
                ".yml": "yaml",
                ".xml": "xml",
            }
            language = ext_to_language.get(file.suffix.lower())

        try:
            client = get_resource_client()
            result = client.create(
                title=title,
                content=file_content,
                resource_type=resource_type,
                language=language,
            )
            console.print(f"[green]Resource created successfully![/green]")
            console.print(f"  ID: {result['id']}")
            console.print(f"  Title: {result['title']}")
            if result.get('resource_type'):
                console.print(f"  Type: {result['resource_type']}")
            if result.get('language'):
                console.print(f"  Language: {result['language']}")
        except APIError as e:
            console.print(f"[red]API Error:[/red] {e.message}")
            raise typer.Exit(1)
        except NetworkError as e:
            console.print(f"[red]Network Error:[/red] {e}")
            raise typer.Exit(1)
        return

    # Handle URL input
    if url:
        if not validate_url(url):
            console.print(f"[red]Error:[/red] Invalid URL: {url}")
            raise typer.Exit(1)

        # Auto-detect title from URL if not provided
        if title is None:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                title = Path(parsed.path).stem.replace("_", " ").replace("-", " ").title()
                if not title:
                    title = parsed.netloc
            except Exception:
                title = "Resource from URL"

        try:
            client = get_resource_client()
            result = client.create(
                title=title,
                url=url,
                resource_type=resource_type or "paper",
            )
            console.print(f"[green]Resource created successfully![/green]")
            console.print(f"  ID: {result['id']}")
            console.print(f"  Title: {result['title']}")
            console.print(f"  URL: {url}")
        except APIError as e:
            console.print(f"[red]API Error:[/red] {e.message}")
            raise typer.Exit(1)
        except NetworkError as e:
            console.print(f"[red]Network Error:[/red] {e}")
            raise typer.Exit(1)
        return


@resource_app.command("list")
def list_resources(
    resource_type: Optional[str] = typer.Option(
        None,
        "--type",
        "-T",
        help="Filter by resource type (code, paper, documentation, article, book, video, audio, image, archive, other)",
    ),
    language: Optional[str] = typer.Option(
        None,
        "--language",
        "-l",
        help="Filter by programming language",
    ),
    query: Optional[str] = typer.Option(
        None,
        "--query",
        "-q",
        help="Search query for title/content",
    ),
    min_quality: Optional[float] = typer.Option(
        None,
        "--min-quality",
        help="Minimum quality score (0.0 to 1.0)",
    ),
    collection_id: Optional[int] = typer.Option(
        None,
        "--collection",
        "-c",
        help="Filter by collection ID",
    ),
    tags: Optional[str] = typer.Option(
        None,
        "--tags",
        help="Filter by tags (comma-separated)",
    ),
    page: int = typer.Option(
        1,
        "--page",
        "-p",
        help="Page number",
    ),
    per_page: int = typer.Option(
        25,
        "--per-page",
        help="Items per page (1-100)",
    ),
    output_format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format (json, table, csv, quiet)",
    ),
) -> None:
    """List resources with optional filters.

    Examples:
        pharos resource list
        pharos resource list --type code --language python
        pharos resource list --query "machine learning"
        pharos resource list --min-quality 0.8
        pharos resource list --tags important,python
    """
    console = get_console()

    # Validate pagination
    try:
        page = validate_per_page(page)
        per_page = validate_per_page(per_page)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Parse tags
    tag_list = None
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    try:
        client = get_resource_client()
        skip = (page - 1) * per_page

        result = client.list(
            skip=skip,
            limit=per_page,
            resource_type=resource_type,
            language=language,
            query=query,
            min_quality=min_quality,
            collection_id=collection_id,
            tags=tag_list,
        )

        # Format output
        formatter = get_formatter(output_format)

        if output_format == "quiet":
            # Just print IDs
            for item in result.items:
                print(item.get("id", ""))
        elif output_format == "json":
            output = {
                "items": result.items,
                "total": result.total,
                "page": result.page,
                "per_page": result.per_page,
                "has_more": result.has_more,
            }
            print(formatter.format(output))
        else:
            # Table or CSV
            if not result.items:
                console.print("[yellow]No resources found.[/yellow]")
                return

            # Add computed fields for display
            display_items = []
            for item in result.items:
                display_item = dict(item)
                # Format quality score
                if "quality_score" in display_item and display_item["quality_score"] is not None:
                    display_item["quality_score"] = format_score(display_item["quality_score"])
                display_items.append(display_item)

            print(formatter.format_list(display_items))

            # Show pagination info
            console.print(f"\n[dim]Showing {len(result.items)} of {result.total} resources[/dim]")
            if result.has_more:
                console.print(f"[dim]Use --page {page + 1} for next page[/dim]")

    except APIError as e:
        console.print(f"[red]API Error:[/red] {e.message}")
        raise typer.Exit(1)
    except NetworkError as e:
        console.print(f"[red]Network Error:[/red] {e}")
        raise typer.Exit(1)


@resource_app.command("get")
def get_resource(
    resource_id: int = typer.Argument(
        ...,
        help="Resource ID to retrieve",
    ),
    output_format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format (json, table, tree)",
    ),
    show_content: bool = typer.Option(
        False,
        "--content",
        help="Show resource content",
    ),
    content_lines: int = typer.Option(
        50,
        "--content-lines",
        help="Number of content lines to show",
    ),
) -> None:
    """Get resource details by ID.

    Examples:
        pharos resource get 1
        pharos resource get 1 --format json
        pharos resource get 1 --content
    """
    console = get_console()

    try:
        client = get_resource_client()
        resource = client.get(resource_id=resource_id)

        # Format output
        formatter = get_formatter(output_format)

        if output_format == "json":
            print(formatter.format(resource.model_dump()))
            return

        # Create display data
        display_data = {
            "ID": resource.id,
            "Title": resource.title,
            "Type": resource.resource_type or "-",
            "Language": resource.language or "-",
            "Quality Score": format_score(resource.quality_score) if resource.quality_score else "-",
            "URL": resource.url or "-",
            "Created At": resource.created_at or "-",
            "Updated At": resource.updated_at or "-",
        }

        # Add metadata if present
        if resource.metadata:
            display_data["Metadata"] = str(resource.metadata)

        if output_format == "tree":
            print(formatter.format({"Resource": display_data}))
        else:
            print(formatter.format(display_data))

        # Show content if requested
        if show_content and resource.content:
            console.print(f"\n[bold]Content:[/bold]")
            content = resource.content
            lines = content.split("\n")

            if len(lines) > content_lines:
                lines = lines[:content_lines]
                content = "\n".join(lines) + "\n... (truncated)"

            # Syntax highlight if it's code
            if resource.language and resource.resource_type == "code":
                syntax = Syntax(content, resource.language, theme="monokai", line_numbers=True)
                console.print(syntax)
            else:
                console.print(content)

    except ResourceNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except APIError as e:
        console.print(f"[red]API Error:[/red] {e.message}")
        raise typer.Exit(1)
    except NetworkError as e:
        console.print(f"[red]Network Error:[/red] {e}")
        raise typer.Exit(1)


@resource_app.command("update")
def update_resource(
    resource_id: int = typer.Argument(
        ...,
        help="Resource ID to update",
    ),
    title: Optional[str] = typer.Option(
        None,
        "--title",
        "-t",
        help="New title for the resource",
    ),
    content: Optional[str] = typer.Option(
        None,
        "--content",
        "-c",
        help="New content for the resource",
    ),
    resource_type: Optional[str] = typer.Option(
        None,
        "--type",
        "-T",
        help="New resource type",
    ),
    language: Optional[str] = typer.Option(
        None,
        "--language",
        "-l",
        help="New programming language",
    ),
) -> None:
    """Update resource metadata.

    Examples:
        pharos resource update 1 --title "New Title"
        pharos resource update 1 --type paper --language english
    """
    console = get_console()

    # Check if at least one update field is provided
    if all(x is None for x in [title, content, resource_type, language]):
        console.print("[red]Error:[/red] Must specify at least one field to update (--title, --content, --type, --language)")
        raise typer.Exit(1)

    try:
        client = get_resource_client()
        resource = client.update(
            resource_id=resource_id,
            title=title,
            content=content,
            resource_type=resource_type,
            language=language,
        )

        console.print(f"[green]Resource updated successfully![/green]")
        console.print(f"  ID: {resource.id}")
        console.print(f"  Title: {resource.title}")
        if resource.resource_type:
            console.print(f"  Type: {resource.resource_type}")
        if resource.language:
            console.print(f"  Language: {resource.language}")

    except ResourceNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except APIError as e:
        console.print(f"[red]API Error:[/red] {e.message}")
        raise typer.Exit(1)
    except NetworkError as e:
        console.print(f"[red]Network Error:[/red] {e}")
        raise typer.Exit(1)


@resource_app.command("delete")
def delete_resource(
    resource_id: int = typer.Argument(
        ...,
        help="Resource ID to delete",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt",
    ),
) -> None:
    """Delete a resource by ID.

    Examples:
        pharos resource delete 1
        pharos resource delete 1 --force
    """
    console = get_console()

    # Get resource info for confirmation
    try:
        client = get_resource_client()
        resource = client.get(resource_id=resource_id)
        resource_title = resource.title
    except ResourceNotFoundError:
        console.print(f"[red]Error:[/red] Resource {resource_id} not found")
        raise typer.Exit(1)
    except (APIError, NetworkError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Confirmation prompt
    if not force:
        console.print(Panel(
            f"[yellow]Are you sure you want to delete resource {resource_id}?[/yellow]\n\n"
            f"  Title: {resource_title}\n"
            f"  Type: {resource.resource_type or 'N/A'}\n\n"
            f"[red]This action cannot be undone![/red]",
            title="Confirm Deletion",
            border_style="red",
        ))

        if not typer.confirm("Do you want to continue?"):
            console.print("[yellow]Deletion cancelled.[/yellow]")
            raise typer.Exit(0)

    try:
        result = client.delete(resource_id=resource_id)
        console.print(f"[green]Resource {resource_id} deleted successfully![/green]")

    except ResourceNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except APIError as e:
        console.print(f"[red]API Error:[/red] {e.message}")
        raise typer.Exit(1)
    except NetworkError as e:
        console.print(f"[red]Network Error:[/red] {e}")
        raise typer.Exit(1)


@resource_app.command("quality")
def get_resource_quality(
    resource_id: int = typer.Argument(
        ...,
        help="Resource ID to get quality score for",
    ),
    output_format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format (json, table)",
    ),
) -> None:
    """Get quality score for a resource.

    Examples:
        pharos resource quality 1
        pharos resource quality 1 --format json
    """
    console = get_console()

    try:
        client = get_resource_client()
        quality = client.get_quality_score(resource_id=resource_id)

        formatter = get_formatter(output_format)

        if output_format == "json":
            print(formatter.format(quality))
            return

        # Create quality table
        table = Table(title=f"Quality Score for Resource {resource_id}")
        table.add_column("Metric", style="bold")
        table.add_column("Score", justify="right")

        # Add overall score
        overall = quality.get("overall_score", 0)
        table.add_row("Overall", format_score(overall))

        # Add individual dimensions
        dimensions = ["clarity", "completeness", "correctness", "originality"]
        for dim in dimensions:
            if dim in quality:
                table.add_row(dim.title(), format_score(quality[dim]))

        console.print(table)

        # Show computed time if available
        if quality.get("computed_at"):
            console.print(f"\n[dim]Computed at: {quality['computed_at']}[/dim]")

    except ResourceNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except APIError as e:
        console.print(f"[red]API Error:[/red] {e.message}")
        raise typer.Exit(1)
    except NetworkError as e:
        console.print(f"[red]Network Error:[/red] {e}")
        raise typer.Exit(1)


@resource_app.command("annotations")
def get_resource_annotations(
    resource_id: int = typer.Argument(
        ...,
        help="Resource ID to get annotations for",
    ),
    output_format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format (json, table)",
    ),
) -> None:
    """Get annotations for a resource.

    Examples:
        pharos resource annotations 1
        pharos resource annotations 1 --format json
    """
    console = get_console()

    try:
        client = get_resource_client()
        annotations = client.get_annotations(resource_id=resource_id)

        if not annotations:
            console.print("[yellow]No annotations found for this resource.[/yellow]")
            return

        formatter = get_formatter(output_format)

        if output_format == "json":
            print(formatter.format(annotations))
            return

        # Format as table
        display_items = []
        for ann in annotations:
            display_item = dict(ann)
            # Truncate long text
            if "text" in display_item:
                display_item["text"] = truncate(display_item["text"], 50)
            display_items.append(display_item)

        print(formatter.format_list(display_items))
        console.print(f"\n[dim]Total annotations: {len(annotations)}[/dim]")

    except ResourceNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except APIError as e:
        console.print(f"[red]API Error:[/red] {e.message}")
        raise typer.Exit(1)
    except NetworkError as e:
        console.print(f"[red]Network Error:[/red] {e}")
        raise typer.Exit(1)

@resource_app.command("import")
def import_resources(
    directory: Path = typer.Argument(
        ...,
        help="Directory to import resources from",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive",
        "-r",
        help="Recursively scan subdirectories",
    ),
    pattern: str = typer.Option(
        "*.{py,js,ts,java,c,cpp,h,cs,go,rs,rb,php,md,txt,rst,tex,pdf,html,xml,json,yaml,yml}",
        "--pattern",
        "-p",
        help="File pattern to match (glob format)",
    ),
    resource_type: Optional[str] = typer.Option(
        None,
        "--type",
        "-T",
        help="Resource type for all imported files (auto-detected if not specified)",
    ),
    language: Optional[str] = typer.Option(
        None,
        "--language",
        "-l",
        help="Programming language for all imported files (auto-detected if not specified)",
    ),
    workers: int = typer.Option(
        4,
        "--workers",
        "-w",
        help="Number of parallel workers (1-10)",
    ),
    skip_errors: bool = typer.Option(
        True,
        "--skip-errors/--no-skip-errors",
        help="Skip files that fail to import (continue on failure)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be imported without actually importing",
    ),
    output_format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format (json, table, quiet)",
    ),
) -> None:
    """Import resources from a directory.

    Supports parallel processing, recursive scanning, and error handling.

    Examples:
        pharos resource import ./my_code/
        pharos resource import ./papers/ --recursive
        pharos resource import ./code/ --workers 8 --type code
        pharos resource import ./docs/ --dry-run
    """
    console = get_console()

    # Validate workers
    if workers < 1 or workers > 10:
        console.print("[red]Error:[/red] Workers must be between 1 and 10")
        raise typer.Exit(1)

    # Find files to import
    # Convert glob pattern to list of extensions for cross-platform compatibility
    # Handle bash-style brace expansion: *.py,*.js -> [py, js]
    import re

    # Parse pattern to extract extensions
    # Pattern like "*.{py,js,ts,java,...}" or "*.py"
    extensions = set()

    # Handle brace expansion: *.py,*.js -> [py, js]
    if "{" in pattern and "}" in pattern:
        # Extract content between braces
        brace_content = re.search(r'\{([^}]+)\}', pattern)
        if brace_content:
            exts = brace_content.group(1).split(",")
            for ext in exts:
                ext = ext.strip().lower()
                if ext:
                    extensions.add(ext)
    elif pattern.startswith("*."):
        ext = pattern[2:].strip().lower()
        if ext:
            extensions.add(ext)

    # If no extensions found, use the pattern as-is
    if not extensions:
        extensions = None

    files_to_import: List[Path] = []

    def matches_pattern(filename: str) -> bool:
        """Check if filename matches the pattern (cross-platform)."""
        if extensions is None:
            from fnmatch import fnmatch
            return fnmatch(filename, pattern)

        ext = Path(filename).suffix.lower()
        if ext.startswith("."):
            ext = ext[1:]
        return ext in extensions

    if recursive:
        for root, dirs, files in directory.walk():
            for file in files:
                if matches_pattern(file):
                    files_to_import.append(Path(root) / file)
    else:
        for file in directory.iterdir():
            if file.is_file() and matches_pattern(file.name):
                files_to_import.append(file)

    if not files_to_import:
        console.print(f"[yellow]No files found matching pattern: {pattern}[/yellow]")
        return

    # Sort for consistent ordering
    files_to_import.sort()

    console.print(f"[bold]Found {len(files_to_import)} files to import[/bold]")
    if dry_run:
        console.print("[yellow]Dry run mode - no files will be imported[/yellow]")
        for i, f in enumerate(files_to_import[:20], 1):
            console.print(f"  {i}. {f}")
        if len(files_to_import) > 20:
            console.print(f"  ... and {len(files_to_import) - 20} more")
        return

    # Auto-detect file type mapping
    def detect_type(path: Path) -> Optional[str]:
        if resource_type:
            return resource_type

        ext = path.suffix.lower()
        code_extensions = {".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".cs", ".go", ".rs", ".rb", ".php"}
        doc_extensions = {".md", ".txt", ".rst", ".tex", ".html", ".xml", ".json", ".yaml", ".yml"}
        paper_extensions = {".pdf", ".ps", ".eps"}

        if ext in code_extensions:
            return "code"
        elif ext in doc_extensions:
            return "documentation"
        elif ext in paper_extensions:
            return "paper"
        return "code"  # Default to code

    def detect_language(path: Path) -> Optional[str]:
        if language:
            return language

        ext = path.suffix.lower()
        ext_to_language = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".cs": "csharp",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".r": "r",
            ".jl": "julia",
            ".m": "matlab",
            ".sh": "shell",
            ".html": "html",
            ".css": "css",
            ".sql": "sql",
            ".md": "markdown",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".xml": "xml",
            ".txt": "text",
            ".pdf": "pdf",
        }
        return ext_to_language.get(ext)

    def import_single_file(file_path: Path) -> ImportResult:
        """Import a single file."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return ImportResult(
                file_path=file_path,
                success=False,
                error="Could not read file (not UTF-8 encoded)",
            )
        except IOError as e:
            return ImportResult(
                file_path=file_path,
                success=False,
                error=f"Could not read file: {e}",
            )

        title = file_path.stem.replace("_", " ").replace("-", " ").title()

        try:
            client = get_resource_client()
            result = client.create(
                title=title,
                content=content,
                resource_type=detect_type(file_path),
                language=detect_language(file_path),
            )
            return ImportResult(
                file_path=file_path,
                success=True,
                resource_id=result.get("id"),
            )
        except APIError as e:
            return ImportResult(
                file_path=file_path,
                success=False,
                error=f"API Error: {e.message}",
            )
        except NetworkError as e:
            return ImportResult(
                file_path=file_path,
                success=False,
                error=f"Network Error: {e}",
            )

    # Import files with progress bar
    start_time = time.time()
    results: List[ImportResult] = []
    successful = 0
    failed = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        transient=True,
        console=console,
    ) as progress:
        task = progress.add_task("Importing resources", total=len(files_to_import))

        if workers == 1:
            # Sequential import
            for file_path in files_to_import:
                result = import_single_file(file_path)
                results.append(result)
                if result.success:
                    successful += 1
                else:
                    failed += 1
                    if not skip_errors:
                        console.print(f"[red]Error importing {file_path}: {result.error}[/red]")
                progress.update(task, advance=1)
        else:
            # Parallel import
            with ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_file = {
                    executor.submit(import_single_file, f): f
                    for f in files_to_import
                }
                for future in as_completed(future_to_file):
                    result = future.result()
                    results.append(result)
                    if result.success:
                        successful += 1
                    else:
                        failed += 1
                        if not skip_errors:
                            console.print(f"[red]Error importing {result.file_path}: {result.error}[/red]")
                    progress.update(task, advance=1)

    elapsed_time = time.time() - start_time

    # Print summary
    console.print(f"\n[bold]Import Summary[/bold]")
    console.print(f"  Total files: {len(files_to_import)}")
    console.print(f"  Successful: [green]{successful}[/green]")
    if failed > 0:
        console.print(f"  Failed: [red]{failed}[/red]")
    console.print(f"  Time: {format_duration(elapsed_time)}")
    if elapsed_time > 0:
        rate = successful / elapsed_time
        console.print(f"  Rate: {rate:.1f} files/second")

    # Print output based on format
    if output_format == "json":
        output = {
            "total": len(files_to_import),
            "successful": successful,
            "failed": failed,
            "elapsed_seconds": round(elapsed_time, 2),
            "files_per_second": round(successful / elapsed_time, 2) if elapsed_time > 0 else 0,
            "results": [
                {
                    "file": str(r.file_path),
                    "success": r.success,
                    "resource_id": r.resource_id,
                    "error": r.error,
                }
                for r in results
            ],
        }
        print(json.dumps(output, indent=2))
    elif output_format == "quiet":
        for r in results:
            if r.success:
                print(r.resource_id)
    elif failed > 0 and not skip_errors:
        console.print(f"\n[yellow]Failed files:[/yellow]")
        for r in results:
            if not r.success:
                console.print(f"  {r.file_path}: {r.error}")


@resource_app.command("export")
def export_resource(
    resource_id: int = typer.Argument(
        ...,
        help="Resource ID to export",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (default: resource title as filename)",
    ),
    format: str = typer.Option(
        "text",
        "--format",
        "-f",
        help="Export format (text, json, markdown)",
    ),
    content_only: bool = typer.Option(
        False,
        "--content-only",
        help="Export only the content, not metadata",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite existing file",
    ),
) -> None:
    """Export a resource to a file.

    Examples:
        pharos resource export 1
        pharos resource export 1 --output ./my_export.txt
        pharos resource export 1 --format json
        pharos resource export 1 --content-only
    """
    console = get_console()

    try:
        client = get_resource_client()
        resource = client.get(resource_id=resource_id)

        # Determine output file
        if output is None:
            # Auto-generate filename from title
            safe_title = resource.title.replace("/", "_").replace("\\", "_")
            safe_title = "".join(c for c in safe_title if c.isalnum() or c in (" ", "_", "-"))
            safe_title = safe_title.strip()[:100]  # Limit length

            if format == "json":
                output = Path(f"{safe_title}.json")
            elif format == "markdown":
                output = Path(f"{safe_title}.md")
            else:
                # Determine extension from language
                ext_map = {
                    "python": ".py",
                    "javascript": ".js",
                    "typescript": ".ts",
                    "java": ".java",
                    "c": ".c",
                    "cpp": ".cpp",
                    "csharp": ".cs",
                    "go": ".go",
                    "rust": ".rs",
                    "ruby": ".rb",
                    "php": ".php",
                    "html": ".html",
                    "css": ".css",
                    "sql": ".sql",
                    "markdown": ".md",
                    "json": ".json",
                    "yaml": ".yaml",
                    "xml": ".xml",
                }
                ext = ext_map.get(resource.language, ".txt")
                output = Path(f"{safe_title}{ext}")

        # Check if file exists
        if output.exists() and not overwrite:
            console.print(f"[red]Error:[/red] File already exists: {output}")
            console.print("[yellow]Use --overwrite to replace existing file[/yellow]")
            raise typer.Exit(1)

        # Export based on format
        if format == "json":
            export_data = resource.model_dump()
            if content_only:
                export_data = {"content": resource.content}
            output.write_text(json.dumps(export_data, indent=2, default=str), encoding="utf-8")

        elif format == "markdown":
            lines = []
            lines.append(f"# {resource.title}\n")

            if not content_only:
                lines.append(f"**Type:** {resource.resource_type or 'N/A'}")
                lines.append(f"**Language:** {resource.language or 'N/A'}")
                if resource.url:
                    lines.append(f"**URL:** {resource.url}")
                if resource.quality_score:
                    lines.append(f"**Quality Score:** {resource.quality_score:.2f}")
                lines.append("")

            lines.append("## Content\n")
            lines.append(resource.content or "(No content)")

            output.write_text("\n".join(lines), encoding="utf-8")

        else:  # text format
            if content_only:
                output.write_text(resource.content or "", encoding="utf-8")
            else:
                lines = []
                lines.append(f"Title: {resource.title}")
                lines.append(f"Type: {resource.resource_type or 'N/A'}")
                lines.append(f"Language: {resource.language or 'N/A'}")
                if resource.url:
                    lines.append(f"URL: {resource.url}")
                lines.append("")
                lines.append("-" * 40)
                lines.append("")
                lines.append(resource.content or "(No content)")

                output.write_text("\n".join(lines), encoding="utf-8")

        console.print(f"[green]Resource exported successfully![/green]")
        console.print(f"  Resource ID: {resource_id}")
        console.print(f"  Title: {resource.title}")
        console.print(f"  Output file: {output}")

    except ResourceNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except APIError as e:
        console.print(f"[red]API Error:[/red] {e.message}")
        raise typer.Exit(1)
    except NetworkError as e:
        console.print(f"[red]Network Error:[/red] {e}")
        raise typer.Exit(1)
    except IOError as e:
        console.print(f"[red]Error:[/red] Could not write to file: {e}")
        raise typer.Exit(1)