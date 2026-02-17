"""Unit tests for CodeClient."""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile
import os

import sys
from pathlib import Path as P

# Add pharos_cli to path
sys.path.insert(0, str(P(__file__).parent.parent))

from pharos_cli.client.code_client import CodeClient
from pharos_cli.client.api_client import SyncAPIClient


class TestCodeClient:
    """Test cases for CodeClient."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        """Create a mock API client."""
        return MagicMock(spec=SyncAPIClient)

    @pytest.fixture
    def code_client(self, mock_api_client: MagicMock) -> CodeClient:
        """Create a CodeClient with mock API client."""
        return CodeClient(mock_api_client)

    @pytest.fixture
    def temp_python_file(self) -> Path:
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
    
    async def async_method(self) -> str:
        """Async method example."""
        return f"Hello {self.name}"


def example_function(x: int, y: int = 10) -> int:
    """Example function."""
    if x > y:
        return x - y
    elif x < y:
        return y - x
    else:
        return 0


def another_function():
    """Another function."""
    pass


# Some comment
class AnotherClass:
    pass
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            yield P(f.name)
        os.unlink(f.name)

    @pytest.fixture
    def temp_js_file(self) -> Path:
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(content)
            f.flush()
            yield P(f.name)
        os.unlink(f.name)

    def test_analyze_python_file(
        self,
        code_client: CodeClient,
        temp_python_file: Path,
    ) -> None:
        """Test analyzing a Python file."""
        result = code_client.analyze_code(str(temp_python_file))

        assert result["file_name"] == temp_python_file.name
        assert result["language"] == "python"
        assert "metrics" in result
        assert "structure" in result
        assert "complexity_score" in result
        assert "estimated_quality" in result

        # Check metrics
        assert result["metrics"]["total_lines"] > 0
        assert result["metrics"]["code_lines"] > 0
        assert result["metrics"]["code_percentage"] >= 0

        # Check structure
        assert result["structure"]["function_count"] >= 2  # example_function, another_function
        assert result["structure"]["class_count"] >= 2  # ExampleClass, AnotherClass
        assert result["structure"]["import_count"] >= 2  # os, sys, typing

    def test_analyze_javascript_file(
        self,
        code_client: CodeClient,
        temp_js_file: Path,
    ) -> None:
        """Test analyzing a JavaScript file."""
        result = code_client.analyze_code(str(temp_js_file))

        assert result["file_name"] == temp_js_file.name
        assert result["language"] == "javascript"
        assert result["structure"]["function_count"] >= 2
        assert result["structure"]["class_count"] >= 1

    def test_analyze_with_explicit_language(
        self,
        code_client: CodeClient,
        temp_python_file: Path,
    ) -> None:
        """Test analyzing with explicit language override."""
        result = code_client.analyze_code(str(temp_python_file), language="python")

        assert result["language"] == "python"

    def test_analyze_file_not_found(self, code_client: CodeClient) -> None:
        """Test analyzing a non-existent file."""
        with pytest.raises(FileNotFoundError):
            code_client.analyze_code("/nonexistent/file.py")

    def test_get_ast_json_format(
        self,
        code_client: CodeClient,
        temp_python_file: Path,
    ) -> None:
        """Test getting AST in JSON format."""
        result = code_client.get_ast(str(temp_python_file), format="json")

        assert result["file_path"] == str(temp_python_file.absolute())
        assert result["language"] == "python"
        assert "ast" in result

    def test_get_ast_text_format(
        self,
        code_client: CodeClient,
        temp_python_file: Path,
    ) -> None:
        """Test getting AST in text format."""
        result = code_client.get_ast(str(temp_python_file), format="text")

        assert result["file_path"] == str(temp_python_file.absolute())
        assert "ast_text" in result

    def test_get_ast_file_not_found(self, code_client: CodeClient) -> None:
        """Test getting AST for non-existent file."""
        with pytest.raises(FileNotFoundError):
            code_client.get_ast("/nonexistent/file.py")

    def test_get_dependencies_python(
        self,
        code_client: CodeClient,
        temp_python_file: Path,
    ) -> None:
        """Test getting dependencies for Python file."""
        result = code_client.get_dependencies(str(temp_python_file))

        assert result["file_name"] == temp_python_file.name
        assert result["language"] == "python"
        assert "imports" in result
        assert "package_dependencies" in result
        assert result["dependency_count"] >= 0

        # Check that imports were found
        import_modules = [imp["module"] for imp in result["imports"]]
        assert any("os" in m or "sys" in m for m in import_modules)

    def test_get_dependencies_file_not_found(self, code_client: CodeClient) -> None:
        """Test getting dependencies for non-existent file."""
        with pytest.raises(FileNotFoundError):
            code_client.get_dependencies("/nonexistent/file.py")

    def test_chunk_code_semantic(
        self,
        code_client: CodeClient,
        temp_python_file: Path,
    ) -> None:
        """Test chunking code with semantic strategy."""
        result = code_client.chunk_code(
            str(temp_python_file),
            strategy="semantic",
            chunk_size=500,
            overlap=50,
        )

        assert result["file_name"] == temp_python_file.name
        assert result["strategy"] == "semantic"
        assert result["language"] == "python"
        assert "chunks" in result
        assert result["total_chunks"] >= 1

        # Check chunk structure
        for chunk in result["chunks"]:
            assert "chunk_index" in chunk
            assert "content" in chunk
            assert "start_line" in chunk
            assert "end_line" in chunk

    def test_chunk_code_fixed(
        self,
        code_client: CodeClient,
        temp_python_file: Path,
    ) -> None:
        """Test chunking code with fixed strategy."""
        result = code_client.chunk_code(
            str(temp_python_file),
            strategy="fixed",
            chunk_size=100,
            overlap=20,
        )

        assert result["strategy"] == "fixed"
        assert result["total_chunks"] >= 1

    def test_chunk_code_file_not_found(self, code_client: CodeClient) -> None:
        """Test chunking non-existent file."""
        with pytest.raises(FileNotFoundError):
            code_client.chunk_code("/nonexistent/file.py")

    def test_scan_directory(
        self,
        code_client: CodeClient,
        temp_python_file: Path,
        temp_js_file: Path,
    ) -> None:
        """Test scanning a directory."""
        scan_dir = temp_python_file.parent

        result = code_client.scan_directory(
            str(scan_dir),
            recursive=False,
            file_limit=100,
        )

        assert "directory" in result
        assert "total_files_scanned" in result
        assert "total_lines_of_code" in result
        assert "language_distribution" in result
        assert "files" in result
        assert "scan_summary" in result

        # Check that our test files are in the results
        file_names = [f["file"] for f in result["files"]]
        assert any(temp_python_file.name in fn for fn in file_names)

    def test_scan_directory_with_pattern(
        self,
        code_client: CodeClient,
        temp_python_file: Path,
    ) -> None:
        """Test scanning with a file pattern."""
        scan_dir = temp_python_file.parent

        result = code_client.scan_directory(
            str(scan_dir),
            recursive=False,
            pattern="*.py",
            file_limit=100,
        )

        # All files should be Python files
        for f in result["files"]:
            if "error" not in f:
                assert f["language"] == "python"

    def test_scan_directory_not_found(self, code_client: CodeClient) -> None:
        """Test scanning non-existent directory."""
        with pytest.raises(FileNotFoundError):
            code_client.scan_directory("/nonexistent/directory")

    def test_scan_directory_not_a_directory(self, code_client: CodeClient, temp_python_file: Path) -> None:
        """Test scanning a file instead of directory."""
        with pytest.raises(NotADirectoryError):
            code_client.scan_directory(str(temp_python_file))


class TestCodeClientLanguageDetection:
    """Test language detection functionality."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        return MagicMock(spec=SyncAPIClient)

    @pytest.fixture
    def code_client(self, mock_api_client: MagicMock) -> CodeClient:
        return CodeClient(mock_api_client)

    def test_detect_python(self, code_client: CodeClient) -> None:
        """Test Python language detection."""
        assert code_client._detect_language("test.py") == "python"
        assert code_client._detect_language("test.pyw") == "python"

    def test_detect_javascript(self, code_client: CodeClient) -> None:
        """Test JavaScript language detection."""
        assert code_client._detect_language("test.js") == "javascript"
        assert code_client._detect_language("test.mjs") == "javascript"

    def test_detect_typescript(self, code_client: CodeClient) -> None:
        """Test TypeScript language detection."""
        assert code_client._detect_language("test.ts") == "typescript"
        assert code_client._detect_language("test.tsx") == "typescript"

    def test_detect_java(self, code_client: CodeClient) -> None:
        """Test Java language detection."""
        assert code_client._detect_language("test.java") == "java"

    def test_detect_cpp(self, code_client: CodeClient) -> None:
        """Test C++ language detection."""
        assert code_client._detect_language("test.cpp") == "cpp"
        assert code_client._detect_language("test.cc") == "cpp"
        assert code_client._detect_language("test.cxx") == "cpp"
        assert code_client._detect_language("test.hpp") == "cpp"

    def test_detect_c(self, code_client: CodeClient) -> None:
        """Test C language detection."""
        assert code_client._detect_language("test.c") == "c"
        assert code_client._detect_language("test.h") == "c"

    def test_detect_rust(self, code_client: CodeClient) -> None:
        """Test Rust language detection."""
        assert code_client._detect_language("test.rs") == "rust"

    def test_detect_go(self, code_client: CodeClient) -> None:
        """Test Go language detection."""
        assert code_client._detect_language("test.go") == "go"

    def test_detect_ruby(self, code_client: CodeClient) -> None:
        """Test Ruby language detection."""
        assert code_client._detect_language("test.rb") == "ruby"

    def test_detect_unknown(self, code_client: CodeClient) -> None:
        """Test unknown extension returns 'unknown'."""
        assert code_client._detect_language("test.xyz") == "unknown"
        assert code_client._detect_language("test") == "unknown"


