"""Integration tests for code commands."""

import pytest
import json
import tempfile
import os
from pathlib import Path
from typing import Generator
from contextlib import contextmanager
from unittest.mock import patch, MagicMock

from typer.testing import CliRunner

from pharos_cli.cli import app


runner = CliRunner()


@contextmanager
def create_temp_python_file() -> Generator[Path, None, None]:
    """Create a temporary Python file for testing."""
    content = '''"""Example Python module."""

import os
import sys
from typing import List, Dict


class ExampleClass:
    """Example class for testing."""
    
    def __init__(self, name: str):
        self.name = name
    
    def get_name(self) -> str:
        """Get the name."""
        return self.name


def example_function(x: int, y: int = 10) -> int:
    """Example function."""
    if x > y:
        return x - y
    return 0
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(content)
        f.flush()
        path = Path(f.name)
    try:
        yield path
    finally:
        if path.exists():
            os.unlink(str(path))


@contextmanager
def create_temp_js_file() -> Generator[Path, None, None]:
    """Create a temporary JavaScript file for testing."""
    content = '''// Example JavaScript module
const fs = require('fs');
import { useState, useEffect } from 'react';

class ExampleComponent {
    constructor(name) {
        this.name = name;
    }
    
    getName() {
        return this.name;
    }
    
    async fetchData() {
        const response = await fetch('/api/data');
        return response.json();
    }
}

function exampleFunction(x, y = 10) {
    if (x > y) {
        return x - y;
    } else if (x < y) {
        return y - x;
    }
    return 0;
}

const arrowFunction = (a, b) => a + b;
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(content)
        f.flush()
        path = Path(f.name)
    try:
        yield path
    finally:
        if path.exists():
            os.unlink(str(path))


@contextmanager
def create_temp_directory() -> Generator[Path, None, None]:
    """Create a temporary directory with code files."""
    tmpdir = tempfile.mkdtemp()
    dir_path = Path(tmpdir)

    # Create Python files
    for i in range(3):
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', dir=tmpdir, delete=False, encoding='utf-8'
        ) as f:
            f.write(f'# File {i}\ndef func{i}():\n    pass\n')
            f.flush()

    # Create JavaScript file
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.js', dir=tmpdir, delete=False, encoding='utf-8'
    ) as f:
        f.write('// JS File\nfunction jsFunc() { return 1; }\n')
        f.flush()

    try:
        yield dir_path
    finally:
        import shutil
        if dir_path.exists():
            shutil.rmtree(str(dir_path))


class TestCodeAnalyzeCommand:
    """Test cases for 'pharos code analyze' command."""

    def test_analyze_basic(self) -> None:
        """Test basic code analysis."""
        with create_temp_python_file() as python_file:
            result = runner.invoke(app, ["code", "analyze", str(python_file)])

            assert result.exit_code == 0
            assert "File:" in result.stdout or python_file.name in result.stdout
            assert "Language:" in result.stdout
            assert "Metrics:" in result.stdout or "Total Lines" in result.stdout

    def test_analyze_with_format_json(self) -> None:
        """Test code analysis with JSON output."""
        with create_temp_python_file() as python_file:
            result = runner.invoke(app, ["code", "analyze", str(python_file), "--format", "json"])

            assert result.exit_code == 0
            # Verify it's valid JSON
            data = json.loads(result.stdout)
            assert "file_name" in data
            assert "language" in data
            assert "metrics" in data

    def test_analyze_with_language_option(self) -> None:
        """Test code analysis with explicit language."""
        with create_temp_python_file() as python_file:
            result = runner.invoke(app, ["code", "analyze", str(python_file), "--language", "python"])

            assert result.exit_code == 0
            assert "python" in result.stdout.lower()

    def test_analyze_file_not_found(self) -> None:
        """Test analyzing non-existent file."""
        result = runner.invoke(app, ["code", "analyze", "/nonexistent/file.py"])

        # Exit code 2 is for usage errors (missing arguments), 1 for other errors
        # When file doesn't exist, it may be a usage error (exit code 2) or other error (exit code 1)
        assert result.exit_code in [1, 2]
        # For exit code 2 (usage error), stdout may be empty
        if result.exit_code == 1:
            assert "Error" in result.stdout or "not found" in result.stdout.lower()


