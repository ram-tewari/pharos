#!/bin/bash
# import_project.sh - Import a project into Pharos
#
# Usage: ./import_project.sh <project_directory> [collection_name]
#
# This script imports all code files from a directory into Pharos
# and optionally creates a collection for them.

set -e

# Configuration
PROJECT_DIR="${1:-./src}"
COLLECTION_NAME="${2:-Project Import $(date +%Y-%m-%d)}"
WORKERS="${WORKERS:-4}"

echo "=========================================="
echo "Pharos Project Import"
echo "=========================================="
echo "Project Directory: $PROJECT_DIR"
echo "Collection Name: $COLLECTION_NAME"
echo "Workers: $WORKERS"
echo ""

# Check if Pharos is configured
if ! pharos config show &> /dev/null; then
    echo "Error: Pharos not configured. Run 'pharos config init' first."
    exit 1
fi

# Check if directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Error: Directory $PROJECT_DIR does not exist"
    exit 1
fi

# Create collection
echo "Creating collection..."
COLLECTION_ID=$(pharos collection create "$COLLECTION_NAME" --format quiet)
echo "Collection ID: $COLLECTION_ID"

# Import Python files
echo ""
echo "Importing Python files..."
pharos resource import "$PROJECT_DIR" \
    --pattern "*.py" \
    --type code \
    --language python \
    --recursive \
    --workers "$WORKERS" \
    --skip-errors \
    --progress

# Import JavaScript/TypeScript files
echo ""
echo "Importing JavaScript/TypeScript files..."
pharos resource import "$PROJECT_DIR" \
    --pattern "*.js" \
    --pattern "*.ts" \
    --pattern "*.jsx" \
    --pattern "*.tsx" \
    --type code \
    --recursive \
    --workers "$WORKERS" \
    --skip-errors \
    --progress

# Import other code files
echo ""
echo "Importing other code files..."
pharos resource import "$PROJECT_DIR" \
    --pattern "*.java" \
    --pattern "*.cpp" \
    --pattern "*.c" \
    --pattern "*.go" \
    --pattern "*.rs" \
    --type code \
    --recursive \
    --workers "$WORKERS" \
    --skip-errors \
    --progress

# Add resources to collection
echo ""
echo "Adding resources to collection..."
TOTAL=$(pharos resource list --format json | jq '.total')
echo "Total resources in system: $TOTAL"

# Summary
echo ""
echo "=========================================="
echo "Import Complete"
echo "=========================================="
echo "Collection ID: $COLLECTION_ID"
echo "Collection Name: $COLLECTION_NAME"
echo ""
echo "Next steps:"
echo "  - View collection: pharos collection show $COLLECTION_ID"
echo "  - Run code analysis: pharos code scan $PROJECT_DIR"
echo "  - Check quality: pharos quality outliers"