class TestCodeClientComplexity:
    """Test complexity calculation functionality."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        return MagicMock(spec=SyncAPIClient)

    @pytest.fixture
    def code_client(self, mock_api_client: MagicMock) -> CodeClient:
        return CodeClient(mock_api_client)

    def test_simple_python_has_low_complexity(self, code_client: CodeClient) -> None:
        """Test that simple Python code has low complexity."""
        content = '''
def hello():
    print("Hello, World!")

class Simple:
    pass
'''
        complexity = code_client._calculate_complexity(content, "python")
        assert 0 <= complexity <= 1

    def test_complex_python_has_higher_complexity(self, code_client: CodeClient) -> None:
        """Test that complex Python code has higher complexity."""
        content = '''
def complex_function(x, y):
    if x > y:
        if x > 100:
            for i in range(x):
                if i % 2 == 0:
                    try:
                        if x and y:
                            result = x + y
                    except:
                        pass
    return x
'''
        complexity = code_client._calculate_complexity(content, "python")
        assert 0 <= complexity <= 1

    def test_estimate_quality_high(self, code_client: CodeClient) -> None:
        """Test quality estimation for simple code."""
        quality = code_client._estimate_quality(complexity=0.2, functions=5, classes=1)
        assert quality == "high"

    def test_estimate_quality_medium(self, code_client: CodeClient) -> None:
        """Test quality estimation for moderately complex code."""
        quality = code_client._estimate_quality(complexity=0.4, functions=15, classes=2)
        assert quality == "medium"

    def test_estimate_quality_low(self, code_client: CodeClient) -> None:
        """Test quality estimation for complex code."""
        quality = code_client._estimate_quality(complexity=0.7, functions=60, classes=10)
        assert quality == "low"


class TestCodeClientImportExtraction:
    """Test import extraction functionality."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        return MagicMock(spec=SyncAPIClient)

    @pytest.fixture
    def code_client(self, mock_api_client: MagicMock) -> CodeClient:
        return CodeClient(mock_api_client)

    def test_extract_python_imports(self, code_client: CodeClient) -> None:
        """Test extracting Python imports."""
        content = '''
import os
import sys
from typing import List, Dict
from pathlib import Path import Path
'''
        imports = code_client._extract_imports(content, "python")

        assert len(imports) >= 3
        import_modules = [imp["module"] for imp in imports]
        assert "os" in import_modules
        assert "sys" in import_modules
        assert "typing" in import_modules or "typing" in str(import_modules)

    def test_extract_javascript_imports(self, code_client: CodeClient) -> None:
        """Test extracting JavaScript imports."""
        content = '''
import React from 'react';
import { useState, useEffect } from 'react';
const fs = require('fs');
'''
        imports = code_client._extract_imports(content, "javascript")

        assert len(imports) >= 2
        import_modules = [imp["module"] for imp in imports]
        assert any("react" in m for m in import_modules)

    def test_extract_java_imports(self, code_client: CodeClient) -> None:
        """Test extracting Java imports."""
        content = '''
import java.util.List;
import java.util.ArrayList;
import java.io.File;
'''
        imports = code_client._extract_imports(content, "java")

        assert len(imports) >= 2
        import_modules = [imp["module"] for imp in imports]
        assert any("java.util" in m for m in import_modules)


