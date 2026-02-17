"""Error display utilities for Pharos CLI.

Provides error display helpers with Rich panels, suggestions for common errors,
and verbose mode with stack traces for the Pharos CLI.
"""

import sys
import traceback
from typing import Optional, Dict, List, Any, Type
from dataclasses import dataclass, field
from enum import Enum

from rich.panel import Panel
from rich.text import Text
from rich.console import Console
from rich.table import Table
from rich.style import Style
from rich.color import Color
from rich.markup import escape

from pharos_cli.utils.console import get_console
from pharos_cli.client.exceptions import (
    PharosError,
    APIError,
    NetworkError,
    ConfigError,
    AuthenticationError,
    ValidationError,
    ResourceNotFoundError,
    PermissionError,
    CollectionNotFoundError,
    AnnotationNotFoundError,
)


class ErrorSeverity(Enum):
    """Error severity levels for display styling."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ErrorSuggestion:
    """A suggestion to help resolve an error."""
    title: str
    description: str
    command: Optional[str] = None
    link: Optional[str] = None


@dataclass
class ErrorContext:
    """Context information for an error display."""
    message: str
    error_type: str
    severity: ErrorSeverity = ErrorSeverity.ERROR
    suggestion: Optional[ErrorSuggestion] = None
    details: Dict[str, Any] = field(default_factory=dict)
    hint: Optional[str] = None
    exit_code: int = 1


# Common error patterns and their suggestions
COMMON_ERRORS: Dict[Type[Exception], List[ErrorSuggestion]] = {
    NetworkError: [
        ErrorSuggestion(
            title="Check your network connection",
            description="Ensure you have an active internet connection.",
            command="ping -c 1 google.com",
        ),
        ErrorSuggestion(
            title="Verify API URL",
            description="Check that the API URL is correct and accessible.",
            command="pharos config show",
        ),
        ErrorSuggestion(
            title="Check if the server is running",
            description="The API server may be down or unreachable.",
            command="curl -I https://pharos.onrender.com/health",
        ),
    ],
    AuthenticationError: [
        ErrorSuggestion(
            title="Login with API key",
            description="Authenticate using your API key.",
            command="pharos auth login --api-key YOUR_API_KEY",
        ),
        ErrorSuggestion(
            title="Check your credentials",
            description="Your API key may be expired or invalid.",
        ),
        ErrorSuggestion(
            title="Re-authenticate",
            description="Try logging out and logging in again.",
            command="pharos auth logout && pharos auth login --api-key YOUR_API_KEY",
        ),
    ],
    ConfigError: [
        ErrorSuggestion(
            title="Initialize configuration",
            description="Run the configuration wizard to set up your CLI.",
            command="pharos init",
        ),
        ErrorSuggestion(
            title="Check configuration file",
            description="Verify your config file syntax is correct.",
        ),
        ErrorSuggestion(
            title="Reset configuration",
            description="Reset to default configuration.",
            command="rm ~/.pharos/config.yaml && pharos init",
        ),
    ],
    ValidationError: [
        ErrorSuggestion(
            title="Check input format",
            description="Ensure your input matches the expected format.",
        ),
        ErrorSuggestion(
            title="Use --help for usage",
            description="View command usage and required parameters.",
            command="pharos resource add --help",
        ),
    ],
    ResourceNotFoundError: [
        ErrorSuggestion(
            title="List available resources",
            description="Check which resources exist.",
            command="pharos resource list",
        ),
        ErrorSuggestion(
            title="Verify resource ID",
            description="Ensure the resource ID is correct.",
        ),
    ],
    CollectionNotFoundError: [
        ErrorSuggestion(
            title="List available collections",
            description="Check which collections exist.",
            command="pharos collection list",
        ),
        ErrorSuggestion(
            title="Verify collection ID",
            description="Ensure the collection ID is correct.",
        ),
    ],
    AnnotationNotFoundError: [
        ErrorSuggestion(
            title="List annotations",
            description="Check annotations for the resource.",
            command="pharos annotate list RESOURCE_ID",
        ),
    ],
    PermissionError: [
        ErrorSuggestion(
            title="Check your permissions",
            description="You may not have access to this resource.",
        ),
        ErrorSuggestion(
            title="Contact administrator",
            description="Request access from your administrator.",
        ),
    ],
}


def get_suggestions(error: Exception) -> List[ErrorSuggestion]:
    """Get suggestions for an error based on its type.
    
    Args:
        error: The exception to get suggestions for
        
    Returns:
        List of ErrorSuggestion objects with helpful suggestions
    """
    suggestions = []
    
    # Check for exact match in common errors
    error_type = type(error)
    if error_type in COMMON_ERRORS:
        suggestions.extend(COMMON_ERRORS[error_type])
    
    # Check for parent class matches
    for exc_type, type_suggestions in COMMON_ERRORS.items():
        if isinstance(error, exc_type) and exc_type not in COMMON_ERRORS:
            suggestions.extend(type_suggestions)
    
    # Add generic suggestions if none found
    if not suggestions:
        suggestions = [
            ErrorSuggestion(
                title="Use --verbose for more details",
                description="Run with --verbose flag to see full error details.",
            ),
            ErrorSuggestion(
                title="Check the documentation",
                description="Visit our docs for troubleshooting guides.",
                link="https://github.com/pharos/pharos-cli#troubleshooting",
            ),
        ]
    
    return suggestions


def format_error_message(error: Exception) -> str:
    """Format an error message for display.
    
    Args:
        error: The exception to format
        
    Returns:
        Formatted error message string
    """
    if isinstance(error, APIError):
        return f"API Error {error.status_code}: {error.message}"
    elif isinstance(error, NetworkError):
        return f"Network Error: {error.message}"
    elif isinstance(error, ValidationError):
        return f"Validation Error: {error.message}"
    elif isinstance(error, PharosError):
        return f"Error: {error.message}"
    else:
        return f"Error: {str(error)}"


def get_error_severity(error: Exception) -> ErrorSeverity:
    """Determine the severity level for an error.
    
    Args:
        error: The exception to check
        
    Returns:
        ErrorSeverity enum value
    """
    if isinstance(error, (NetworkError, ConfigError)):
        return ErrorSeverity.WARNING
    elif isinstance(error, (AuthenticationError, PermissionError)):
        return ErrorSeverity.ERROR
    elif isinstance(error, APIError):
        if error.status_code >= 500:
            return ErrorSeverity.CRITICAL
        elif error.status_code >= 400:
            return ErrorSeverity.ERROR
        return ErrorSeverity.WARNING
    elif isinstance(error, (ResourceNotFoundError, CollectionNotFoundError, AnnotationNotFoundError)):
        return ErrorSeverity.INFO
    return ErrorSeverity.ERROR


def create_error_panel(
    error: Exception,
    context: Optional[ErrorContext] = None,
    verbose: bool = False,
) -> Panel:
    """Create a Rich panel for displaying an error.
    
    Args:
        error: The exception to display
        context: Optional error context with additional details
        verbose: Whether to show verbose output (stack trace)
        
    Returns:
        Rich Panel object ready for display
    """
    console = get_console()
    severity = get_error_severity(error)
    
    # Determine colors based on severity
    severity_colors = {
        ErrorSeverity.DEBUG: "dim",
        ErrorSeverity.INFO: "blue",
        ErrorSeverity.WARNING: "yellow",
        ErrorSeverity.ERROR: "red",
        ErrorSeverity.CRITICAL: "bright_red",
    }
    color = severity_colors.get(severity, "red")
    
    # Build the error message
    message = format_error_message(error)
    
    # Create the main content
    content = Text()
    content.append(message, style=color)
    
    # Add context details if provided
    if context and context.details:
        content.append("\n\n", style="dim")
        content.append("Details:\n", style="dim")
        for key, value in context.details.items():
            content.append(f"  • {key}: ", style="dim")
            content.append(str(value), style="white")
            content.append("\n", style="dim")
    
    # Add hint if provided
    if context and context.hint:
        content.append("\n\n", style="dim")
        content.append("Hint: ", style="italic yellow")
        content.append(context.hint, style="white")
    
    # Add verbose stack trace
    if verbose:
        content.append("\n\n", style="dim")
        content.append("Stack trace:\n", style="dim")
        tb_str = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        content.append(tb_str, style="dim")
    
    # Determine title based on error type
    if isinstance(error, APIError):
        title = f"API Error ({error.status_code})"
    elif isinstance(error, NetworkError):
        title = "Network Error"
    elif isinstance(error, AuthenticationError):
        title = "Authentication Error"
    elif isinstance(error, ConfigError):
        title = "Configuration Error"
    elif isinstance(error, ValidationError):
        title = "Validation Error"
    elif isinstance(error, ResourceNotFoundError):
        title = "Resource Not Found"
    elif isinstance(error, CollectionNotFoundError):
        title = "Collection Not Found"
    elif isinstance(error, AnnotationNotFoundError):
        title = "Annotation Not Found"
    elif isinstance(error, PermissionError):
        title = "Permission Denied"
    else:
        title = type(error).__name__
    
    return Panel(
        content,
        title=f"[{color}]{title}[/]",
        border_style=color,
        expand=False,
        padding=(1, 2),
    )


def create_suggestions_table(suggestions: List[ErrorSuggestion]) -> Optional[Panel]:
    """Create a table of suggestions for resolving an error.
    
    Args:
        suggestions: List of ErrorSuggestion objects
        
    Returns:
        Rich Panel containing suggestions table, or None if no suggestions
    """
    if not suggestions:
        return None
    
    table = Table(show_header=True, header_style="bold cyan", box=None)
    table.add_column("Suggestion", style="white", width=30)
    table.add_column("Description", style="dim", width=50)
    table.add_column("Action", style="green", width=30)
    
    for suggestion in suggestions:
        table.add_row(
            suggestion.title,
            suggestion.description,
            suggestion.command or suggestion.link or "-",
        )
    
    return Panel(
        table,
        title="[yellow]Suggestions[/]",
        border_style="yellow",
        expand=False,
        padding=(1, 1),
    )


def display_error(
    error: Exception,
    verbose: bool = False,
    context: Optional[ErrorContext] = None,
    suggestions: Optional[List[ErrorSuggestion]] = None,
) -> int:
    """Display an error with optional suggestions and verbose output.
    
    Args:
        error: The exception to display
        verbose: Whether to show verbose output (stack trace)
        context: Optional error context with additional details
        suggestions: Optional list of custom suggestions
        
    Returns:
        Exit code (1 for errors, 0 for success)
    """
    console = get_console()
    
    # Display the main error panel
    panel = create_error_panel(error, context, verbose)
    console.print(panel)
    
    # Get and display suggestions
    error_suggestions = suggestions or get_suggestions(error)
    if error_suggestions:
        suggestions_panel = create_suggestions_table(error_suggestions)
        if suggestions_panel:
            console.print("\n")
            console.print(suggestions_panel)
    
    # Return appropriate exit code
    if isinstance(error, APIError):
        return error.status_code
    return 1


def display_warning(message: str) -> None:
    """Display a warning message.
    
    Args:
        message: Warning message to display
    """
    console = get_console()
    panel = Panel(
        Text(message, style="yellow"),
        title="[yellow]Warning[/]",
        border_style="yellow",
        expand=False,
        padding=(1, 2),
    )
    console.print(panel)


def display_info(message: str) -> None:
    """Display an info message.
    
    Args:
        message: Info message to display
    """
    console = get_console()
    panel = Panel(
        Text(message, style="blue"),
        title="[blue]Info[/]",
        border_style="blue",
        expand=False,
        padding=(1, 2),
    )
    console.print(panel)


def display_success(message: str) -> None:
    """Display a success message.
    
    Args:
        message: Success message to display
    """
    console = get_console()
    panel = Panel(
        Text(message, style="green"),
        title="[green]Success[/]",
        border_style="green",
        expand=False,
        padding=(1, 2),
    )
    console.print(panel)


def format_exception_chain(error: Exception) -> str:
    """Format an exception chain for verbose output.
    
    Args:
        error: The exception to format
        
    Returns:
        Formatted exception chain string
    """
    lines = []
    current = error
    
    while current is not None:
        if isinstance(current, PharosError):
            lines.append(f"{type(current).__name__}: {current.message}")
        else:
            lines.append(f"{type(current).__name__}: {str(current)}")
        
        current = getattr(current, "__cause__", None)
    
    return " -> ".join(lines)


def create_error_context(
    message: str,
    error_type: str,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    suggestion: Optional[ErrorSuggestion] = None,
    details: Optional[Dict[str, Any]] = None,
    hint: Optional[str] = None,
    exit_code: int = 1,
) -> ErrorContext:
    """Create an ErrorContext object.
    
    Args:
        message: Error message
        error_type: Type of error
        severity: Error severity level
        suggestion: Optional single suggestion
        details: Additional error details
        hint: Optional hint for the user
        exit_code: Exit code to return
        
    Returns:
        ErrorContext object
    """
    return ErrorContext(
        message=message,
        error_type=error_type,
        severity=severity,
        suggestion=suggestion,
        details=details or {},
        hint=hint,
        exit_code=exit_code,
    )


def handle_cli_error(
    error: Exception,
    verbose: bool = False,
    context: Optional[ErrorContext] = None,
) -> int:
    """Handle a CLI error and display appropriate message.
    
    This is the main entry point for error handling in CLI commands.
    
    Args:
        error: The exception that occurred
        verbose: Whether to show verbose output
        context: Optional error context
        
    Returns:
        Exit code to use when exiting
    """
    return display_error(error, verbose=verbose, context=context)


def print_error_and_exit(
    error: Exception,
    verbose: bool = False,
    context: Optional[ErrorContext] = None,
) -> None:
    """Print an error message and exit the program.
    
    Args:
        error: The exception that occurred
        verbose: Whether to show verbose output
        context: Optional error context
    """
    exit_code = handle_cli_error(error, verbose, context)
    sys.exit(exit_code)


class ErrorDisplay:
    """Class for managing error display with Rich formatting.
    
    Usage:
        display = ErrorDisplay()
        display.show(error)
        display.show_with_suggestions(error, suggestions)
        display.show_verbose(error)
    """
    
    def __init__(self, verbose: bool = False):
        """Initialize the error display.
        
        Args:
            verbose: Whether to show verbose output by default
        """
        self.verbose = verbose
        self.console = get_console()
    
    def show(self, error: Exception, context: Optional[ErrorContext] = None) -> int:
        """Display an error.
        
        Args:
            error: The exception to display
            context: Optional error context
            
        Returns:
            Exit code
        """
        return display_error(error, verbose=self.verbose, context=context)
    
    def show_with_suggestions(
        self,
        error: Exception,
        suggestions: List[ErrorSuggestion],
        context: Optional[ErrorContext] = None,
    ) -> int:
        """Display an error with custom suggestions.
        
        Args:
            error: The exception to display
            suggestions: List of suggestions to display
            context: Optional error context
            
        Returns:
            Exit code
        """
        return display_error(
            error,
            verbose=self.verbose,
            context=context,
            suggestions=suggestions,
        )
    
    def show_verbose(self, error: Exception, context: Optional[ErrorContext] = None) -> int:
        """Display an error with verbose output (stack trace).
        
        Args:
            error: The exception to display
            context: Optional error context
            
        Returns:
            Exit code
        """
        return display_error(error, verbose=True, context=context)
    
    def warning(self, message: str) -> None:
        """Display a warning.
        
        Args:
            message: Warning message
        """
        display_warning(message)
    
    def info(self, message: str) -> None:
        """Display an info message.
        
        Args:
            message: Info message
        """
        display_info(message)
    
    def success(self, message: str) -> None:
        """Display a success message.
        
        Args:
            message: Success message
        """
        display_success(message)