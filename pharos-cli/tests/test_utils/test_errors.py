"""Tests for error display utilities."""

import pytest
from unittest.mock import MagicMock, patch
import sys

from pharos_cli.utils.errors import (
    ErrorSeverity,
    ErrorSuggestion,
    ErrorContext,
    get_suggestions,
    format_error_message,
    get_error_severity,
    create_error_panel,
    create_suggestions_table,
    display_error,
    display_warning,
    display_info,
    display_success,
    format_exception_chain,
    create_error_context,
    handle_cli_error,
    print_error_and_exit,
    ErrorDisplay,
    COMMON_ERRORS,
)
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


class TestErrorSuggestion:
    """Tests for ErrorSuggestion dataclass."""
    
    def test_error_suggestion_init(self):
        """Test ErrorSuggestion initialization."""
        suggestion = ErrorSuggestion(
            title="Check connection",
            description="Verify your network connection",
            command="ping google.com",
            link="https://docs.example.com",
        )
        assert suggestion.title == "Check connection"
        assert suggestion.description == "Verify your network connection"
        assert suggestion.command == "ping google.com"
        assert suggestion.link == "https://docs.example.com"
    
    def test_error_suggestion_minimal(self):
        """Test ErrorSuggestion with minimal fields."""
        suggestion = ErrorSuggestion(
            title="Check connection",
            description="Verify your network connection",
        )
        assert suggestion.command is None
        assert suggestion.link is None


class TestErrorContext:
    """Tests for ErrorContext dataclass."""
    
    def test_error_context_init(self):
        """Test ErrorContext initialization."""
        context = ErrorContext(
            message="Something went wrong",
            error_type="NetworkError",
            severity=ErrorSeverity.ERROR,
            suggestion=ErrorSuggestion("Try again", "Please retry"),
            details={"key": "value"},
            hint="Check your input",
            exit_code=1,
        )
        assert context.message == "Something went wrong"
        assert context.error_type == "NetworkError"
        assert context.severity == ErrorSeverity.ERROR
        assert context.suggestion is not None
        assert context.details == {"key": "value"}
        assert context.hint == "Check your input"
        assert context.exit_code == 1
    
    def test_error_context_defaults(self):
        """Test ErrorContext default values."""
        context = ErrorContext(
            message="Error message",
            error_type="TestError",
        )
        assert context.severity == ErrorSeverity.ERROR
        assert context.suggestion is None
        assert context.details == {}
        assert context.hint is None
        assert context.exit_code == 1


class TestErrorSeverity:
    """Tests for ErrorSeverity enum."""
    
    def test_error_severity_values(self):
        """Test ErrorSeverity enum values."""
        assert ErrorSeverity.DEBUG.value == "debug"
        assert ErrorSeverity.INFO.value == "info"
        assert ErrorSeverity.WARNING.value == "warning"
        assert ErrorSeverity.ERROR.value == "error"
        assert ErrorSeverity.CRITICAL.value == "critical"


class TestGetSuggestions:
    """Tests for get_suggestions function."""
    
    def test_get_suggestions_network_error(self):
        """Test getting suggestions for NetworkError."""
        error = NetworkError("Connection failed")
        suggestions = get_suggestions(error)
        assert len(suggestions) > 0
        assert any("network" in s.title.lower() for s in suggestions)
    
    def test_get_suggestions_authentication_error(self):
        """Test getting suggestions for AuthenticationError."""
        error = AuthenticationError("Invalid API key")
        suggestions = get_suggestions(error)
        assert len(suggestions) > 0
        assert any("login" in s.title.lower() or "auth" in s.title.lower() for s in suggestions)
    
    def test_get_suggestions_config_error(self):
        """Test getting suggestions for ConfigError."""
        error = ConfigError("Config file not found")
        suggestions = get_suggestions(error)
        assert len(suggestions) > 0
        assert any("config" in s.title.lower() for s in suggestions)
    
    def test_get_suggestions_validation_error(self):
        """Test getting suggestions for ValidationError."""
        error = ValidationError("Invalid input")
        suggestions = get_suggestions(error)
        assert len(suggestions) > 0
        assert any("format" in s.title.lower() or "input" in s.title.lower() for s in suggestions)
    
    def test_get_suggestions_resource_not_found(self):
        """Test getting suggestions for ResourceNotFoundError."""
        error = ResourceNotFoundError("Resource 123 not found")
        suggestions = get_suggestions(error)
        assert len(suggestions) > 0
        assert any("resource" in s.title.lower() for s in suggestions)
    
    def test_get_suggestions_collection_not_found(self):
        """Test getting suggestions for CollectionNotFoundError."""
        error = CollectionNotFoundError("Collection 123 not found")
        suggestions = get_suggestions(error)
        assert len(suggestions) > 0
        assert any("collection" in s.title.lower() for s in suggestions)
    
    def test_get_suggestions_annotation_not_found(self):
        """Test getting suggestions for AnnotationNotFoundError."""
        error = AnnotationNotFoundError("Annotation 123 not found")
        suggestions = get_suggestions(error)
        assert len(suggestions) > 0
        assert any("annotation" in s.title.lower() for s in suggestions)
    
    def test_get_suggestions_permission_error(self):
        """Test getting suggestions for PermissionError."""
        error = PermissionError("Access denied")
        suggestions = get_suggestions(error)
        assert len(suggestions) > 0
        assert any("permission" in s.title.lower() or "access" in s.title.lower() for s in suggestions)
    
    def test_get_suggestions_generic_error(self):
        """Test getting suggestions for generic Exception."""
        error = ValueError("Some value error")
        suggestions = get_suggestions(error)
        assert len(suggestions) > 0
        # Generic errors should get verbose and documentation suggestions
        assert any("verbose" in s.title.lower() for s in suggestions)
    
    def test_get_suggestions_api_error(self):
        """Test getting suggestions for APIError."""
        error = APIError(400, "Bad request")
        suggestions = get_suggestions(error)
        # APIError doesn't have specific suggestions, should get generic ones
        assert len(suggestions) > 0