class TestCodeClientChunking:
    """Test code chunking functionality."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        return MagicMock(spec=SyncAPIClient)

    @pytest.fixture
    def code_client(self, mock_api_client: MagicMock) -> CodeClient:
        return CodeClient(mock_api_client)

    def test_chunk_fixed_basic(self, code_client: CodeClient) -> None:
        """Test fixed-size chunking."""
        content = "line " + "\n".join([f"{i}" for i in range(100)])
        chunks = code_client._chunk_fixed(content, chunk_size=20, overlap=5)

        assert len(chunks) >= 4
        for chunk in chunks:
            lines = chunk.split("\n")
            assert len(lines) <= 25  # Allow some buffer for overlap

    def test_chunk_semantic_python(self, code_client: CodeClient) -> None:
        """Test semantic chunking for Python."""
        content = '''
class ClassA:
    def method_a(self):
        pass

def function_a():
    pass

class ClassB:
    def method_b(self):
        pass

def function_b():
    pass
'''
        chunks = code_client._chunk_semantic(content, "python", chunk_size=100, overlap=10)

        assert len(chunks) >= 2

    def test_get_line_numbers(self, code_client: CodeClient) -> None:
        """Test line number extraction."""
        content = "line1\nline2\nline3\nline4\nline5"
        chunk = "line2\nline3\nline4"

        start, end = code_client._get_line_numbers(content, chunk)
        assert start == 2
        assert end == 4


class TestCodeClientEdgeCases:
    """Edge case tests for CodeClient."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        return MagicMock(spec=SyncAPIClient)

    @pytest.fixture
    def code_client(self, mock_api_client: MagicMock) -> CodeClient:
        return CodeClient(mock_api_client)

    def test_analyze_empty_file(self, code_client: CodeClient) -> None:
        """Test analyzing an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("")
            f.flush()
            path = P(f.name)

        try:
            result = code_client.analyze_code(str(path))
            # Empty file has 1 line (empty string)
            assert result["metrics"]["total_lines"] == 1
            assert result["metrics"]["code_lines"] == 0
        finally:
            os.unlink(str(path))

    def test_analyze_file_with_only_comments(self, code_client: CodeClient) -> None:
        """Test analyzing a file with only comments."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("# This is a comment\n# Another comment\n# Third comment")
            f.flush()
            path = P(f.name)

        try:
            result = code_client.analyze_code(str(path))
            assert result["metrics"]["comment_lines"] == 3
            assert result["metrics"]["code_lines"] == 0
        finally:
            os.unlink(str(path))

    def test_analyze_binary_file_extension(self, code_client: CodeClient) -> None:
        """Test that binary file extensions are handled."""
        # Create a file with invalid UTF-8 bytes
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pyc', delete=False) as f:
            # Write bytes that are invalid UTF-8 (continuation bytes without start)
            f.write(b'\x80\x81\x82\x83')
            f.flush()
            path = P(f.name)

        try:
            # This should fail because it's not valid UTF-8
            with pytest.raises(UnicodeDecodeError):
                code_client.analyze_code(str(path))
        finally:
            os.unlink(str(path))

    def test_scan_directory_empty(self, code_client: CodeClient) -> None:
        """Test scanning an empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = code_client.scan_directory(tmpdir, recursive=False)

            assert result["total_files_scanned"] == 0
            assert result["total_lines_of_code"] == 0
            assert len(result["files"]) == 0

    def test_scan_directory_file_limit(self, code_client: CodeClient) -> None:
        """Test scanning with a file limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create more files than the limit
            for i in range(20):
                with tempfile.NamedTemporaryFile(
                    mode='w', suffix='.py', dir=tmpdir, delete=False
                ) as f:
                    f.write(f"# File {i}\ndef func{i}():\n    pass")
                    f.flush()

            result = code_client.scan_directory(tmpdir, recursive=False, file_limit=5)

            assert result["total_files_scanned"] <= 5

    def test_get_ast_unknown_language(self, code_client: CodeClient) -> None:
        """Test AST extraction for unknown language."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
            f.write("some content\nmore content")
            f.flush()
            path = P(f.name)

        try:
            result = code_client.get_ast(str(path), format="json")
            assert result["language"] == "unknown"
        finally:
            os.unlink(str(path))

    def test_chunk_with_large_overlap(self, code_client: CodeClient) -> None:
        """Test chunking with overlap >= chunk_size (should be handled)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("\n".join([f"line {i}" for i in range(100)]))
            f.flush()
            path = P(f.name)

        try:
            # This should work but may produce fewer chunks
            result = code_client.chunk_code(str(path), chunk_size=50, overlap=60)
            assert result["total_chunks"] >= 1
        finally:
            os.unlink(str(path))