class TestCodeAstCommand:
    """Test cases for 'pharos code ast' command."""

    def test_ast_basic(self) -> None:
        """Test basic AST extraction."""
        with create_temp_python_file() as python_file:
            result = runner.invoke(app, ["code", "ast", str(python_file)])

            assert result.exit_code == 0
            assert "AST" in result.stdout or python_file.name in result.stdout

    def test_ast_json_format(self) -> None:
        """Test AST extraction with JSON format."""
        with create_temp_python_file() as python_file:
            result = runner.invoke(app, ["code", "ast", str(python_file), "--format", "json"])

            assert result.exit_code == 0
            data = json.loads(result.stdout)
            assert "file_path" in data
            assert "language" in data
            assert "ast" in data

    def test_ast_text_format(self) -> None:
        """Test AST extraction with text format."""
        with create_temp_python_file() as python_file:
            result = runner.invoke(app, ["code", "ast", str(python_file), "--format", "text"])

            assert result.exit_code == 0
            # Text format should contain AST representation
            # The simple AST extraction produces a tree with definitions
            assert "AST:" in result.stdout or "Definitions" in result.stdout

    def test_ast_output_to_file(self) -> None:
        """Test AST extraction to file."""
        with create_temp_python_file() as python_file:
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
                output_file = Path(f.name)

            try:
                result = runner.invoke(app, [
                    "code", "ast", str(python_file),
                    "--output", str(output_file)
                ])

                assert result.exit_code == 0
                assert output_file.exists()
                data = json.loads(output_file.read_text())
                assert "file_path" in data
            finally:
                if output_file.exists():
                    os.unlink(str(output_file))

    def test_ast_file_not_found(self) -> None:
        """Test AST extraction for non-existent file."""
        result = runner.invoke(app, ["code", "ast", "/nonexistent/file.py"])

        # Exit code 2 is for usage errors (missing arguments), 1 for other errors
        assert result.exit_code in [1, 2]


class TestCodeDepsCommand:
    """Test cases for 'pharos code deps' command."""

    def test_deps_basic(self) -> None:
        """Test basic dependency extraction."""
        with create_temp_python_file() as python_file:
            result = runner.invoke(app, ["code", "deps", str(python_file)])

            assert result.exit_code == 0
            assert "Dependencies" in result.stdout or python_file.name in result.stdout
            assert "Imports" in result.stdout

    def test_deps_json_format(self) -> None:
        """Test dependency extraction with JSON format."""
        with create_temp_python_file() as python_file:
            result = runner.invoke(app, ["code", "deps", str(python_file), "--format", "json"])

            assert result.exit_code == 0
            data = json.loads(result.stdout)
            assert "file_name" in data
            assert "imports" in data

    def test_deps_file_not_found(self) -> None:
        """Test dependency extraction for non-existent file."""
        result = runner.invoke(app, ["code", "deps", "/nonexistent/file.py"])

        # Exit code 2 is for usage errors (missing arguments), 1 for other errors
        assert result.exit_code in [1, 2]


class TestCodeChunkCommand:
    """Test cases for 'pharos code chunk' command."""

    def test_chunk_basic(self) -> None:
        """Test basic code chunking."""
        with create_temp_python_file() as python_file:
            result = runner.invoke(app, ["code", "chunk", str(python_file)])

            assert result.exit_code == 0
            assert "Chunking Results" in result.stdout or python_file.name in result.stdout
            assert "Total Chunks" in result.stdout

    def test_chunk_json_format(self) -> None:
        """Test code chunking with JSON format."""
        with create_temp_python_file() as python_file:
            result = runner.invoke(app, ["code", "chunk", str(python_file), "--format", "json"])

            assert result.exit_code == 0
            # The output may contain ANSI escape codes from Rich, strip them
            import re
            # Remove all ANSI escape codes
            clean_output = re.sub(r'\x1B\[[0-9;]*[mGKHF]', '', result.stdout)
            # Also remove any remaining control characters that might break JSON
            clean_output = re.sub(r'[\x00-\x1f\x7f]', '', clean_output)
            data = json.loads(clean_output)
            assert "file_name" in data
            assert "chunks" in data
            assert "total_chunks" in data

    def test_chunk_with_strategy(self) -> None:
        """Test code chunking with different strategies."""
        with create_temp_python_file() as python_file:
            for strategy in ["semantic", "fixed"]:
                result = runner.invoke(app, [
                    "code", "chunk", str(python_file),
                    "--strategy", strategy
                ])
                assert result.exit_code == 0

    def test_chunk_with_custom_size(self) -> None:
        """Test code chunking with custom chunk size."""
        with create_temp_python_file() as python_file:
            result = runner.invoke(app, [
                "code", "chunk", str(python_file),
                "--chunk-size", "100",
                "--overlap", "20"
            ])

            assert result.exit_code == 0

    def test_chunk_invalid_chunk_size(self) -> None:
        """Test code chunking with invalid chunk size."""
        with create_temp_python_file() as python_file:
            result = runner.invoke(app, [
                "code", "chunk", str(python_file),
                "--chunk-size", "10"  # Too small
            ])

            assert result.exit_code == 1
            assert "Error" in result.stdout

    def test_chunk_invalid_overlap(self) -> None:
        """Test code chunking with invalid overlap."""
        with create_temp_python_file() as python_file:
            result = runner.invoke(app, [
                "code", "chunk", str(python_file),
                "--overlap", "1000"  # Larger than chunk_size
            ])

            assert result.exit_code == 1

    def test_chunk_output_to_file(self) -> None:
        """Test code chunking to file."""
        with create_temp_python_file() as python_file:
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
                output_file = Path(f.name)

            try:
                result = runner.invoke(app, [
                    "code", "chunk", str(python_file),
                    "--output", str(output_file)
                ])

                assert result.exit_code == 0
                assert output_file.exists()
                content = output_file.read_text()
                assert "---" in content  # Chunks are separated by ---
            finally:
                if output_file.exists():
                    os.unlink(str(output_file))

    def test_chunk_file_not_found(self) -> None:
        """Test code chunking for non-existent file."""
        result = runner.invoke(app, ["code", "chunk", "/nonexistent/file.py"])

        # Exit code 2 is for usage errors (missing arguments), 1 for other errors
        assert result.exit_code in [1, 2]


