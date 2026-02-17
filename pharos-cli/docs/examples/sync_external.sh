#!/bin/bash
# sync_external.sh - Sync external data sources to Pharos
#
# Usage: ./sync_external.sh <source_type> <source_path>
#
# Supported source types:
#   - github: GitHub repository (requires gh CLI)
#   - git: Git repository
#   - local: Local directory
#
# Examples:
#   ./sync_external.sh local ./my_project
#   ./sync_external.sh github owner/repo

set -e

SOURCE_TYPE="$1"
SOURCE_PATH="$2"

if [ -z "$SOURCE_TYPE" ] || [ -z "$SOURCE_PATH" ]; then
    echo "Usage: $0 <source_type> <source_path>"
    echo ""
    echo "Supported source types:"
    echo "  local   - Local directory"
    echo "  git     - Git repository URL or path"
    echo "  github  - GitHub repository (owner/repo)"
    exit 1
fi

TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

case "$SOURCE_TYPE" in
    local)
        echo "Syncing from local directory: $SOURCE_PATH"
        if [ ! -d "$SOURCE_PATH" ]; then
            echo "Error: Directory not found: $SOURCE_PATH"
            exit 1
        fi
        cp -r "$SOURCE_PATH"/* "$TEMP_DIR/"
        ;;
        
    git)
        echo "Cloning git repository: $SOURCE_PATH"
        git clone --depth 1 "$SOURCE_PATH" "$TEMP_DIR" 2>/dev/null || {
            # Try as local path
            if [ -d "$SOURCE_PATH/.git" ]; then
                git clone --depth 1 "$SOURCE_PATH" "$TEMP_DIR"
            else
                echo "Error: Not a valid git repository: $SOURCE_PATH"
                exit 1
            fi
        }
        ;;
        
    github)
        echo "Cloning GitHub repository: $SOURCE_PATH"
        if command -v gh &> /dev/null; then
            gh repo clone "$SOURCE_PATH" "$TEMP_DIR" -- --depth 1 2>/dev/null || {
                echo "Error: Failed to clone $SOURCE_PATH"
                exit 1
            }
        else
            # Use git directly
            git clone "https://github.com/$SOURCE_PATH" "$TEMP_DIR" --depth 1 || {
                echo "Error: Failed to clone $SOURCE_PATH"
                exit 1
            }
        fi
        ;;
        
    *)
        echo "Error: Unknown source type: $SOURCE_TYPE"
        exit 1
        ;;
esac

echo ""
echo "Importing files..."

# Import code files
pharos resource import "$TEMP_DIR" \
    --pattern "*.py" \
    --pattern "*.js" \
    --pattern "*.ts" \
    --pattern "*.java" \
    --pattern "*.go" \
    --pattern "*.rs" \
    --type code \
    --recursive \
    --workers 4 \
    --skip-errors

# Import documentation
pharos resource import "$TEMP_DIR" \
    --pattern "*.md" \
    --pattern "*.txt" \
    --pattern "*.rst" \
    --type documentation \
    --recursive \
    --skip-errors

# Import other text files
pharos resource import "$TEMP_DIR" \
    --pattern "*.json" \
    --pattern "*.yaml" \
    --pattern "*.yml" \
    --type documentation \
    --recursive \
    --skip-errors

# Summary
TOTAL=$(pharos resource list --format json | jq '.total')
echo ""
echo "=========================================="
echo "Sync Complete"
echo "=========================================="
echo "Source: $SOURCE_TYPE:$SOURCE_PATH"
echo "Total resources: $TOTAL"
echo ""
echo "Next steps:"
echo "  - Run code analysis: pharos code scan $TEMP_DIR"
echo "  - Check quality: pharos quality outliers"