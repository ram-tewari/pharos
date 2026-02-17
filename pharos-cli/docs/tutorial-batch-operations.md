# Batch Operations Tutorial

Learn how to efficiently manage large numbers of resources using Pharos CLI batch operations.

## Table of Contents

- [Overview](#overview)
- [Bulk Import](#bulk-import)
- [Batch Delete](#batch-delete)
- [Batch Update](#batch-update)
- [Batch Export](#batch-export)
- [Parallel Processing](#parallel-processing)
- [Best Practices](#best-practices)
- [Example Workflows](#example-workflows)

---

## Overview

Batch operations allow you to process multiple resources efficiently without manual intervention. This is essential for:

- Initial data migration
- Regular synchronization
- Bulk updates
- Data cleanup
- Export operations

### Key Features

- **Parallel processing** - Use multiple workers for speed
- **Progress tracking** - Real-time progress bars
- **Error handling** - Continue on failure, skip problematic items
- **Dry-run mode** - Preview changes before applying

---

## Bulk Import

### Import All Files in a Directory

```bash
# Import all files from a directory
pharos resource import ./data/
```

### Import Specific File Types

```bash
# Import only Python files
pharos resource import ./project/ --pattern "*.py"

# Import multiple patterns
pharos resource import ./project/ --pattern "*.py" --pattern "*.js"

# Import PDFs
pharos resource import ./papers/ --pattern "*.pdf"
```

### Recursive Import

```bash
# Recursively import all files
pharos resource import ./project/ --recursive

# Recursive with pattern
pharos resource import ./project/ --pattern "*.py" --recursive
```

### Import with Type Assignment

```bash
# Import as code
pharos resource import ./src/ --pattern "*.py" --type code

# Import as papers
pharos resource import ./papers/ --pattern "*.pdf" --type paper

# Import as documentation
pharos resource import ./docs/ --pattern "*.md" --type documentation
```

### Import with Language Detection

```bash
# Auto-detect language for code files
pharos resource import ./project/ --pattern "*.py" --auto-language

# Specify language explicitly
pharos resource import ./project/ --pattern "*.py" --language python
```

### Parallel Import

```bash
# Use multiple workers for faster import
pharos resource import ./large_project/ --workers 8

# Default is 4 workers
pharos resource import ./project/ --workers 4
```

### Error Handling

```bash
# Skip files that fail to import
pharos resource import ./project/ --skip-errors

# Continue on error (default behavior)
pharos resource import ./project/ --continue-on-error

# Fail on first error
pharos resource import ./project/ --fail-fast
```

### Import with Progress

```bash
# Show progress bar
pharos resource import ./project/ --progress

# Verbose output
pharos resource import ./project/ --verbose
```

### Complete Import Example

```bash
# Import all Python files from project recursively with parallel processing
pharos resource import ./my_project/ \
  --pattern "*.py" \
  --type code \
  --recursive \
  --workers 8 \
  --skip-errors \
  --progress
```

---

## Batch Delete

### Delete by IDs

```bash
# Delete specific IDs
pharos batch delete "1,2,3,4,5"
```

### Delete with Confirmation

```bash
# Interactive confirmation (default)
pharos batch delete "1,2,3"

# Force delete without confirmation
pharos batch delete "1,2,3" --force
```

### Dry Run

```bash
# Preview what will be deleted
pharos batch delete "1,2,3,4,5" --dry-run
```

This shows what would be deleted without actually deleting.

### Delete with Filters

```bash
# Delete low-quality resources
pharos quality outliers --min-score 0.3 --format json | \
  jq -r '.outliers[].resource_id' | \
  tr '\n' ',' | \
  sed 's/,$//' | \
  xargs pharos batch delete
```

### Parallel Delete

```bash
# Use multiple workers
pharos batch delete "1,2,3,4,5,6,7,8" --workers 8
```

### Delete All Resources (Use with Caution)

```bash
# Get all resource IDs
pharos resource list --format json | \
  jq -r '.items[].id' | \
  tr '\n' ',' | \
  sed 's/,$//' > all_ids.txt

# Review the list
cat all_ids.txt

# Delete all (after review)
pharos batch delete "$(cat all_ids.txt)" --force
```

---

## Batch Update

### Update File Format

Create a JSON file with updates:

```json
{
  "updates": [
    {
      "id": 1,
      "title": "Updated Title",
      "tags": ["important", "review"]
    },
    {
      "id": 2,
      "description": "New description"
    },
    {
      "id": 3,
      "quality_score": null
    }
  ]
}
```

### Apply Updates

```bash
# Apply updates from file
pharos batch update updates.json
```

### Dry Run

```bash
# Preview changes without applying
pharos batch update updates.json --dry-run
```

### Update Examples

#### Update Titles

```json
{
  "updates": [
    {"id": 1, "title": "New Title for Resource 1"},
    {"id": 2, "title": "New Title for Resource 2"},
    {"id": 3, "title": "New Title for Resource 3"}
  ]
}
```

#### Update Tags

```json
{
  "updates": [
    {"id": 1, "tags": ["python", "tutorial"]},
    {"id": 2, "tags": ["machine-learning", "advanced"]},
    {"id": 3, "tags": ["documentation"]}
  ]
}
```

#### Clear Fields

```json
{
  "updates": [
    {"id": 1, "quality_score": null},
    {"id": 2, "tags": []}
  ]
}
```

#### Bulk Tag Update Script

```bash
#!/bin/bash
# add_tag.sh - Add a tag to multiple resources

TAG="$1"
IDS_FILE="$2"

if [ -z "$TAG" ] || [ -z "$IDS_FILE" ]; then
  echo "Usage: $0 <tag> <ids_file>"
  exit 1
fi

# Read IDs and create update file
cat > updates.json << EOF
{
  "updates": [
$(cat "$IDS_FILE" | while read id; do
  echo "    {\"id\": $id, \"tags\": [\"$TAG\"]},"
done | sed '$ s/,$//')
  ]
}
EOF

# Apply updates
pharos batch update updates.json

# Cleanup
rm updates.json

echo "Tag '$TAG' added to resources in $IDS_FILE"
```

---

## Batch Export

### Export Collection

```bash
# Export collection as ZIP
pharos batch export --collection 1 --format zip --output collection1.zip

# Export as JSON
pharos batch export --collection 1 --format json --output collection1.json

# Export as Markdown files
pharos batch export --collection 1 --format markdown --output ./exports/
```

### Export by IDs

```bash
# Export specific resource IDs
pharos batch export --ids "1,2,3,4,5" --format json --output resources.json
```

### Export with Filters

```bash
# Export high-quality resources
pharos resource list --min-quality 0.8 --format json | \
  jq -r '.items[].id' | \
  tr '\n' ',' | \
  sed 's/,$//' > high_quality_ids.txt

pharos batch export --ids "$(cat high_quality_ids.txt)" --output high_quality.json
```

### Parallel Export

```bash
# Use multiple workers for large exports
pharos batch export --collection 1 --workers 8 --output collection1.zip
```

### Export Formats

#### JSON Format

```json
{
  "resources": [
    {
      "id": 1,
      "title": "Resource 1",
      "content": "...",
      "metadata": {...}
    }
  ]
}
```

#### Markdown Format

Creates individual `.md` files for each resource:

```
exports/
├── resource_1.md
├── resource_2.md
└── resource_3.md
```

Each file contains:
```markdown
---
id: 1
title: Resource Title
type: code
tags: [tag1, tag2]
---

Resource content here...
```

#### ZIP Format

Contains all resources with metadata:

```
collection.zip
├── resources.json
├── resource_1/
│   ├── content.txt
│   └── metadata.json
└── resource_2/
    ├── content.txt
    └── metadata.json
```

---

## Parallel Processing

### Worker Configuration

```bash
# Use 4 workers (default)
pharos resource import ./project/ --workers 4

# Use 8 workers for faster processing
pharos resource import ./project/ --workers 8

# Use 2 workers for less system load
pharos resource import ./project/ --workers 2
```

### When to Use More Workers

- Large imports (1000+ files)
- Fast network connection
- Powerful hardware
- No rate limits on API

### When to Use Fewer Workers

- Slower network
- Rate-limited API
- Resource-constrained environment
- Large file processing

### Monitor Progress

```bash
# Show progress bar
pharos resource import ./project/ --progress

# Verbose logging
pharos resource import ./project/ --verbose

# Quiet mode (less output)
pharos resource import ./project/ --quiet
```

---

## Best Practices

### 1. Always Dry Run First

```bash
# Preview batch operations
pharos batch delete "1,2,3" --dry-run
pharos batch update updates.json --dry-run
```

### 2. Use Parallel Processing Wisely

```bash
# Test with small batch first
pharos resource import ./project/ --pattern "*.py" --workers 2

# Increase workers after testing
pharos resource import ./project/ --pattern "*.py" --workers 8
```

### 3. Handle Errors Gracefully

```bash
# Skip errors for large imports
pharos resource import ./project/ --skip-errors

# Log errors
pharos resource import ./project/ --skip-errors 2>&1 | tee import.log
```

### 4. Use Appropriate Output Format

```bash
# For scripting: JSON
pharos resource list --format json > resources.json

# For display: table (default)
pharos resource list

# For piping: quiet (IDs only)
pharos resource list --format quiet | xargs -I {} pharos resource get {}
```

### 5. Back Up Before Major Operations

```bash
# Backup before batch delete
pharos backup --output backup_before_delete.json

# Backup before batch update
pharos backup --output backup_before_update.json
```

### 6. Monitor Resource Usage

```bash
# Check system stats
pharos stats

# Check quality distribution
pharos quality distribution
```

---

## Example Workflows

### Workflow 1: Import New Project

```bash
#!/bin/bash
# import_project.sh

PROJECT_DIR="./my_project"
COLLECTION_NAME="My Project"

echo "Starting project import..."

# Create collection
COLLECTION_ID=$(pharos collection create "$COLLECTION_NAME" --format quiet)
echo "Created collection: $COLLECTION_ID"

# Import code files
pharos resource import "$PROJECT_DIR" \
  --pattern "*.py" \
  --pattern "*.js" \
  --pattern "*.ts" \
  --type code \
  --recursive \
  --workers 8 \
  --skip-errors \
  --progress

# Import documentation
pharos resource import "$PROJECT_DIR" \
  --pattern "*.md" \
  --pattern "*.txt" \
  --type documentation \
  --recursive \
  --skip-errors

# Import resources and add to collection
for id in $(pharos resource list --format json | jq -r '.items[].id' | tail -10); do
  pharos collection add "$COLLECTION_ID" "$id"
done

echo "Project import complete!"
echo "Collection ID: $COLLECTION_ID"
```

### Workflow 2: Clean Up Low-Quality Resources

```bash
#!/bin/bash
# cleanup_low_quality.sh

THRESHOLD="${1:-0.3}"

echo "Finding resources with quality < $THRESHOLD..."

# Get low-quality resource IDs
pharos quality outliers --min-score "$THRESHOLD" --format json > low_quality.json

COUNT=$(jq '.total' low_quality.json)
echo "Found $COUNT low-quality resources"

if [ "$COUNT" -gt 0 ]; then
  # Show what will be deleted
  echo "Resources to delete:"
  jq -r '.outliers[] | "\(.resource_id): \(.quality_overall)"' low_quality.json

  # Get IDs for deletion
  IDS=$(jq -r '.outliers[].resource_id' low_quality.json | tr '\n' ',' | sed 's/,$//')

  # Delete (uncomment to actually delete)
  # echo "Deleting..."
  # pharos batch delete "$IDS" --force

  echo "Dry run complete. Run with --force to actually delete."
fi

# Cleanup
rm low_quality.json
```

### Workflow 3: Sync External Data

```bash
#!/bin/bash
# sync_external.sh

SOURCE_DIR="./external_data"
BATCH_SIZE=100

echo "Starting sync from $SOURCE_DIR..."

# Import new files
pharos resource import "$SOURCE_DIR" \
  --pattern "*.md" \
  --pattern "*.txt" \
  --type documentation \
  --recursive \
  --skip-errors

# Get newly imported IDs
NEW_IDS=$(pharos resource list --format json | \
  jq -r '.items[] | select(.created_at | contains("'$(date +%Y-%m-%d)'")) | .id')

# Add to main collection
for id in $NEW_IDS; do
  pharos collection add 1 "$id"
done

echo "Sync complete. Added $(echo $NEW_IDS | wc -w) new resources."
```

### Workflow 4: Generate Collection Report

```bash
#!/bin/bash
# generate_report.sh

COLLECTION_ID="$1"
OUTPUT_DIR="./reports/$(date +%Y%m%d)"

if [ -z "$COLLECTION_ID" ]; then
  echo "Usage: $0 <collection_id>"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "Generating report for collection $COLLECTION_ID..."

# Collection details
pharos collection show "$COLLECTION_ID" --format json > "$OUTPUT_DIR/collection.json"

# Quality report
pharos quality report "$COLLECTION_ID" --format json > "$OUTPUT_DIR/quality_report.json"

# Export resources
pharos batch export --collection "$COLLECTION_ID" --format json --output "$OUTPUT_DIR/resources.json"

# Graph data
pharos graph stats --format json > "$OUTPUT_DIR/graph_stats.json"

# Taxonomy distribution
pharos taxonomy distribution --format json > "$OUTPUT_DIR/taxonomy.json"

echo "Report generated in $OUTPUT_DIR/"
ls -la "$OUTPUT_DIR"
```

### Workflow 5: Daily Backup

```bash
#!/bin/bash
# daily_backup.sh

BACKUP_DIR="./backups/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

echo "Creating daily backup..."

# Backup all resources
pharos backup --output "$BACKUP_DIR/full_backup.json"

# Backup collections
pharos collection list --format json | \
  jq -r '.items[].id' | \
  while read id; do
    NAME=$(pharos collection show "$id" --format json | jq -r '.name' | tr ' ' '_')
    pharos collection export "$id" --format json --output "$BACKUP_DIR/collection_${id}_${NAME}.json"
  done

# Backup graph
pharos graph export --format json --output "$BACKUP_DIR/graph.json"

# Verify backup
pharos backup verify "$BACKUP_DIR/full_backup.json"

echo "Backup complete: $BACKUP_DIR"
```

---

## Troubleshooting

### Import Fails with Connection Error

```bash
# Check API URL
pharos config show

# Test connection
pharos health

# Retry with fewer workers
pharos resource import ./project/ --workers 2
```

### Batch Delete Times Out

```bash
# Delete in smaller batches
pharos batch delete "1,2,3" --workers 2
pharos batch delete "4,5,6" --workers 2
```

### Export Produces Incomplete Results

```bash
# Use more workers
pharos batch export --collection 1 --workers 8

# Check for errors
pharos batch export --collection 1 --verbose
```

### Memory Issues with Large Imports

```bash
# Import in smaller batches
pharos resource import ./project/ --pattern "*.py" --batch-size 50

# Use fewer workers
pharos resource import ./project/ --workers 2
```

---

## See Also

- [Command Reference](command-reference.md)
- [Usage Patterns](usage-patterns.md)
- [Workflows](workflows.md)
- [Cheat Sheet](cheat-sheet.md)
- [Scripting Guide](scripting-guide.md)