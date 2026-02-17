"""Code client for Pharos CLI."""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from pharos_cli.client.api_client import SyncAPIClient


class CodeClient:
    """Client for code analysis operations."""

    def __init__(self, api_client: SyncAPIClient):
        """Initialize the code client.

        Args:
            api_client: The sync API client instance.
        """
        self.api = api_client

    def analyze_code(
        self,
        file_path: str,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyze a code file for metrics and quality.

        Args:
            file_path: Path to the code file.
            language: Programming language (auto-detected if not provided).

        Returns:
            Analysis results including metrics, complexity, and quality indicators.
        """
        file = Path(file_path)
        if not file.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = file.read_text(encoding="utf-8")

        # Auto-detect language if not provided
        if not language:
            language = self._detect_language(file_path)

        # Basic metrics
        lines = content.split("\n")
        total_lines = len(lines)
        code_lines = len([l for l in lines if l.strip() and not l.strip().startswith("#") and not l.strip().startswith("//")])
        comment_lines = len([l for l in lines if l.strip().startswith("#") or l.strip().startswith("//")])
        blank_lines = total_lines - code_lines - comment_lines

        # Calculate complexity indicators
        functions = self._count_functions(content, language)
        classes = self._count_classes(content, language)
        imports = self._count_imports(content, language)

        # Calculate complexity score (simple heuristic)
        complexity_score = self._calculate_complexity(content, language)

        return {
            "file_path": str(file.absolute()),
            "file_name": file.name,
            "language": language,
            "metrics": {
                "total_lines": total_lines,
                "code_lines": code_lines,
                "comment_lines": comment_lines,
                "blank_lines": blank_lines,
                "code_percentage": round(code_lines / total_lines * 100, 2) if total_lines > 0 else 0,
            },
            "structure": {
                "function_count": functions,
                "class_count": classes,
                "import_count": imports,
            },
            "complexity_score": complexity_score,
            "estimated_quality": self._estimate_quality(complexity_score, functions, classes),
        }

    def get_ast(
        self,
        file_path: str,
        format: str = "json",
    ) -> Dict[str, Any]:
        """Extract Abstract Syntax Tree from a code file.

        Args:
            file_path: Path to the code file.
            format: Output format (json, text).

        Returns:
            AST representation of the code.
        """
        file = Path(file_path)
        if not file.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = file.read_text(encoding="utf-8")
        language = self._detect_language(file_path)

        # Try to use tree-sitter if available
        try:
            import tree_sitter

            # Get language
            lang_name = self._get_treesitter_language(language)
            if lang_name:
                parser = tree_sitter.Parser()
                try:
                    language_obj = getattr(tree_sitter, lang_name)
                    parser = tree_sitter.Parser(language_obj)
                    tree = parser.parse(content.encode())

                    if format == "json":
                        return {
                            "file_path": str(file.absolute()),
                            "language": language,
                            "ast": json.loads(tree.root_node.sexp()),
                        }
                    else:
                        return {
                            "file_path": str(file.absolute()),
                            "language": language,
                            "ast_text": tree.root_node.sexp(),
                        }
                except (AttributeError, TypeError):
                    pass  # Fall back to simple parsing
            else:
                pass  # Fall back to simple parsing
        except ImportError:
            pass  # tree-sitter not available

        # Fall back to simple AST extraction
        return self._simple_ast_extraction(file, content, language, format)

    def get_dependencies(
        self,
        file_path: str,
        include_transitive: bool = False,
    ) -> Dict[str, Any]:
        """Extract dependencies from a code file.

        Args:
            file_path: Path to the code file.
            include_transitive: Include transitive dependencies.

        Returns:
            Dependency information including imports and requirements.
        """
        file = Path(file_path)
        if not file.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = file.read_text(encoding="utf-8")
        language = self._detect_language(file_path)

        # Extract imports based on language
        imports = self._extract_imports(content, language)

        # Extract package dependencies if applicable
        package_deps = self._extract_package_deps(file, language)

        return {
            "file_path": str(file.absolute()),
            "file_name": file.name,
            "language": language,
            "imports": imports,
            "package_dependencies": package_deps,
            "dependency_count": len(imports) + len(package_deps),
        }

    def chunk_code(
        self,
        file_path: str,
        strategy: str = "semantic",
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> Dict[str, Any]:
        """Chunk a code file for indexing.

        Args:
            file_path: Path to the code file.
            strategy: Chunking strategy (semantic, fixed).
            chunk_size: Target chunk size.
            overlap: Overlap between chunks.

        Returns:
            List of chunks with metadata.
        """
        file = Path(file_path)
        if not file.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = file.read_text(encoding="utf-8")
        language = self._detect_language(file_path)

        if strategy == "fixed":
            chunks = self._chunk_fixed(content, chunk_size, overlap)
        else:
            chunks = self._chunk_semantic(content, language, chunk_size, overlap)

        return {
            "file_path": str(file.absolute()),
            "file_name": file.name,
            "language": language,
            "strategy": strategy,
            "chunk_size": chunk_size,
            "overlap": overlap,
            "chunks": [
                {
                    "chunk_index": i,
                    "content": chunk,
                    "start_line": self._get_line_numbers(content, chunk)[0],
                    "end_line": self._get_line_numbers(content, chunk)[1],
                }
                for i, chunk in enumerate(chunks)
            ],
            "total_chunks": len(chunks),
        }

    def scan_directory(
        self,
        directory: str,
        recursive: bool = True,
        pattern: Optional[str] = None,
        file_limit: int = 1000,
    ) -> Dict[str, Any]:
        """Scan a directory for code files and analyze them.

        Args:
            directory: Directory to scan.
            recursive: Scan subdirectories recursively.
            pattern: File pattern to match (glob format).
            file_limit: Maximum number of files to process.

        Returns:
            Scan results with file list and summary.
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")

        # Find files
        if pattern:
            if recursive:
                files = list(dir_path.rglob(pattern))
            else:
                files = list(dir_path.glob(pattern))
        else:
            # Default code file patterns
            extensions = ["*.py", "*.js", "*.ts", "*.java", "*.c", "*.cpp", "*.h", "*.cs", "*.go", "*.rs", "*.rb", "*.php"]
            if recursive:
                files = []
                for ext in extensions:
                    files.extend(dir_path.rglob(ext))
            else:
                files = []
                for ext in extensions:
                    files.extend(dir_path.glob(ext))

        # Sort and limit
        files = sorted(files)[:file_limit]

        # Analyze each file
        results = []
        total_lines = 0
        total_files = len(files)
        language_counts: Dict[str, int] = {}

        for file_path in files:
            try:
                analysis = self.analyze_code(str(file_path))
                results.append({
                    "file": str(file_path.relative_to(dir_path)),
                    "language": analysis["language"],
                    "lines": analysis["metrics"]["total_lines"],
                    "complexity": analysis["complexity_score"],
                })
                total_lines += analysis["metrics"]["total_lines"]
                lang = analysis["language"]
                language_counts[lang] = language_counts.get(lang, 0) + 1
            except Exception as e:
                results.append({
                    "file": str(file_path.relative_to(dir_path)),
                    "error": str(e),
                })

        return {
            "directory": str(dir_path.absolute()),
            "recursive": recursive,
            "total_files_scanned": total_files,
            "total_lines_of_code": total_lines,
            "language_distribution": language_counts,
            "files": results,
            "scan_summary": {
                "largest_file": max(results, key=lambda x: x.get("lines", 0)) if results else None,
                "most_common_language": max(language_counts, key=language_counts.get) if language_counts else None,
                "average_complexity": sum(f.get("complexity", 0) for f in results if "complexity" in f) / len(results) if results else 0,
            },
        }

    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = Path(file_path).suffix.lower()

        language_map = {
            ".py": "python",
            ".pyw": "python",
            ".js": "javascript",
            ".mjs": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".cxx": "cpp",
            ".h": "c",
            ".hpp": "cpp",
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
            ".bash": "shell",
            ".zsh": "shell",
            ".html": "html",
            ".htm": "html",
            ".css": "css",
            ".scss": "scss",
            ".sql": "sql",
            ".md": "markdown",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".xml": "xml",
        }

        return language_map.get(ext, "unknown")

    def _get_treesitter_language(self, language: str) -> Optional[str]:
        """Get tree-sitter language constant name."""
        ts_languages = {
            "python": "PYTHON",
            "javascript": "JAVASCRIPT",
            "typescript": "TYPESCRIPT",
            "java": "JAVA",
            "c": "C",
            "cpp": "CPP",
            "csharp": "CSHARP",
            "go": "GO",
            "rust": "RUST",
            "ruby": "RUBY",
            "php": "PHP",
            "swift": "SWIFT",
            "kotlin": "KOTLIN",
            "scala": "SCALA",
            "html": "HTML",
            "css": "CSS",
            "sql": "SQL",
            "bash": "BASH",
            "shell": "BASH",
        }
        return ts_languages.get(language.lower())

    def _count_functions(self, content: str, language: str) -> int:
        """Count functions in code."""
        if language == "python":
            import re
            # Match def and async def
            matches = re.findall(r"^\s*(?:async\s+)?def\s+\w+\s*\(", content, re.MULTILINE)
            return len(matches)
        elif language in ["javascript", "typescript"]:
            import re
            # Match function declarations, arrow functions, and methods
            matches = re.findall(r"(?:function\s+\w+|\w+\s*=\s*(?:async\s+)?function|\w+\s*:\s*(?:async\s+)?function|(?:async\s+)?\(\s*\)\s*=>|\w+\s*\([^)]*\)\s*\{)", content)
            return len(matches)
        elif language in ["java", "csharp", "cpp", "c", "go", "rust"]:
            import re
            # Match method/function declarations
            pattern = r"(?:public|private|protected|static|\s)*\s*(?:void|int|str|bool|auto|let|const|var|\w+)\s+\w+\s*\("
            matches = re.findall(pattern, content)
            return len(matches)
        return 0

    def _count_classes(self, content: str, language: str) -> int:
        """Count classes in code."""
        import re

        if language == "python":
            matches = re.findall(r"^\s*class\s+\w+", content, re.MULTILINE)
        elif language in ["java", "csharp", "cpp"]:
            matches = re.findall(r"(?:public|private|protected)?\s*class\s+\w+", content)
        elif language == "rust":
            matches = re.findall(r"(?:pub\s+)?struct\s+\w+", content)
        else:
            matches = re.findall(r"class\s+\w+", content)

        return len(matches)

    def _count_imports(self, content: str, language: str) -> int:
        """Count import statements."""
        import re

        if language == "python":
            matches = re.findall(r"^(?:import|from)\s+", content, re.MULTILINE)
        elif language in ["javascript", "typescript"]:
            matches = re.findall(r"(?:import|require)\s*\(", content)
        elif language in ["java", "csharp"]:
            matches = re.findall(r"^import\s+", content, re.MULTILINE)
        else:
            matches = re.findall(r"import\s+", content)

        return len(matches)

    def _calculate_complexity(self, content: str, language: str) -> float:
        """Calculate a simple complexity score."""
        # Base complexity on nesting depth and control structures
        import re

        # Count control structures
        patterns = [
            r"\bif\b",
            r"\belse\b",
            r"\belif\b",
            r"\bfor\b",
            r"\bwhile\b",
            r"\btry\b",
            r"\bexcept\b",
            r"\bwith\b",
            r"\blambda\b",
        ]

        total_control = 0
        for pattern in patterns:
            total_control += len(re.findall(pattern, content))

        # Count functions/classes as additional complexity
        functions = self._count_functions(content, language)
        classes = self._count_classes(content, language)

        # Calculate score (0-1 range)
        lines = len(content.split("\n"))
        base_score = (total_control + functions * 2 + classes * 3) / max(lines, 1)

        return min(round(base_score * 10, 2), 1.0)

    def _estimate_quality(self, complexity: float, functions: int, classes: int) -> str:
        """Estimate code quality based on metrics."""
        if complexity < 0.3 and functions < 20 and classes < 5:
            return "high"
        elif complexity < 0.6 and functions < 50:
            return "medium"
        else:
            return "low"

    def _extract_imports(self, content: str, language: str) -> List[Dict[str, str]]:
        """Extract import statements from code."""
        imports = []
        import re

        if language == "python":
            # Match 'import x' and 'from x import y'
            import re
            for match in re.finditer(r"^(?:from\s+(\S+)\s+import\s+(.+)|import\s+(.+))", content, re.MULTILINE):
                groups = match.groups()
                if groups[0]:  # from x import y
                    for item in groups[1].split(","):
                        imports.append({
                            "module": groups[0],
                            "item": item.strip(),
                            "type": "from",
                        })
                elif groups[2]:  # import x
                    for item in groups[2].split(","):
                        imports.append({
                            "module": item.strip(),
                            "item": None,
                            "type": "import",
                        })
        elif language in ["javascript", "typescript"]:
            # Match import and require statements
            # Handle: import x from 'module', import {x} from 'module', import * as x from 'module'
            import_pattern = r'import\s+(?:\{[^}]*\}|\*\s+as\s+\w+|\w+)\s+from\s+["\']([^"\']+)["\']'
            for match in re.finditer(import_pattern, content):
                imports.append({
                    "module": match.group(1),
                    "item": None,
                    "type": "import",
                })
            # Handle: require('module')
            require_pattern = r'require\s*\(\s*["\']([^"\']+)["\']\s*\)'
            for match in re.finditer(require_pattern, content):
                imports.append({
                    "module": match.group(1),
                    "item": None,
                    "type": "require",
                })
        elif language in ["java", "csharp"]:
            for match in re.finditer(r"import\s+([\w.]+);", content):
                imports.append({
                    "module": match.group(1),
                    "item": None,
                    "type": "import",
                })
        elif language == "go":
            for match in re.finditer(r'(?:import\s*\(([^)]*)\|"([^"]+)")', content):
                for module in (match.group(1) or match.group(2)).split("\n"):
                    module = module.strip().strip('"')
                    if module:
                        imports.append({
                            "module": module,
                            "item": None,
                            "type": "import",
                        })
        elif language == "rust":
            for match in re.finditer(r'use\s+([\w:]+);', content):
                imports.append({
                    "module": match.group(1),
                    "item": None,
                    "type": "use",
                })

        return imports[:50]  # Limit to 50 imports

    def _extract_package_deps(self, file: Path, language: str) -> List[Dict[str, str]]:
        """Extract package dependencies from dependency files."""
        deps = []

        # Check for common dependency files
        if language == "python":
            req_file = file.parent / "requirements.txt"
            if req_file.exists():
                for line in req_file.read_text().split("\n"):
                    line = line.strip()
                    if line and not line.startswith("#"):
                        deps.append({"file": "requirements.txt", "dependency": line})
        elif language in ["javascript", "typescript"]:
            pkg_file = file.parent / "package.json"
            if pkg_file.exists():
                try:
                    pkg = json.loads(pkg_file.read_text())
                    for dep in pkg.get("dependencies", {}):
                        version = pkg["dependencies"][dep]
                        deps.append({"file": "package.json", "dependency": f"{dep}@{version}"})
                except json.JSONDecodeError:
                    pass
        elif language == "rust":
            cargo_file = file.parent / "Cargo.toml"
            if cargo_file.exists():
                content = cargo_file.read_text()
                # Simple parsing for dependencies
                import re
                for match in re.finditer(r'(\w+)\s*=\s*"([^"]+)"', content):
                    deps.append({"file": "Cargo.toml", "dependency": f"{match.group(1)}={match.group(2)}"})

        return deps

    def _simple_ast_extraction(
        self,
        file: Path,
        content: str,
        language: str,
        format: str = "json",
    ) -> Dict[str, Any]:
        """Simple AST extraction without tree-sitter."""
        import re

        # Extract top-level definitions
        definitions = []

        if language == "python":
            # Find classes
            for match in re.finditer(r"^class\s+(\w+)(?:\(([^)]+)\))?:", content, re.MULTILINE):
                definitions.append({
                    "type": "class",
                    "name": match.group(1),
                    "bases": match.group(2).split(",") if match.group(2) else [],
                })

            # Find functions
            for match in re.finditer(r"^(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\):", content, re.MULTILINE):
                params = [p.strip().split(":")[0].split("=")[0] for p in match.group(2).split(",") if p.strip()]
                definitions.append({
                    "type": "function",
                    "name": match.group(1),
                    "parameters": params,
                })

        elif language in ["javascript", "typescript"]:
            # Find classes
            for match in re.finditer(r"class\s+(\w+)(?:\s+extends\s+(\w+))?", content):
                definitions.append({
                    "type": "class",
                    "name": match.group(1),
                    "bases": [match.group(2)] if match.group(2) else [],
                })

            # Find functions
            for match in re.finditer(r"(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s+)?function)", content):
                name = match.group(1) or match.group(2)
                definitions.append({
                    "type": "function",
                    "name": name,
                    "parameters": [],
                })

        elif language in ["java", "csharp", "cpp"]:
            # Find classes
            for match in re.finditer(r"(?:public|private|protected)?\s*class\s+(\w+)", content):
                definitions.append({
                    "type": "class",
                    "name": match.group(1),
                    "bases": [],
                })

            # Find methods
            for match in re.finditer(r"(?:public|private|protected|static)?\s*(?:void|int|str|bool|\w+)\s+(\w+)\s*\(([^)]*)\)", content):
                params = [p.strip().split()[-1] for p in match.group(2).split(",") if p.strip()]
                definitions.append({
                    "type": "method",
                    "name": match.group(1),
                    "parameters": params,
                })

        if format == "json":
            return {
                "file_path": str(file.absolute()),
                "language": language,
                "ast": {
                    "type": "module",
                    "definitions": definitions,
                },
            }
        else:
            return {
                "file_path": str(file.absolute()),
                "language": language,
                "ast_text": "\n".join([f"{d['type']}: {d['name']}" for d in definitions]),
            }

    def _chunk_fixed(
        self,
        content: str,
        chunk_size: int,
        overlap: int,
    ) -> List[str]:
        """Chunk content with fixed size."""
        lines = content.split("\n")
        chunks = []

        # Handle edge case where overlap >= chunk_size
        if overlap >= chunk_size:
            overlap = chunk_size - 1
            if overlap < 0:
                overlap = 0

        for i in range(0, len(lines), chunk_size - overlap):
            chunk_lines = lines[i : i + chunk_size]
            if chunk_lines:
                chunks.append("\n".join(chunk_lines))

        return chunks

    def _chunk_semantic(
        self,
        content: str,
        language: str,
        chunk_size: int,
        overlap: int,
    ) -> List[str]:
        """Chunk content semantically (by function/class boundaries)."""
        import re

        chunks = []
        lines = content.split("\n")

        if language == "python":
            # Split by class and function definitions
            pattern = r"^(class|def|async def)\s+"
            boundaries = []

            for i, line in enumerate(lines):
                if re.match(pattern, line):
                    boundaries.append(i)

            boundaries.append(len(lines))

            # If no boundaries found, use fixed chunking
            if len(boundaries) <= 1:
                return self._chunk_fixed(content, chunk_size, overlap)

            for i in range(len(boundaries) - 1):
                start = max(0, boundaries[i] - overlap if i > 0 else 0)
                end = min(len(lines), boundaries[i + 1] + overlap if i + 1 < len(boundaries) - 1 else len(lines))
                chunk_lines = lines[start:end]

                # If chunk is too large, use fixed chunking
                if len(chunk_lines) > chunk_size * 2:
                    for j in range(0, len(chunk_lines), chunk_size - overlap):
                        sub_chunk = chunk_lines[j : j + chunk_size]
                        if sub_chunk:
                            chunks.append("\n".join(sub_chunk))
                else:
                    chunks.append("\n".join(chunk_lines))

        else:
            # For other languages, use fixed chunking
            chunks = self._chunk_fixed(content, chunk_size, overlap)

        return chunks

    def _get_line_numbers(self, content: str, chunk: str) -> tuple:
        """Get start and end line numbers for a chunk."""
        lines = content.split("\n")
        chunk_lines = chunk.split("\n")

        # Find the chunk in the content
        for i in range(len(lines) - len(chunk_lines) + 1):
            if lines[i : i + len(chunk_lines)] == chunk_lines:
                return (i + 1, i + len(chunk_lines))

        return (0, len(chunk_lines))