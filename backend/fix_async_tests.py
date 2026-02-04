#!/usr/bin/env python3
"""
Script to add @pytest.mark.asyncio decorator to async test functions.

This fixes the "async def functions are not natively supported" error.
"""

import re
from pathlib import Path


def add_asyncio_markers(file_path: Path) -> bool:
    """Add @pytest.mark.asyncio to async test functions."""
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    
    # Pattern to match async test functions without the decorator
    # Matches: async def test_something(...):
    # But not if preceded by @pytest.mark.asyncio
    pattern = r'(?<!@pytest\.mark\.asyncio\n)(?<!@pytest\.mark\.asyncio\r\n)(async def test_\w+\()'
    
    # Check if file needs fixing
    if not re.search(pattern, content):
        return False
    
    # Split into lines for processing
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is an async test function
        if line.strip().startswith('async def test_'):
            # Check if previous line already has the marker
            if i > 0 and '@pytest.mark.asyncio' in lines[i-1]:
                new_lines.append(line)
            else:
                # Add the marker with proper indentation
                indent = len(line) - len(line.lstrip())
                marker = ' ' * indent + '@pytest.mark.asyncio'
                new_lines.append(marker)
                new_lines.append(line)
        else:
            new_lines.append(line)
        
        i += 1
    
    new_content = '\n'.join(new_lines)
    
    if new_content != original_content:
        file_path.write_text(new_content, encoding='utf-8')
        return True
    
    return False


def main():
    """Process all test files in the auth module."""
    test_dir = Path(__file__).parent / 'tests' / 'modules' / 'auth'
    
    if not test_dir.exists():
        print(f"Error: {test_dir} does not exist")
        return
    
    fixed_files = []
    
    for test_file in test_dir.glob('test_*.py'):
        print(f"Processing {test_file.name}...", end=' ')
        if add_asyncio_markers(test_file):
            fixed_files.append(test_file.name)
            print("✓ Fixed")
        else:
            print("- No changes needed")
    
    print(f"\n✓ Fixed {len(fixed_files)} file(s)")
    if fixed_files:
        print("Fixed files:")
        for f in fixed_files:
            print(f"  - {f}")


if __name__ == '__main__':
    main()