class TestFormatErrorMessage:
    """Tests for format_error_message function."""
    
    def test_format_api_error(self):
        """Test formatting APIError."""
        error = APIError(404, "Resource not found")
        result = format_error_message(error)
        assert "API Error 404" in result
        assert "Resource not found" in result
    
    def test_format_network_error(self):
        """Test formatting NetworkError."""
        error = NetworkError("Connection refused")
        result = format_error_message(error)
        assert "Network Error" in result
        assert "Connection refused" in result
    
    def test_format_validation_error(self):
        """Test formatting ValidationError."""
        error = ValidationError("Invalid input format")
        result = format_error_message(error)
        assert "Validation Error" in result
        assert "Invalid input format" in result
    
    def test_format_pharos_error(self):
        """Test formatting generic PharosError."""
        error = PharosError("Something went wrong")
        result = format_error_message(error)
        assert "Error" in result
        assert "Something went wrong" in result
    
    def test_format_generic_exception(self):
        """Test formatting generic Exception."""
        error = ValueError("Invalid value")
        result = format_error_message(error)
        assert "Error" in result
        assert "Invalid value" in result


class TestGetErrorSeverity:
    """Tests for get_error_severity function."""
    
    def test_severity_network_error(self):
        """Test severity for NetworkError."""
        error = NetworkError("Connection failed")
        severity = get_error_severity(error)
        assert severity == ErrorSeverity.WARNING
    
    def test_severity_config_error(self):
        """Test severity for ConfigError."""
        error = ConfigError("Config not found")
        severity = get_error_severity(error)
        assert severity == ErrorSeverity.WARNING
    
    def test_severity_authentication_error(self):
        """Test severity for AuthenticationError."""
        error = AuthenticationError("Invalid token")
        severity = get_error_severity(error)
        assert severity == ErrorSeverity.ERROR
    
    def test_severity_permission_error(self):
        """Test severity for PermissionError."""
        error = PermissionError("Access denied")
        severity = get_error_severity(error)
        assert severity == ErrorSeverity.ERROR
    
    def test_severity_api_error_4xx(self):
        """Test severity for APIError with 4xx status."""
        error = APIError(400, "Bad request")
        severity = get_error_severity(error)
        assert severity == ErrorSeverity.ERROR
    
    def test_severity_api_error_5xx(self):
        """Test severity for APIError with 5xx status."""
        error = APIError(500, "Internal server error")
        severity = get_error_severity(error)
        assert severity == ErrorSeverity.CRITICAL
    
    def test_severity_api_error_3xx(self):
        """Test severity for APIError with 3xx status."""
        error = APIError(301, "Redirect")
        severity = get_error_severity(error)
        assert severity == ErrorSeverity.WARNING
    
    def test_severity_resource_not_found(self):
        """Test severity for ResourceNotFoundError."""
        error = ResourceNotFoundError("Not found")
        severity = get_error_severity(error)
        assert severity == ErrorSeverity.INFO
    
    def test_severity_generic_error(self):
        """Test severity for generic Exception."""
        error = ValueError("Invalid value")
        severity = get_error_severity(error)
        assert severity == ErrorSeverity.ERROR


