#!/usr/bin/env python3
"""Quick verification script for Phase 1 & 2 fixes."""

import sys
from pathlib import Path

print("=" * 80)
print("PHASE 1 & 2 VERIFICATION")
print("=" * 80)

# Test 1: Import all modified modules
print("\n[Test 1] Importing modified modules...")
try:
    from app.modules.search.schema import DocumentChunkResult
    from app.modules.search.service import SearchService
    from app.modules.ingestion.language_parser import LanguageParser, build_semantic_summary
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Verify DocumentChunkResult has new fields
print("\n[Test 2] Checking DocumentChunkResult schema...")
required_fields = {
    'file_name', 'github_uri', 'branch_reference', 'start_line', 'end_line',
    'symbol_name', 'ast_node_type', 'semantic_summary', 'code', 'source', 'cache_hit'
}
schema_fields = set(DocumentChunkResult.model_fields.keys())
missing = required_fields - schema_fields
if missing:
    print(f"❌ Missing fields: {missing}")
    sys.exit(1)
print(f"✅ All required fields present: {len(required_fields)} fields")

# Test 3: Verify LanguageParser supports expected languages
print("\n[Test 3] Checking LanguageParser language support...")
supported = LanguageParser.supported_extensions()
expected = {'.c', '.h', '.cpp', '.go', '.rs', '.js', '.ts', '.tsx'}
if not expected.issubset(supported):
    missing = expected - supported
    print(f"❌ Missing language support: {missing}")
    sys.exit(1)
print(f"✅ All expected languages supported: {len(supported)} extensions")

# Test 4: Test LanguageParser on sample code
print("\n[Test 4] Testing LanguageParser extraction...")
test_cases = [
    (".go", """package main
import "fmt"
func Hello() string {
    return "world"
}
"""),
    (".rs", """use std::io;
fn main() {
    println!("Hello");
}
"""),
    (".ts", """import { Component } from 'react';
export function greet(name: string): string {
    return `Hello ${name}`;
}
"""),
]

for ext, code in test_cases:
    parser = LanguageParser.for_path(Path(f"test{ext}"))
    if parser is None:
        print(f"❌ Failed to create parser for {ext}")
        sys.exit(1)
    
    symbols = parser.extract(code, f"test{ext}")
    if not symbols:
        print(f"❌ No symbols extracted from {ext}")
        sys.exit(1)
    
    # Check for function definitions (not just imports)
    funcs = [s for s in symbols if s.node_type in ('function', 'method')]
    if not funcs:
        print(f"❌ No functions found in {ext} sample")
        sys.exit(1)
    
    print(f"  ✅ {ext}: extracted {len(symbols)} symbols ({len(funcs)} functions)")

# Test 5: Verify semantic summary format
print("\n[Test 5] Testing semantic summary generation...")
from app.modules.ingestion.language_parser import SymbolInfo

test_symbol = SymbolInfo(
    name="test_func",
    qualified_name="module.test_func",
    node_type="function",
    start_line=10,
    end_line=15,
    signature="func test_func(x int) string",
    docstring="Test function",
    dependencies=["fmt.Println", "strings.Join"]
)

summary = build_semantic_summary(test_symbol, "go")
if not summary:
    print("❌ Empty semantic summary")
    sys.exit(1)

if "[go]" not in summary:
    print("❌ Language tag missing from summary")
    sys.exit(1)

if "deps:" not in summary:
    print("❌ Dependencies missing from summary")
    sys.exit(1)

print(f"✅ Semantic summary format correct ({len(summary)} chars)")

# Test 6: Verify from_orm_chunk classmethod exists
print("\n[Test 6] Checking DocumentChunkResult.from_orm_chunk...")
if not hasattr(DocumentChunkResult, 'from_orm_chunk'):
    print("❌ from_orm_chunk classmethod missing")
    sys.exit(1)
print("✅ from_orm_chunk classmethod exists")

print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED")
print("=" * 80)
print("\nNext steps:")
print("1. Start the API server: uvicorn app.main:app --reload")
print("2. Test search with: POST /api/search/advanced with include_code=true")
print("3. Re-ingest a non-Python repo to test polyglot AST extraction")
print("=" * 80)