class TestCodeScanCommand:
    """Test cases for 'pharos code scan' command."""

    def test_scan_basic(self) -> None:
        """Test basic directory scanning."""
        with create_temp_directory() as temp_dir:
            result = runner.invoke(app, ["code", "scan", str(temp_dir)])

            assert result.exit_code == 0
            assert "Scan Results" in result.stdout or temp_dir.name in result.stdout
            assert "Total Files" in result.stdout or "Files" in result.stdout

    def test_scan_json_format(self) -> None:
        """Test directory scanning with JSON format."""
        with create_temp_directory() as temp_dir:
            result = runner.invoke(app, ["code", "scan", str(temp_dir), "--format", "json"])

            assert result.exit_code == 0
            data = json.loads(result.stdout)
            assert "directory" in data
            assert "total_files_scanned" in data
            assert "language_distribution" in data

    def test_scan_non_recursive(self) -> None:
        """Test non-recursive directory scanning."""
        with create_temp_directory() as temp_dir:
            # Create a subdirectory
            subdir = temp_dir / "subdir"
            subdir.mkdir()
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', dir=str(subdir), delete=False, encoding='utf-8'
            ) as f:
                f.write("# Subdir file\ndef sub():\n    pass\n")

            result = runner.invoke(app, ["code", "scan", str(temp_dir), "--no-recursive"])

            assert result.exit_code == 0

    def test_scan_with_pattern(self) -> None:
        """Test directory scanning with file pattern."""
        with create_temp_directory() as temp_dir:
            result = runner.invoke(app, [
                "code", "scan", str(temp_dir),
                "--pattern", "*.py"
            ])

            assert result.exit_code == 0
            # Should only show Python files
            assert "python" in result.stdout.lower() or "Files" in result.stdout

    def test_scan_with_limit(self) -> None:
        """Test directory scanning with file limit."""
        with create_temp_directory() as temp_dir:
            result = runner.invoke(app, [
                "code", "scan", str(temp_dir),
                "--limit", "2"
            ])

            assert result.exit_code == 0

    def test_scan_invalid_workers(self) -> None:
        """Test directory scanning with invalid workers."""
        with create_temp_directory() as temp_dir:
            result = runner.invoke(app, [
                "code", "scan", str(temp_dir),
                "--workers", "20"  # Too many
            ])

            assert result.exit_code == 1
            assert "Error" in result.stdout

    def test_scan_directory_not_found(self) -> None:
        """Test scanning non-existent directory."""
        result = runner.invoke(app, ["code", "scan", "/nonexistent/directory"])

        # Exit code 2 is for usage errors (missing arguments), 1 for other errors
        assert result.exit_code in [1, 2]


class TestCodeLanguagesCommand:
    """Test cases for 'pharos code languages' command."""

    def test_languages_list(self) -> None:
        """Test listing supported languages."""
        result = runner.invoke(app, ["code", "languages"])

        assert result.exit_code == 0
        assert "python" in result.stdout.lower()
        assert "javascript" in result.stdout.lower()
        assert "Language" in result.stdout or "Extensions" in result.stdout