class TestCreateErrorPanel:
    """Tests for create_error_panel function."""
    
    def test_create_error_panel_basic(self):
        """Test creating a basic error panel."""
        error = ValueError("Test error")
        panel = create_error_panel(error)
        assert panel is not None
        assert panel.border_style is not None
    
    def test_create_error_panel_with_context(self):
        """Test creating error panel with context."""
        error = APIError(400, "Bad request")
        context = ErrorContext(
            message="API Error",
            error_type="APIError",
            details={"request_id": "123"},
        )
        panel = create_error_panel(error, context=context)
        assert panel is not None
    
    def test_create_error_panel_verbose(self):
        """Test creating error panel with verbose output."""
        error = ValueError("Test error")
        panel = create_error_panel(error, verbose=True)
        assert panel is not None
    
    def test_create_error_panel_api_error_title(self):
        """Test error panel title for APIError."""
        error = APIError(404, "Not found")
        panel = create_error_panel(error)
        assert "404" in str(panel.title) or "API Error" in str(panel.title)
    
    def test_create_error_panel_network_error_title(self):
        """Test error panel title for NetworkError."""
        error = NetworkError("Connection failed")
        panel = create_error_panel(error)
        assert "Network" in str(panel.title)
    
    def test_create_error_panel_with_hint(self):
        """Test creating error panel with hint."""
        error = ValidationError("Invalid input")
        context = ErrorContext(
            message="Validation error",
            error_type="ValidationError",
            hint="Check the documentation for valid formats",
        )
        panel = create_error_panel(error, context=context)
        assert panel is not None


class TestCreateSuggestionsTable:
    """Tests for create_suggestions_table function."""
    
    def test_create_suggestions_table_empty(self):
        """Test creating suggestions table with empty list."""
        panel = create_suggestions_table([])
        assert panel is None
    
    def test_create_suggestions_table_with_suggestions(self):
        """Test creating suggestions table with suggestions."""
        suggestions = [
            ErrorSuggestion("Check connection", "Verify network", "ping google.com"),
            ErrorSuggestion("Retry", "Try again", "pharos retry"),
        ]
        panel = create_suggestions_table(suggestions)
        assert panel is not None
        assert panel.border_style is not None
    
    def test_create_suggestions_table_with_link(self):
        """Test creating suggestions table with link instead of command."""
        suggestions = [
            ErrorSuggestion(
                "See docs",
                "Check documentation",
                link="https://docs.example.com",
            ),
        ]
        panel = create_suggestions_table(suggestions)
        assert panel is not None


class TestDisplayError:
    """Tests for display_error function."""
    
    def test_display_error_basic(self):
        """Test displaying a basic error."""
        error = ValueError("Test error")
        exit_code = display_error(error)
        assert exit_code == 1
    
    def test_display_error_api_error(self):
        """Test displaying APIError returns status code."""
        error = APIError(404, "Not found")
        exit_code = display_error(error)
        assert exit_code == 404
    
    def test_display_error_with_verbose(self):
        """Test displaying error with verbose flag."""
        error = ValueError("Test error")
        exit_code = display_error(error, verbose=True)
        assert exit_code == 1
    
    def test_display_error_with_context(self):
        """Test displaying error with context."""
        error = APIError(400, "Bad request")
        context = ErrorContext(
            message="Error",
            error_type="APIError",
            details={"key": "value"},
        )
        exit_code = display_error(error, context=context)
        assert exit_code == 400
    
    def test_display_error_with_custom_suggestions(self):
        """Test displaying error with custom suggestions."""
        error = ValueError("Test error")
        suggestions = [
            ErrorSuggestion("Custom", "Custom suggestion", "custom command"),
        ]
        exit_code = display_error(error, suggestions=suggestions)
        assert exit_code == 1


class TestDisplayWarning:
    """Tests for display_warning function."""
    
    def test_display_warning(self):
        """Test displaying a warning."""
        # Should not raise an exception
        display_warning("This is a warning")


class TestDisplayInfo:
    """Tests for display_info function."""
    
    def test_display_info(self):
        """Test displaying info message."""
        # Should not raise an exception
        display_info("This is info")


class TestDisplaySuccess:
    """Tests for display_success function."""
    
    def test_display_success(self):
        """Test displaying success message."""
        # Should not raise an exception
        display_success("Operation completed")


