#!/usr/bin/env python3
"""Pre-deployment verification script.

Runs all checks to ensure Phase 1 & 2 are ready for production deployment.
"""

import sys
import subprocess
from pathlib import Path

print("=" * 80)
print("PRE-DEPLOYMENT VERIFICATION")
print("=" * 80)

checks_passed = 0
checks_failed = 0

def check(name: str, passed: bool, details: str = ""):
    global checks_passed, checks_failed
    if passed:
        print(f"✅ {name}")
        if details:
            print(f"   {details}")
        checks_passed += 1
    else:
        print(f"❌ {name}")
        if details:
            print(f"   {details}")
        checks_failed += 1
    return passed

print("\n[1] Checking file modifications...")
modified_files = [
    "app/modules/search/schema.py",
    "app/modules/search/service.py",
    "app/modules/search/router.py",
    "app/modules/ingestion/language_parser.py",
    "app/modules/ingestion/ast_pipeline.py",
    "config/requirements-base.txt",
]

for file in modified_files:
    path = Path(file)
    check(f"File exists: {file}", path.exists())

print("\n[2] Checking Python syntax...")
syntax_ok = True
for file in modified_files:
    if file.endswith('.py'):
        result = subprocess.run(
            ["python", "-m", "py_compile", file],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            check(f"Syntax: {file}", False, result.stderr[:100])
            syntax_ok = False

if syntax_ok:
    check("All Python files compile", True)

print("\n[3] Checking imports...")
try:
    from app.modules.search.schema import DocumentChunkResult
    from app.modules.search.service import SearchService
    from app.modules.ingestion.language_parser import LanguageParser
    check("All imports successful", True)
except Exception as e:
    check("All imports successful", False, str(e))

print("\n[4] Checking schema fields...")
try:
    required_fields = {
        'file_name', 'github_uri', 'branch_reference', 'start_line', 'end_line',
        'symbol_name', 'ast_node_type', 'semantic_summary', 'code', 'source', 'cache_hit'
    }
    schema_fields = set(DocumentChunkResult.model_fields.keys())
    missing = required_fields - schema_fields
    check(
        "DocumentChunkResult has all fields",
        len(missing) == 0,
        f"Missing: {missing}" if missing else f"{len(required_fields)} fields present"
    )
except Exception as e:
    check("DocumentChunkResult has all fields", False, str(e))

print("\n[5] Checking LanguageParser...")
try:
    supported = LanguageParser.supported_extensions()
    expected = {'.c', '.h', '.cpp', '.go', '.rs', '.js', '.ts', '.tsx'}
    check(
        "LanguageParser supports expected languages",
        expected.issubset(supported),
        f"{len(supported)} extensions supported"
    )
except Exception as e:
    check("LanguageParser supports expected languages", False, str(e))

print("\n[6] Checking requirements.txt...")
req_file = Path("config/requirements-base.txt")
if req_file.exists():
    content = req_file.read_text()
    required_packages = [
        "tree-sitter",
        "tree-sitter-c",
        "tree-sitter-cpp",
        "tree-sitter-go",
        "tree-sitter-rust",
        "tree-sitter-javascript",
        "tree-sitter-typescript",
    ]
    all_present = all(pkg in content for pkg in required_packages)
    check(
        "requirements-base.txt has tree-sitter packages",
        all_present,
        f"{len([p for p in required_packages if p in content])}/{len(required_packages)} packages"
    )
else:
    check("requirements-base.txt exists", False)

print("\n[7] Running unit tests...")
import os
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'
result = subprocess.run(
    ["python", "test_fixes.py"],
    capture_output=True,
    text=True,
    env=env
)
tests_passed = "ALL TESTS PASSED" in result.stdout
check(
    "Unit tests pass",
    tests_passed,
    "6/6 tests passed" if tests_passed else "Some tests failed"
)

if not tests_passed and result.stdout:
    print("\nTest output:")
    print(result.stdout[-500:])  # Last 500 chars

print("\n" + "=" * 80)
print(f"VERIFICATION RESULTS: {checks_passed} passed, {checks_failed} failed")
print("=" * 80)

if checks_failed == 0:
    print("\n✅ ALL CHECKS PASSED - READY FOR DEPLOYMENT")
    print("\nNext steps:")
    print("1. git add backend/ *.md")
    print("2. git commit -m 'feat: Phase 1 & 2 - Search fixes + polyglot AST'")
    print("3. git push origin main")
    print("4. Monitor Render deployment")
    sys.exit(0)
else:
    print(f"\n❌ {checks_failed} CHECKS FAILED - FIX BEFORE DEPLOYING")
    print("\nReview errors above and fix issues before deployment.")
    sys.exit(1)
