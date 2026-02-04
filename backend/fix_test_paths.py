#!/usr/bin/env python3
"""
Fix test endpoint paths to include /api prefix.

All module routers use /api/* prefixes, but many tests still use the old paths
without /api. This script updates all test files to use the correct paths.
"""

import re
from pathlib import Path

# Mapping of old paths to new paths
PATH_MAPPINGS = {
    '"/collections/': '"/api/collections/',
    '"/resources/': '"/api/resources/',
    '"/search/': '"/api/search/',
    '"/annotations/': '"/api/annotations/',
    '"/scholarly/': '"/api/scholarly/',
    '"/authority/': '"/api/authority/',
    '"/curation/': '"/api/curation/',
    '"/quality/': '"/api/quality/',
    '"/taxonomy/': '"/api/taxonomy/',
    '"/graph/': '"/api/graph/',
    '"/recommendations/': '"/api/recommendations/',
    '"/monitoring/': '"/api/monitoring/',
    "'/collections/": "'/api/collections/",
    "'/resources/": "'/api/resources/",
    "'/search/": "'/api/search/",
    "'/annotations/": "'/api/annotations/",
    "'/scholarly/": "'/api/scholarly/",
    "'/authority/": "'/api/authority/",
    "'/curation/": "'/api/curation/",
    "'/quality/": "'/api/quality/",
    "'/taxonomy/": "'/api/taxonomy/",
    "'/graph/": "'/api/graph/",
    "'/recommendations/": "'/api/recommendations/",
    "'/monitoring/": "'/api/monitoring/",
}

def fix_file(file_path: Path) -> tuple[bool, int]:
    """Fix paths in a single file. Returns (changed, num_replacements)."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        replacements = 0
        
        for old_path, new_path in PATH_MAPPINGS.items():
            if old_path in content:
                # Only replace if not already /api/
                # Avoid double-replacing
                if new_path not in content or content.count(old_path) > content.count(new_path):
                    count = content.count(old_path)
                    content = content.replace(old_path, new_path)
                    replacements += count
        
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return True, replacements
        return False, 0
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, 0

def main():
    """Fix all test files."""
    tests_dir = Path(__file__).parent / "tests"
    
    if not tests_dir.exists():
        print(f"Tests directory not found: {tests_dir}")
        return
    
    # Find all Python test files
    test_files = list(tests_dir.rglob("test_*.py"))
    
    print(f"Found {len(test_files)} test files")
    print("Fixing paths...\n")
    
    total_files_changed = 0
    total_replacements = 0
    
    for test_file in test_files:
        changed, replacements = fix_file(test_file)
        if changed:
            total_files_changed += 1
            total_replacements += replacements
            print(f"✓ {test_file.relative_to(tests_dir)}: {replacements} replacements")
    
    print(f"\nSummary:")
    print(f"  Files changed: {total_files_changed}")
    print(f"  Total replacements: {total_replacements}")
    
    if total_files_changed == 0:
        print("\n✓ All test files already use correct paths!")
    else:
        print(f"\n✓ Fixed {total_files_changed} test files")

if __name__ == "__main__":
    main()