class TestFormatExceptionChain:
    """Tests for format_exception_chain function."""
    
    def test_format_exception_chain_single(self):
        """Test formatting single exception."""
        error = ValueError("Test error")
        result = format_exception_chain(error)
        assert "ValueError" in result
        assert "Test error" in result
    
    def test_format_exception_chain_with_cause(self):
        """Test formatting exception chain with cause."""
        try:
            raise ValueError("Original error")
        except ValueError as e:
            try:
                raise RuntimeError("Wrapper error") from e
            except RuntimeError as e:
                result = format_exception_chain(e)
                assert "RuntimeError" in result
                assert "ValueError" in result


class TestCreateErrorContext:
    """Tests for create_error_context function."""
    
    def test_create_error_context_basic(self):
        """Test creating error context."""
        context = create_error_context(
            message="Error message",
            error_type="TestError",
        )
        assert context.message == "Error message"
        assert context.error_type == "TestError"
        assert context.severity == ErrorSeverity.ERROR
        assert context.exit_code == 1
    
    def test_create_error_context_with_all_params(self):
        """Test creating error context with all parameters."""
        suggestion = ErrorSuggestion("Fix", "Fix it")
        context = create_error_context(
            message="Error message",
            error_type="TestError",
            severity=ErrorSeverity.WARNING,
            suggestion=suggestion,
            details={"key": "value"},
            hint="Check this",
            exit_code=2,
        )
        assert context.severity == ErrorSeverity.WARNING
        assert context.suggestion == suggestion
        assert context.details == {"key": "value"}
        assert context.hint == "Check this"
        assert context.exit_code == 2


class TestHandleCliError:
    """Tests for handle_cli_error function."""
    
    def test_handle_cli_error_basic(self):
        """Test handling basic CLI error."""
        error = ValueError("Test error")
        exit_code = handle_cli_error(error)
        assert exit_code == 1
    
    def test_handle_cli_error_api_error(self):
        """Test handling APIError."""
        error = APIError(500, "Server error")
        exit_code = handle_cli_error(error)
        assert exit_code == 500
    
    def test_handle_cli_error_verbose(self):
        """Test handling error with verbose flag."""
        error = ValueError("Test error")
        exit_code = handle_cli_error(error, verbose=True)
        assert exit_code == 1
    
    def test_handle_cli_error_with_context(self):
        """Test handling error with context."""
        error = APIError(400, "Bad request")
        context = ErrorContext(
            message="Error",
            error_type="APIError",
        )
        exit_code = handle_cli_error(error, context=context)
        assert exit_code == 400


class TestPrintErrorAndExit:
    """Tests for print_error_and_exit function."""
    
    def test_print_error_and_exit(self):
        """Test printing error and exiting."""
        error = ValueError("Test error")
        with pytest.raises(SystemExit) as exc_info:
            print_error_and_exit(error)
        assert exc_info.value.code == 1
    
    def test_print_error_and_exit_api_error(self):
        """Test printing APIError and exiting."""
        error = APIError(404, "Not found")
        with pytest.raises(SystemExit) as exc_info:
            print_error_and_exit(error)
        assert exc_info.value.code == 404


class TestErrorDisplay:
    """Tests for ErrorDisplay class."""
    
    def test_error_display_init(self):
        """Test ErrorDisplay initialization."""
        display = ErrorDisplay()
        assert display.verbose is False
    
    def test_error_display_init_verbose(self):
        """Test ErrorDisplay with verbose=True."""
        display = ErrorDisplay(verbose=True)
        assert display.verbose is True
    
    def test_error_display_show(self):
        """Test ErrorDisplay.show method."""
        display = ErrorDisplay()
        error = ValueError("Test error")
        exit_code = display.show(error)
        assert exit_code == 1
    
    def test_error_display_show_with_suggestions(self):
        """Test ErrorDisplay.show_with_suggestions method."""
        display = ErrorDisplay()
        error = ValueError("Test error")
        suggestions = [ErrorSuggestion("Fix", "Fix it")]
        exit_code = display.show_with_suggestions(error, suggestions)
        assert exit_code == 1
    
    def test_error_display_show_verbose(self):
        """Test ErrorDisplay.show_verbose method."""
        display = ErrorDisplay()
        error = ValueError("Test error")
        exit_code = display.show_verbose(error)
        assert exit_code == 1
    
    def test_error_display_warning(self):
        """Test ErrorDisplay.warning method."""
        display = ErrorDisplay()
        # Should not raise an exception
        display.warning("Test warning")
    
    def test_error_display_info(self):
        """Test ErrorDisplay.info method."""
        display = ErrorDisplay()
        # Should not raise an exception
        display.info("Test info")
    
    def test_error_display_success(self):
        """Test ErrorDisplay.success method."""
        display = ErrorDisplay()
        # Should not raise an exception
        display.success("Test success")


