# Pharos CLI Usage Patterns

Common usage patterns and best practices for the Pharos CLI.

## Table of Contents

- [Basic Patterns](#basic-patterns)
- [Filtering and Search](#filtering-and-search)
- [Batch Operations](#batch-operations)
- [Output Handling](#output-handling)
- [Scripting Patterns](#scripting-patterns)
- [CI/CD Integration](#cicd-integration)
- [Interactive Workflows](#interactive-workflows)
- [Performance Optimization](#performance-optimization)

---

## Basic Patterns

### Single Resource Operations

```bash
# Add a resource
pharos resource add ./myfile.py

# Get resource details
pharos resource get 123

# Update a resource
pharos resource update 123 --title "New Title"

# Delete a resource
pharos resource delete 123 --force
```

### Listing Resources

```bash
# List all resources
pharos resource list

# List with pagination
pharos resource list --page 1 --per-page 50

# List with filters
pharos resource list --type code --language python --min-quality 0.8
```

### Chaining Commands

```bash
# Find resources and get details
pharos resource list --type paper --format quiet | head -5 | xargs -I {} pharos resource get {}

# Search and export
pharos search "machine learning" --format json | jq '.results[:10]' > top_results.json
```

---

## Filtering and Search

### Keyword Search

```bash
# Basic search
pharos search "python"

# Search with type filter
pharos search "api" --type code

# Search with quality filter
pharos search "tutorial" --min-quality 0.9
```

### Semantic Search

```bash
# Semantic search for conceptual queries
pharos search "how neural networks learn" --semantic

# Hybrid search with weight
pharos search "machine learning algorithms" --hybrid --weight 0.7
```

### Advanced Filtering

```bash
# Multiple filters
pharos search "python" \
  --type code \
  --language python \
  --min-quality 0.7 \
  --tags tutorial,beginner

# Collection-specific search
pharos search "optimization" --collection 5

# Date range filtering (via graph discover)
pharos graph discover "AI" "healthcare" --start-date 2023-01-01
```

---

## Batch Operations

### Importing Multiple Files

```bash
# Import all Python files in a directory
pharos resource import ./my_project/ --pattern "*.py"

# Recursive import with parallel workers
pharos resource import ./large_project/ --recursive --workers 8

# Import specific file types
pharos resource import ./papers/ \
  --pattern "*.pdf" \
  --type paper \
  --skip-errors
```

### Batch Delete

```bash
# Delete by IDs
pharos batch delete "1,2,3,4,5"

# Dry run first
pharos batch delete "1,2,3" --dry-run

# Force delete without confirmation
pharos batch delete "1,2,3" --force
```

### Batch Update

```bash
# Create update file
cat > updates.json << 'EOF'
{
  "updates": [
    {"id": 1, "title": "Updated Title 1"},
    {"id": 2, "title": "Updated Title 2"},
    {"id": 3, "tags": ["important", "review"]}
  ]
}
EOF

# Apply updates
pharos batch update updates.json

# Dry run to preview
pharos batch update updates.json --dry-run
```

### Batch Export

```bash
# Export entire collection
pharos batch export --collection 1 --format zip --output collection.zip

# Export specific resources
pharos batch export --ids "1,2,3,4,5" --format json --output resources.json

# Export as markdown files
pharos batch export --collection 1 --format markdown --output ./exports/
```

---

## Output Handling

### Format Selection

```bash
# Interactive use - table format (default)
pharos resource list

# Scripting - JSON format
pharos resource list --format json

# Data analysis - CSV format
pharos search "python" --format csv > search_results.csv

# Piping - quiet format (IDs only)
pharos resource list --format quiet
```

### Saving Results

```bash
# Save search results
pharos search "machine learning" --output results.json

# Save with specific format
pharos search "AI" --output results.json --format json

# Save collection export
pharos collection export 1 --format zip --output collection.zip
```

### Processing Output

```bash
# Extract IDs from JSON
pharos resource list --format json | jq '.items[].id'

# Filter by quality
pharos resource list --format json | jq '.items[] | select(.quality_score > 0.8)'

# Count results
pharos search "python" --format json | jq '.total'

# Pretty print
pharos resource get 1 --format json | jq '.'
```

---

## Scripting Patterns

### Resource Management Script

```bash
#!/bin/bash
# Add all new files to Pharos

for file in $(find ./src -name "*.py"); do
  echo "Adding: $file"
  pharos resource add "$file" --type code --language python
done

echo "Done adding files"
```

### Search and Export Script

```bash
#!/bin/bash
# Search and export top results

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

### Batch Processing Script

```bash
#!/bin/bash
# Process resources in batches

BATCH_SIZE=50
TOTAL=$(pharos resource list --format json | jq '.total')

for ((i=1; i<=TOTAL; i+=BATCH_SIZE)); do
  echo "Processing resources $i to $((i+BATCH_SIZE-1))"
  
  pharos resource list \
    --page $(( (i-1)/BATCH_SIZE + 1 )) \
    --per-page $BATCH_SIZE \
    --format json \
    --output batch_$i.json
done
```

### Quality Check Script

```bash
#!/bin/bash
# Find low quality resources

pharos quality outliers \
  --min-score 0.3 \
  --format json \
  | jq '.outliers[] | select(.quality_overall < 0.5)' \
  > low_quality_resources.json

echo "Found $(wc -l < low_quality_resources.json) low quality resources"
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Pharos Integration

on:
  push:
    branches: [main]
  pull_request:

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install Pharos CLI
        run: pip install pharos-cli
      
      - name: Configure Pharos
        run: |
          pharos config init --non-interactive \
            --url ${{ secrets.PHAROS_URL }} \
            --api-key ${{ secrets.PHAROS_API_KEY }}
      
      - name: Add code to knowledge base
        run: |
          pharos resource import ./src/ \
            --pattern "*.py" \
            --type code \
            --workers 4
      
      - name: Run code analysis
        run: |
          pharos code scan ./src/ --format json > analysis.json
          echo "Analysis complete"
      
      - name: Check quality
        run: |
          pharos quality outliers --format json > quality_report.json
          if [ $(jq '.total' quality_report.json) -gt 0 ]; then
            echo "Quality issues found"
            exit 1
          fi
```

### GitLab CI Example

```yaml
stages:
  - analyze

pharos-analysis:
  stage: analyze
  image: python:3.11
  before_script:
    - pip install pharos-cli
    - pharos config init --non-interactive --url $PHAROS_URL --api-key $PHAROS_API_KEY
  script:
    - pharos resource import ./src/ --pattern "*.py"
    - pharos code scan ./src/ --format json > analysis.json
  artifacts:
    reports:
      json: analysis.json
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    environment {
        PHAROS_URL = credentials('pharos-url')
        PHAROS_API_KEY = credentials('pharos-api-key')
    }
    
    stages {
        stage('Analyze') {
            steps {
                sh '''
                    pip install pharos-cli
                    pharos config init --non-interactive \
                        --url $PHAROS_URL \
                        --api-key $PHAROS_API_KEY
                    
                    pharos resource import ./src/ --pattern "*.py"
                    pharos code scan ./src/ --format json > analysis.json
                '''
            }
        }
        
        stage('Quality Check') {
            steps {
                sh '''
                    pharos quality outliers --format json > quality.json
                    if [ $(jq '.total' quality.json) -gt 0 ]; then
                        echo "Quality issues found"
                        exit 1
                    fi
                '''
            }
        }
    }
}
```

---

## Interactive Workflows

### Research Workflow

```bash
# 1. Create a collection for the research topic
pharos collection create "Machine Learning Research"

# 2. Add papers to the collection
pharos resource add ./papers/paper1.pdf --type paper
pharos resource add ./papers/paper2.pdf --type paper

# 3. Add to collection
pharos collection add 1 1
pharos collection add 1 2

# 4. Search within the collection
pharos search "neural networks" --collection 1

# 5. Ask questions about the papers
pharos ask "What are the main contributions of these papers?" --collection 1 --show-sources

# 6. Export the collection for sharing
pharos collection export 1 --format zip --output ml_research.zip
```

### Code Review Workflow

```bash
# 1. Analyze new code
pharos code analyze ./new_feature.py

# 2. Check for similar code
pharos recommend similar $(pharos resource add ./new_feature.py --format quiet)

# 3. Check quality
pharos quality score $(pharos resource add ./new_feature.py --format quiet)

# 4. Add to knowledge base
pharos resource add ./new_feature.py --type code --language python

# 5. Add to relevant collection
pharos collection add 5 $(pharos resource add ./new_feature.py --format quiet)
```

### Knowledge Graph Exploration

```bash
# 1. Get graph statistics
pharos graph stats

# 2. Find related resources
pharos graph related 123

# 3. Explore neighbors
pharos graph neighbors 123 --limit 20

# 4. Discover connections
pharos graph discover "machine learning" "drug discovery"

# 5. Check for contradictions
pharos graph contradictions

# 6. Export graph
pharos graph export --format graphml -o knowledge_graph.graphml
```

---

## Performance Optimization

### Parallel Processing

```bash
# Use multiple workers for batch operations
pharos resource import ./large_project/ --workers 8

pharos batch delete "1,2,3,4,5,6,7,8" --workers 8

pharos batch export --collection 1 --workers 8
```

### Caching

```bash
# Disable progress bars for scripting (faster)
pharos resource list --format json > /dev/null

# Use quiet mode for processing
pharos resource list --format quiet | while read id; do
  pharos resource get $id --format json
done
```

### Pagination Best Practices

```bash
# Don't load all results at once
for page in $(seq 1 100); do
  pharos resource list --page $page --per-page 100 --format json
  # Process results
  # Break if no more results
done

# Use limit to control output size
pharos search "query" --limit 50
```

### Efficient Searches

```bash
# Use specific filters to reduce results
pharos search "python" --type code --language python --min-quality 0.8

# Use semantic search for conceptual queries (more accurate)
pharos search "how to implement transformers" --semantic

# Use hybrid search for balanced results
pharos search "python decorators" --hybrid --weight 0.7
```

---

## Error Handling

### Basic Error Handling

```bash
#!/bin/bash
# Safe resource deletion

RESOURCE_ID=$1

if [ -z "$RESOURCE_ID" ]; then
  echo "Usage: $0 <resource_id>"
  exit 1
fi

if pharos resource get "$RESOURCE_ID" --format json > /dev/null 2>&1; then
  pharos resource delete "$RESOURCE_ID" --force
  echo "Resource $RESOURCE_ID deleted"
else
  echo "Resource $RESOURCE_ID not found"
  exit 1
fi
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

### Validation

```bash
#!/bin/bash
# Validate before operation

RESOURCE_ID=$1

# Check if resource exists
if ! pharos resource get "$RESOURCE_ID" --format json > /dev/null 2>&1; then
  echo "Error: Resource $RESOURCE_ID not found"
  exit 1
fi

# Check quality before export
QUALITY=$(pharos resource quality "$RESOURCE_ID" --format json | jq '.overall_score')
if (( $(echo "$QUALITY < 0.5" | bc -l) )); then
  echo "Warning: Resource has low quality score ($QUALITY)"
fi

# Proceed with operation
pharos resource get "$RESOURCE_ID" --format json > export.json
```

---

## Best Practices

### 1. Use Configuration Profiles

```bash
# Development profile
pharos config init  # Creates default profile

# Production profile
pharos config init
pharos config show --profile production

# Use specific profile
PHAROS_PROFILE=production pharos resource list
```

### 2. Secure API Key Handling

```bash
# Never commit API keys
echo "PHAROS_API_KEY=your_key_here" >> .env
source .env

# Use environment variables in CI/CD
export PHAROS_API_KEY=${{ secrets.PHAROS_API_KEY }}
```

### 3. Use Dry Run for Destructive Operations

```bash
# Always dry run first
pharos batch delete "1,2,3" --dry-run

# Review the output
# Then run without --dry-run
pharos batch delete "1,2,3" --force
```

### 4. Log Operations

```bash
#!/bin/bash
# Log all operations

LOG_FILE="pharos_operations.log"

log_operation() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log_operation "Starting resource import"
pharos resource import ./src/ --pattern "*.py" >> "$LOG_FILE" 2>&1
log_operation "Resource import complete"
```

### 5. Regular Maintenance

```bash
# Check health regularly
pharos health

# Monitor quality
pharos quality outliers --format json

# Clear cache periodically
pharos cache clear --force

# Backup before major operations
pharos backup --output backup_$(date +%Y%m%d).json
```

---

## See Also

- [Command Reference](command-reference.md)
- [Workflows](workflows.md)
- [Cheat Sheet](cheat-sheet.md)
- [Installation Guide](installation.md)
- [Configuration Guide](configuration.md)