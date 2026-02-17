#!/bin/bash
# Release script for Pharos CLI

set -e

echo "Pharos CLI Release Script"
echo "========================="

# Get current version
VERSION=$(python -c "import pharos_cli; print(pharos_cli.__version__)")
echo "Current version: $VERSION"

# Ask for new version
read -p "Enter new version (current: $VERSION): " NEW_VERSION

if [ -z "$NEW_VERSION" ]; then
    echo "Version cannot be empty"
    exit 1
fi

# Confirm
echo "Preparing release v$NEW_VERSION"
read -p "Continue? [y/N]: " CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "Aborted"
    exit 0
fi

# Update version in pyproject.toml
echo "Updating version in pyproject.toml..."
sed -i "s/version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml

# Update version in pharos_cli/version.py
echo "Updating version in pharos_cli/version.py..."
sed -i "s/__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" pharos_cli/version.py

# Update version in pharos_cli/__init__.py
echo "Updating version in pharos_cli/__init__.py..."
sed -i "s/__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" pharos_cli/__init__.py

# Run tests
echo "Running tests..."
pip install -e ".[dev]" > /dev/null 2>&1
pytest tests -v --tb=short

# Run linters
echo "Running linters..."
ruff check pharos_cli tests
black --check pharos_cli tests
mypy pharos_cli

# Build package
echo "Building package..."
pip install build > /dev/null 2>&1
python -m build

# Check package
echo "Checking package..."
pip install twine > /dev/null 2>&1
twine check dist/*

# Create git tag
echo "Creating git tag v$NEW_VERSION..."
git add -A
git commit -m "Release v$NEW_VERSION"
git tag -a "v$NEW_VERSION" -m "Version $NEW_VERSION"

echo ""
echo "Release v$NEW_VERSION prepared!"
echo ""
echo "To publish to PyPI:"
echo "  1. Push the tag: git push origin v$NEW_VERSION"
echo "  2. The GitHub Action will publish to PyPI automatically"
echo ""
echo "Or to publish manually:"
echo "  twine upload dist/*"