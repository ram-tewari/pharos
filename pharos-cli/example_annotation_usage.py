"""Example usage of annotation commands."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pharos_cli.cli import app
from typer.testing import CliRunner

def main():
    """Demonstrate annotation command usage."""
    runner = CliRunner()
    
    print("=== Pharos CLI Annotation Commands Demo ===\n")
    
    # Show main help
    print("1. Main help (showing annotation commands):")
    result = runner.invoke(app, ["--help"])
    annotation_lines = [line for line in result.stdout.split('\n') if 'annotate' in line.lower()]
    for line in annotation_lines[:3]:
        print(f"   {line}")
    print()
    
    # Show annotation command help
    print("2. Annotation command help:")
    result = runner.invoke(app, ["annotate", "--help"])
    lines = result.stdout.split('\n')
    for line in lines[:25]:
        print(f"   {line}")
    print()
    
    # Show create command help
    print("3. Annotation create command help:")
    result = runner.invoke(app, ["annotate", "create", "--help"])
    lines = result.stdout.split('\n')
    for line in lines[:15]:
        print(f"   {line}")
    print()
    
    # Show list command help
    print("4. Annotation list command help:")
    result = runner.invoke(app, ["annotate", "list", "--help"])
    lines = result.stdout.split('\n')
    for line in lines[:15]:
        print(f"   {line}")
    print()
    
    print("=== Example Commands ===")
    print("""
To create an annotation:
  pharos annotate create 123 --text "Important insight" --tags important,review

To list annotations for a resource:
  pharos annotate list --resource 123

To search annotations:
  pharos annotate search "machine learning" --type fulltext

To export annotations:
  pharos annotate export --resource 123 --format markdown --output ./annotations.md

To import annotations:
  pharos annotate import ./annotations.json --resource 123
    """)

if __name__ == "__main__":
    main()