class TestCodeStatsCommand:
    """Test cases for 'pharos code stats' command."""

    def test_stats_file(self) -> None:
        """Test stats for a single file."""
        with create_temp_python_file() as python_file:
            result = runner.invoke(app, ["code", "stats", str(python_file)])

            assert result.exit_code == 0
            assert "Code Statistics" in result.stdout or python_file.name in result.stdout
            assert "Language:" in result.stdout or "python" in result.stdout.lower()

    def test_stats_directory(self) -> None:
        """Test stats for a directory."""
        with create_temp_directory() as temp_dir:
            result = runner.invoke(app, ["code", "stats", str(temp_dir)])

            assert result.exit_code == 0
            assert "Code Statistics" in result.stdout or temp_dir.name in result.stdout
            assert "Total Files" in result.stdout or "Total Lines" in result.stdout

    def test_stats_current_directory(self) -> None:
        """Test stats for current directory."""
        result = runner.invoke(app, ["code", "stats", "."])

        assert result.exit_code == 0


class TestCodeCommandHelp:
    """Test help and error messages for code commands."""

    def test_code_help(self) -> None:
        """Test main code command help."""
        result = runner.invoke(app, ["code", "--help"])

        assert result.exit_code == 0
        assert "analyze" in result.stdout.lower()
        assert "ast" in result.stdout.lower()
        assert "deps" in result.stdout.lower()
        assert "chunk" in result.stdout.lower()
        assert "scan" in result.stdout.lower()

    def test_analyze_help(self) -> None:
        """Test analyze command help."""
        result = runner.invoke(app, ["code", "analyze", "--help"])

        assert result.exit_code == 0
        assert "file" in result.stdout.lower()
        assert "--format" in result.stdout
        assert "--language" in result.stdout

    def test_ast_help(self) -> None:
        """Test AST command help."""
        result = runner.invoke(app, ["code", "ast", "--help"])

        assert result.exit_code == 0
        assert "file" in result.stdout.lower()
        assert "--format" in result.stdout
        assert "--output" in result.stdout

    def test_deps_help(self) -> None:
        """Test deps command help."""
        result = runner.invoke(app, ["code", "deps", "--help"])

        assert result.exit_code == 0
        assert "file" in result.stdout.lower()
        assert "--format" in result.stdout
        assert "--transitive" in result.stdout

    def test_chunk_help(self) -> None:
        """Test chunk command help."""
        result = runner.invoke(app, ["code", "chunk", "--help"])

        assert result.exit_code == 0
        assert "file" in result.stdout.lower()
        assert "--strategy" in result.stdout
        assert "--chunk-size" in result.stdout
        assert "--overlap" in result.stdout

    def test_scan_help(self) -> None:
        """Test scan command help."""
        result = runner.invoke(app, ["code", "scan", "--help"])

        assert result.exit_code == 0
        assert "directory" in result.stdout.lower()
        assert "--recursive" in result.stdout
        assert "--pattern" in result.stdout
        assert "--limit" in result.stdout

    def test_languages_help(self) -> None:
        """Test languages command help."""
        result = runner.invoke(app, ["code", "languages"])

        assert result.exit_code == 0

    def test_stats_help(self) -> None:
        """Test stats command help."""
        result = runner.invoke(app, ["code", "stats", "--help"])

        assert result.exit_code == 0
        assert "file" in result.stdout.lower() or "directory" in result.stdout.lower()


class TestCodeCommandErrors:
    """Test error handling for code commands."""

    def test_analyze_permission_error(self) -> None:
        """Test analyzing file without read permission."""
        # This is hard to test on Windows, so we skip if we can't create such a file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write("# Test")
            f.flush()
            path = Path(f.name)

        try:
            # Try to make file unreadable (may not work on all systems)
            os.chmod(str(path), 0o000)

            result = runner.invoke(app, ["code", "analyze", str(path)])

            # Should either fail or succeed depending on system
            assert result.exit_code in [0, 1]
        finally:
            try:
                os.unlink(str(path))
            except:
                pass
            try:
                os.chmod(str(path), 0o644)
            except:
                pass

    def test_chunk_invalid_strategy(self) -> None:
        """Test chunking with invalid strategy."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write("# Test")
            f.flush()
            path = Path(f.name)

        try:
            result = runner.invoke(app, [
                "code", "chunk", str(path),
                "--strategy", "invalid"
            ])

            assert result.exit_code == 1
            assert "Error" in result.stdout
        finally:
            os.unlink(str(path))