class TestCommonErrors:
    """Tests for COMMON_ERRORS dictionary."""
    
    def test_common_errors_has_network_error(self):
        """Test that COMMON_ERRORS has NetworkError."""
        assert NetworkError in COMMON_ERRORS
        assert len(COMMON_ERRORS[NetworkError]) > 0
    
    def test_common_errors_has_authentication_error(self):
        """Test that COMMON_ERRORS has AuthenticationError."""
        assert AuthenticationError in COMMON_ERRORS
        assert len(COMMON_ERRORS[AuthenticationError]) > 0
    
    def test_common_errors_has_config_error(self):
        """Test that COMMON_ERRORS has ConfigError."""
        assert ConfigError in COMMON_ERRORS
        assert len(COMMON_ERRORS[ConfigError]) > 0
    
    def test_common_errors_has_validation_error(self):
        """Test that COMMON_ERRORS has ValidationError."""
        assert ValidationError in COMMON_ERRORS
        assert len(COMMON_ERRORS[ValidationError]) > 0
    
    def test_common_errors_has_resource_not_found_error(self):
        """Test that COMMON_ERRORS has ResourceNotFoundError."""
        assert ResourceNotFoundError in COMMON_ERRORS
        assert len(COMMON_ERRORS[ResourceNotFoundError]) > 0
    
    def test_common_errors_has_collection_not_found_error(self):
        """Test that COMMON_ERRORS has CollectionNotFoundError."""
        assert CollectionNotFoundError in COMMON_ERRORS
        assert len(COMMON_ERRORS[CollectionNotFoundError]) > 0
    
    def test_common_errors_has_annotation_not_found_error(self):
        """Test that COMMON_ERRORS has AnnotationNotFoundError."""
        assert AnnotationNotFoundError in COMMON_ERRORS
        assert len(COMMON_ERRORS[AnnotationNotFoundError]) > 0
    
    def test_common_errors_has_permission_error(self):
        """Test that COMMON_ERRORS has PermissionError."""
        assert PermissionError in COMMON_ERRORS
        assert len(COMMON_ERRORS[PermissionError]) > 0


class TestErrorDisplayIntegration:
    """Integration tests for error display utilities."""
    
    def test_full_error_display_workflow(self):
        """Test complete error display workflow."""
        error = APIError(
            status_code=400,
            message="Invalid request parameters",
            details={"param": "resource_id", "reason": "not found"},
        )
        
        # Get severity
        severity = get_error_severity(error)
        assert severity == ErrorSeverity.ERROR
        
        # Format message
        message = format_error_message(error)
        assert "API Error 400" in message
        
        # Get suggestions
        suggestions = get_suggestions(error)
        assert len(suggestions) > 0
        
        # Create panel
        panel = create_error_panel(error, verbose=False)
        assert panel is not None
        
        # Create suggestions table
        table = create_suggestions_table(suggestions)
        assert table is not None
        
        # Display error
        exit_code = display_error(error, suggestions=suggestions)
        assert exit_code == 400
    
    def test_verbose_error_display_workflow(self):
        """Test verbose error display workflow."""
        error = ValueError("Detailed error message")
        
        # Create panel with verbose
        panel = create_error_panel(error, verbose=True)
        assert panel is not None
        
        # Display with verbose
        exit_code = display_error(error, verbose=True)
        assert exit_code == 1
    
    def test_custom_error_context_workflow(self):
        """Test custom error context workflow."""
        error = ConfigError("Configuration missing")
        
        context = create_error_context(
            message="Config error",
            error_type="ConfigError",
            severity=ErrorSeverity.WARNING,
            details={"config_path": "/path/to/config"},
            hint="Run 'pharos init' to create default config",
        )
        
        # Create panel with context
        panel = create_error_panel(error, context=context)
        assert panel is not None
        
        # Display with context
        exit_code = display_error(error, context=context)
        assert exit_code == 1
    
    def test_error_display_class_workflow(self):
        """Test ErrorDisplay class workflow."""
        display = ErrorDisplay(verbose=False)
        
        # Show error
        error = NetworkError("Connection failed")
        exit_code = display.show(error)
        assert exit_code == 1
        
        # Show with suggestions
        suggestions = get_suggestions(error)
        exit_code = display.show_with_suggestions(error, suggestions)
        assert exit_code == 1
        
        # Show verbose
        exit_code = display.show_verbose(error)
        assert exit_code == 1
        
        # Show warning
        display.warning("This is a warning")
        
        # Show info
        display.info("This is info")
        
        # Show success
        display.success("This is success")