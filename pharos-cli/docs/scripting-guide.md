# Scripting with Pharos CLI

A comprehensive guide to using Pharos CLI in shell scripts and automation workflows.

## Table of Contents

- [Introduction](#introduction)
- [Output Formats](#output-formats)
- [Parsing JSON Output](#parsing-json-output)
- [Common Scripting Patterns](#common-scripting-patterns)
- [Error Handling](#error-handling)
- [Environment Variables](#environment-variables)
- [Advanced Scripting](#advanced-scripting)
- [Example Scripts](#example-scripts)
- [Best Practices](#best-practices)

---

## Introduction

Pharos CLI is designed for scripting with support for multiple output formats, proper exit codes, and environment variable configuration.

### Key Features for Scripting

- **JSON output** - Parseable by tools like `jq`
- **Quiet mode** - Output only IDs for piping
- **Non-interactive mode** - No prompts
- **Proper exit codes** - 0 for success, non-zero for errors
- **Environment variable configuration** - Configure via env vars

### Basic Script Structure

```bash
#!/bin/bash
# Script template for Pharos CLI

# Exit on error
set -e

# Configure Pharos (optional, can use environment variables)
export PHAROS_API_URL="${PHAROS_API_URL:-https://pharos.onrender.com}"
export PHAROS_API_KEY="$PHAROS_API_KEY"

# Your script logic here
pharos resource list --format json
```

---

## Output Formats

### JSON Format (Best for Scripting)

```bash
# Get JSON output
pharos resource list --format json

# Pretty-printed JSON
pharos resource get 1 --format json

# Minified JSON (for parsing)
pharos resource list --format json | jq -c '.'
```

### Quiet Format (IDs Only)

```bash
# Output only resource IDs
pharos resource list --format quiet

# Use in pipelines
pharos resource list --format quiet | while read id; do
  pharos resource get "$id"
done
```

### CSV Format (Spreadsheets)

```bash
# Export to CSV
pharos resource list --format csv > resources.csv

# Import to spreadsheet
# Works with Excel, Google Sheets, etc.
```

### Table Format (Human Readable)

```bash
# Default format, good for terminal
pharos resource list

# With color
pharos resource list --color always
```

---

## Parsing JSON Output

### Installing jq

```bash
# Ubuntu/Debian
sudo apt install jq

# macOS
brew install jq

# pip
pip install jq
```

### Basic jq Operations

```bash
# Get top-level fields
pharos resource list --format json | jq '.total'
pharos resource list --format json | jq '.items | length'

# Get nested fields
pharos resource get 1 --format json | jq '.title'
pharos resource get 1 --format json | jq '.metadata.language'

# Arrays
pharos resource list --format json | jq '.items[].title'
pharos resource list --format json | jq '.items[0].title'

# Filtering
pharos resource list --format json | jq '.items[] | select(.quality_score > 0.8)'
pharos resource list --format json | jq '.items[] | select(.type == "code")'

# Mapping
pharos resource list --format json | jq '.items[] | {id, title, quality: .quality_score}'

# Counting
pharos resource list --format json | jq '[.items[] | select(.quality_score > 0.8)] | length'

# Sorting
pharos resource list --format json | jq '.items | sort_by(.quality_score) | reverse'
```

### Advanced jq Examples

```bash
# Get all resource IDs with high quality
pharos resource list --format json | \
  jq -r '.items[] | select(.quality_score > 0.8) | .id' | \
  tr '\n' ',' | sed 's/,$//'

# Create update JSON
pharos resource list --format json | \
  jq '{updates: [.items[] | {id: .id, quality_score: .quality_score}]}'

# Extract specific fields
pharos resource list --format json | \
  jq '.items[] | {id, title, type, quality_score}'

# Group by type
pharos resource list --format json | \
  jq 'group_by(.type) | .[] | {type: .[0].type, count: length}'
```

---

## Common Scripting Patterns

### Pattern 1: Iterate Over Resources

```bash
#!/bin/bash
# Process each resource

for id in $(pharos resource list --format quiet); do
  echo "Processing resource $id"
  pharos resource get "$id" --format json | jq '.title'
done
```

### Pattern 2: Filter and Process

```bash
#!/bin/bash
# Process only high-quality resources

pharos resource list --format json | \
  jq -r '.items[] | select(.quality_score > 0.8) | .id' | \
  while read id; do
    pharos resource get "$id" --format json
  done
```

### Pattern 3: Batch Operations

```bash
#!/bin/bash
# Batch delete low-quality resources

# Get low-quality IDs
IDS=$(pharos quality outliers --min-score 0.3 --format json | \
      jq -r '.outliers[].resource_id' | \
      tr '\n' ',' | \
      sed 's/,$//')

if [ -n "$IDS" ]; then
  echo "Deleting: $IDS"
  pharos batch delete "$IDS" --force
fi
```

### Pattern 4: Search and Export

```bash
#!/bin/bash
# Search and save results

QUERY="$1"
OUTPUT_FILE="$2"

if [ -z "$QUERY" ] || [ -z "$OUTPUT_FILE" ]; then
  echo "Usage: $0 <query> <output_file>"
  exit 1
fi

pharos search "$QUERY" \
  --min-quality 0.8 \
  --limit 100 \
  --format json \
  --output "$OUTPUT_FILE"

echo "Results saved to $OUTPUT_FILE"
```

### Pattern 5: Collection Management

```bash
#!/bin/bash
# Create collection and add resources

COLLECTION_NAME="$1"
RESOURCE_DIR="$2"

if [ -z "$COLLECTION_NAME" ] || [ -z "$RESOURCE_DIR" ]; then
  echo "Usage: $0 <collection_name> <resource_dir>"
  exit 1
fi

# Create collection
COLLECTION_ID=$(pharos collection create "$COLLECTION_NAME" --format quiet)
echo "Created collection: $COLLECTION_ID"

# Import resources
pharos resource import "$RESOURCE_DIR" --pattern "*.py" --type code

# Add to collection
for id in $(pharos resource list --format quiet | tail -10); do
  pharos collection add "$COLLECTION_ID" "$id"
done

echo "Added resources to collection $COLLECTION_ID"
```

### Pattern 6: Parallel Processing

```bash
#!/bin/bash
# Process resources in parallel

IDS=$(pharos resource list --format quiet)

echo "$IDS" | xargs -P 4 -I {} sh -c 'pharos resource get {} --format json | jq ".id"' &
wait

echo "All resources processed"
```

---

## Error Handling

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Authentication error |
| 4 | Resource not found |
| 5 | Network error |

### Basic Error Handling

```bash
#!/bin/bash
# Check exit code

if pharos resource get 1 --format json > /dev/null 2>&1; then
  echo "Resource exists"
else
  echo "Resource not found"
fi
```

### Strict Mode

```bash
#!/bin/bash
# Exit on any error

set -e

# This will fail if resource doesn't exist
pharos resource get 1

# This won't run if above fails
echo "This won't print if resource doesn't exist"
```

### Continue on Error

```bash
#!/bin/bash
# Continue even if some operations fail

set +e

# Try to get resources (may fail)
pharos resource get 1
pharos resource get 99999  # This will fail
pharos resource get 2

set -e

echo "Continuing after errors"
```

### Custom Error Handling

```bash
#!/bin/bash
# Custom error handling

handle_error() {
  echo "Error: $1" >&2
  exit 1
}

# Check if resource exists
if ! pharos resource get 1 --format json > /dev/null 2>&1; then
  handle_error "Resource 1 not found"
fi

# Check quality
QUALITY=$(pharos resource get 1 --format json | jq -r '.quality_score')
if (( $(echo "$QUALITY < 0.5" | bc -l) )); then
  handle_error "Resource quality too low: $QUALITY"
fi

echo "All checks passed"
```

### Retry Logic

```bash
#!/bin/bash
# Retry with exponential backoff

MAX_RETRIES=3
RETRY_DELAY=1

retry_command() {
  local cmd="$1"
  local attempt=1
  
  while [ $attempt -le $MAX_RETRIES ]; do
    if eval "$cmd"; then
      return 0
    fi
    
    echo "Attempt $attempt failed, retrying in $RETRY_DELAY seconds..."
    sleep $RETRY_DELAY
    RETRY_DELAY=$((RETRY_DELAY * 2))
    attempt=$((attempt + 1))
  done
  
  echo "Failed after $MAX_RETRIES attempts"
  return 1
}

retry_command "pharos health"
```

---

## Environment Variables

### Configuration Variables

```bash
# API configuration
export PHAROS_API_URL="https://pharos.onrender.com"
export PHAROS_API_KEY="your-api-key"

# Output preferences
export PHAROS_OUTPUT_FORMAT="json"
export PHAROS_COLOR="never"
export PHAROS_PAGER="never"

# Behavior
export PHAROS_TIMEOUT="30"
export PHAROS_WORKERS="4"
```

### Using in Scripts

```bash
#!/bin/bash
# Use environment variables

export PHAROS_API_URL="${PHAROS_API_URL:-https://pharos.onrender.com}"
export PHAROS_API_KEY="${PHAROS_API_KEY:-}"
export PHAROS_OUTPUT_FORMAT="${PHAROS_OUTPUT_FORMAT:-json}"

# Validate required variables
if [ -z "$PHAROS_API_KEY" ]; then
  echo "Error: PHAROS_API_KEY not set"
  exit 1
fi

# Commands use environment variables
pharos resource list
```

### CI/CD Environment Variables

```bash
#!/bin/bash
# CI/CD script with secrets

# API key from CI/CD secret
export PHAROS_API_KEY="$PHAROS_API_KEY"

# Non-interactive
export PHAROS_NON_INTERACTIVE="1"

# Run commands
pharos resource import ./src/ --pattern "*.py"
pharos code scan ./src/ --format json > analysis.json
```

---

## Advanced Scripting

### Progress Tracking

```bash
#!/bin/bash
# Show progress during long operations

TOTAL=$(pharos resource list --format json | jq '.total')
CURRENT=0

pharos resource list --format quiet | while read id; do
  CURRENT=$((CURRENT + 1))
  echo "Progress: $CURRENT/$TOTAL"
  pharos resource get "$id" --format json > /dev/null
done
```

### Interactive Prompts

```bash
#!/bin/bash
# Interactive confirmation

read -p "Delete all low-quality resources? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  IDS=$(pharos quality outliers --min-score 0.3 --format json | \
        jq -r '.outliers[].resource_id' | tr '\n' ',' | sed 's/,$//')
  pharos batch delete "$IDS" --force
  echo "Resources deleted"
fi
```

### Configuration Profiles

```bash
#!/bin/bash
# Use different profiles

# Development
export PHAROS_PROFILE="dev"
pharos resource list

# Production
export PHAROS_PROFILE="prod"
pharos resource list
```

### Logging

```bash
#!/bin/bash
# Log operations

LOG_FILE="pharos_$(date +%Y%m%d).log"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "Starting import"
pharos resource import ./src/ --pattern "*.py" >> "$LOG_FILE" 2>&1
log "Import complete"

cat "$LOG_FILE"
```

### Signal Handling

```bash
#!/bin/bash
# Handle interrupts

cleanup() {
  echo "Interrupted, cleaning up..."
  # Add cleanup logic here
  exit 1
}

trap cleanup SIGINT SIGTERM

# Long-running operation
while true; do
  pharos resource list --format json > /dev/null
  sleep 60
done
```

---

## Example Scripts

### Example 1: Daily Sync Script

```bash
#!/bin/bash
# daily_sync.sh - Sync external data to Pharos

set -e

# Configuration
SOURCE_DIR="./external_data"
LOG_FILE="./logs/sync_$(date +%Y%m%d).log"
BACKUP_DIR="./backups"

# Create directories
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$BACKUP_DIR"

# Log function
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting daily sync"

# Create backup
log "Creating backup..."
pharos backup --output "$BACKUP_DIR/backup_$(date +%Y%m%d).json"

# Import new files
log "Importing files from $SOURCE_DIR..."
pharos resource import "$SOURCE_DIR" \
  --pattern "*.md" \
  --pattern "*.txt" \
  --type documentation \
  --recursive \
  --skip-errors \
  --progress

# Check quality
log "Checking quality..."
pharos quality outliers --min-score 0.5 --format json > "$BACKUP_DIR/quality_$(date +%Y%m%d).json"

# Summary
TOTAL=$(pharos resource list --format json | jq '.total')
log "Sync complete. Total resources: $TOTAL"
```

### Example 2: Quality Report Generator

```bash
#!/bin/bash
# generate_quality_report.sh

set -e

OUTPUT_DIR="./quality_reports/$(date +%Y%m%d)"
mkdir -p "$OUTPUT_DIR"

echo "Generating quality report..."

# Overall statistics
pharos quality distribution --format json > "$OUTPUT_DIR/distribution.json"

# Outliers
pharos quality outliers --format json > "$OUTPUT_DIR/outliers.json"

# By dimension
for dimension in accuracy completeness consistency freshness; do
  pharos quality trends --dimension "$dimension" --format json \
    > "$OUTPUT_DIR/trends_${dimension}.json"
done

# Collection reports
for id in $(pharos collection list --format quiet); do
  NAME=$(pharos collection show "$id" --format json | jq -r '.name' | tr ' ' '_')
  pharos quality report "$id" --format json \
    > "$OUTPUT_DIR/collection_${id}_${NAME}.json"
done

# Summary
TOTAL_OUTLIERS=$(jq '.total' "$OUTPUT_DIR/outliers.json")
echo "Report generated in $OUTPUT_DIR"
echo "Total outliers: $TOTAL_OUTLIERS"
```

### Example 3: Resource Migrator

```bash
#!/bin/bash
# migrate_resources.sh - Migrate resources between collections

set -e

SOURCE_COLLECTION="$1"
DEST_COLLECTION="$2"

if [ -z "$SOURCE_COLLECTION" ] || [ -z "$DEST_COLLECTION" ]; then
  echo "Usage: $0 <source_collection_id> <dest_collection_id>"
  exit 1
fi

echo "Migrating resources from collection $SOURCE_COLLECTION to $DEST_COLLECTION"

# Get resources from source
RESOURCES=$(pharos collection show "$SOURCE_COLLECTION" --format json | \
            jq -r '.resources[].id')

COUNT=0
for id in $RESOURCES; do
  echo "Moving resource $id..."
  pharos collection add "$DEST_COLLECTION" "$id"
  COUNT=$((COUNT + 1))
done

echo "Migrated $COUNT resources"
```

### Example 4: Search and Notify

```bash
#!/bin/bash
# search_and_notify.sh - Search and notify on new results

set -e

QUERY="$1"
OUTPUT_FILE="/tmp/search_results_$(date +%Y%m%d).json"
PREVIOUS_FILE="/tmp/search_results_previous.json"
WEBHOOK_URL="$2"

if [ -z "$QUERY" ] || [ -z "$WEBHOOK_URL" ]; then
  echo "Usage: $0 <query> <webhook_url>"
  exit 1
fi

echo "Searching for: $QUERY"

# Current search
pharos search "$QUERY" --min-quality 0.8 --format json > "$OUTPUT_FILE"

# Compare with previous
if [ -f "$PREVIOUS_FILE" ]; then
  NEW_COUNT=$(jq -s \
    --argfile prev "$PREVIOUS_FILE" \
    --argfile curr "$OUTPUT_FILE" \
    '($curr | length) - ($prev | length)' \
    <<< '[]' 2>/dev/null || echo "0")
  
  if [ "$NEW_COUNT" -gt 0 ]; then
    echo "Found $NEW_COUNT new results"
    
    # Send webhook notification
    curl -X POST "$WEBHOOK_URL" \
      -H "Content-Type: application/json" \
      -d "{\"query\": \"$QUERY\", \"new_results\": $NEW_COUNT}"
  fi
fi

# Save current as previous
cp "$OUTPUT_FILE" "$PREVIOUS_FILE"

echo "Search complete"
```

### Example 5: Health Monitor

```bash
#!/bin/bash
# monitor_health.sh - Monitor Pharos health

set -e

WEBHOOK_URL="$1"
INTERVAL="${2:-60}"

if [ -z "$WEBHOOK_URL" ]; then
  echo "Usage: $0 <webhook_url> [interval_seconds]"
  exit 1
fi

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "Starting health monitor..."

while true; do
  # Check health
  if pharos health > /dev/null 2>&1; then
    log "System healthy"
  else
    log "System unhealthy, sending alert"
    
    curl -X POST "$WEBHOOK_URL" \
      -H "Content-Type: application/json" \
      -d '{"status": "unhealthy", "timestamp": "'$(date -Iseconds)'"}'
  fi
  
  sleep "$INTERVAL"
done
```

---

## Best Practices

### 1. Use set -e

```bash
#!/bin/bash
# Exit on error
set -e
```

### 2. Use Quoted Variables

```bash
# Good
pharos resource get "$id"

# Bad (may break on spaces)
pharos resource get $id
```

### 3. Use Meaningful Exit Codes

```bash
#!/bin/bash

exit_with_error() {
  echo "Error: $1" >&2
  exit 1
}

[ -z "$PHAROS_API_KEY" ] && exit_with_error "API key not set"
```

### 4. Log Operations

```bash
#!/bin/bash

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "Starting operation"
```

### 5. Validate Inputs

```bash
#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <resource_id>"
  exit 1
fi
```

### 6. Use Temporary Files Safely

```bash
#!/bin/bash

TMPFILE=$(mktemp)
trap "rm -f $TMPFILE" EXIT

pharos resource list --format json > "$TMPFILE"
```

### 7. Test Before Production

```bash
#!/bin/bash

# Test with dry run
pharos batch delete "1,2,3" --dry-run

# Review output
# Then run without --dry-run
pharos batch delete "1,2,3" --force
```

### 8. Document Your Scripts

```bash
#!/bin/bash
# sync_data.sh - Sync external data to Pharos
#
# Usage: ./sync_data.sh <source_directory>
#
# This script:
# 1. Creates a backup
# 2. Imports files from source directory
# 3. Checks quality
# 4. Reports summary

set -e

SOURCE_DIR="$1"
# ...
```

---

## See Also

- [Command Reference](command-reference.md)
- [Usage Patterns](usage-patterns.md)
- [Workflows](workflows.md)
- [Cheat Sheet](cheat-sheet.md)
- [Tutorial: Getting Started](tutorial-getting-started.md)
- [Tutorial: Batch Operations](tutorial-batch-operations.md)
- [Tutorial: CI/CD Integration](tutorial-ci-cd.md)