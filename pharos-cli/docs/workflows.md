# Pharos CLI Workflows

Common workflows and use cases for the Pharos CLI.

## Table of Contents

- [Getting Started Workflow](#getting-started-workflow)
- [Research Paper Management](#research-paper-management)
- [Codebase Analysis](#codebase-analysis)
- [Knowledge Graph Exploration](#knowledge-graph-exploration)
- [Quality Assurance](#quality-assurance)
- [Batch Operations](#batch-operations-1)
- [CI/CD Integration](#cicd-integration)
- [Data Export and Reporting](#data-export-and-reporting)
- [Troubleshooting Workflows](#troubleshooting-workflows)

---

## Getting Started Workflow

Complete workflow for new users to set up and start using Pharos CLI.

### Step 1: Installation

```bash
# Install via pip
pip install pharos-cli

# Verify installation
pharos --version
```

### Step 2: Configuration

```bash
# Initialize configuration (interactive)
pharos config init

# Or non-interactive setup
pharos config init \
  --url https://pharos.onrender.com \
  --api-key YOUR_API_KEY \
  --non-interactive
```

### Step 3: Authentication

```bash
# API key authentication
pharos auth login --api-key YOUR_API_KEY

# Verify authentication
pharos auth whoami
```

### Step 4: Health Check

```bash
# Verify connection to backend
pharos health

# If issues, check configuration
pharos config show
```

### Step 5: Add First Resources

```bash
# Add a code file
pharos resource add ./example.py

# Add a documentation file
pharos resource add ./README.md --type documentation

# List your resources
pharos resource list
```

### Step 6: Try a Search

```bash
# Search for your added content
pharos search "example"

# Try semantic search
pharos search "what does this code do" --semantic
```

---

## Research Paper Management

Workflow for researchers managing academic papers.

### Creating a Research Collection

```bash
# Create a collection for a research topic
pharos collection create "Machine Learning Papers 2024" \
  --description "Papers on ML from 2024"

# Note the collection ID (e.g., 1)
```

### Adding Papers

```bash
# Add individual papers
pharos resource add ./papers/attention_is_all_you_need.pdf \
  --type paper \
  --title "Attention Is All You Need"

pharos resource add ./papers/bert_pre-training.pdf \
  --type paper \
  --title "BERT: Pre-training of Deep Bidirectional Transformers"

# Add to collection
pharos collection add 1 1  # Add paper 1 to collection 1
pharos collection add 1 2  # Add paper 2 to collection 1
```

### Batch Import Papers

```bash
# Import all PDFs from a directory
pharos resource import ./papers/ \
  --pattern "*.pdf" \
  --type paper \
  --recursive

# Check import results
pharos resource list --type paper
```

### Searching Papers

```bash
# Search within collection
pharos search "transformer architecture" --collection 1

# Find high-quality papers
pharos search "neural networks" --collection 1 --min-quality 0.9

# Semantic search for conceptual queries
pharos search "how do attention mechanisms work" --semantic --collection 1
```

### Analyzing Papers

```bash
# Get paper details
pharos resource get 1

# Check quality assessment
pharos resource quality 1

# View annotations (if any)
pharos resource annotations 1
```

### Asking Questions About Papers

```bash
# Get summary of a paper
pharos ask "What are the main contributions of this paper?" \
  --resources 1 \
  --show-sources

# Compare concepts across papers
pharos ask "Compare the attention mechanisms in these papers" \
  --resources 1,2 \
  --show-sources

# Find related work
pharos ask "What papers cite or are related to this work?" \
  --resources 1 \
  --strategy graphrag
```

### Exporting Collection

```bash
# Export as ZIP for sharing
pharos collection export 1 \
  --format zip \
  --output "ML_Papers_2024.zip"

# Export as JSON for analysis
pharos collection export 1 \
  --format json \
  --output "ml_papers_data.json"
```

---

## Codebase Analysis

Workflow for analyzing and understanding codebases.

### Initial Codebase Scan

```bash
# Scan entire codebase
pharos code scan ./src/

# Scan with specific pattern
pharos code scan ./src/ --pattern "*.py"

# Recursive scan (default)
pharos code scan ./project/ --recursive

# Get statistics
pharos code stats ./project/
```

### Analyzing Individual Files

```bash
# Analyze a single file
pharos code analyze ./src/main.py

# Extract AST for deep analysis
pharos code ast ./src/main.py --format json -o main_ast.json

# Show dependencies
pharos code deps ./src/main.py

# Chunk code for indexing
pharos code chunk ./src/main.py \
  --strategy semantic \
  --chunk-size 1000 \
  -o chunks.txt
```

### Finding Similar Code

```bash
# Find resources similar to a file
pharos recommend similar 1

# Get recommendations for a file
pharos recommend similar 1 --limit 10

# Explain why files are similar
pharos recommend explain 1 --explain
```

### Quality Assessment

```bash
# Check quality score
pharos quality score 1

# Get detailed breakdown
pharos quality score 1 --verbose

# Find low-quality code
pharos quality outliers --min-score 0.3

# Recompute quality
pharos quality recompute 1 --async
```

### Adding Code to Knowledge Base

```bash
# Add single file
pharos resource add ./src/utils.py \
  --type code \
  --language python

# Add entire directory
pharos resource import ./src/ \
  --pattern "*.py" \
  --type code \
  --workers 4

# Add with auto-detection
pharos resource add ./script.py
```

### Searching Code

```bash
# Keyword search
pharos search "authentication" --type code

# Semantic search for functionality
pharos search "how to validate user input" --semantic --type code

# Filter by language
pharos search "database" --type code --language python

# Filter by quality
pharos search "API" --type code --min-quality 0.8
```

---

## Knowledge Graph Exploration

Workflow for exploring and discovering connections in your knowledge graph.

### Getting Started with Graph

```bash
# View graph statistics
pharos graph stats

# See graph overview
pharos graph overview

# Check centrality scores
pharos graph centrality --top 20
```

### Finding Related Resources

```bash
# Get related resources for a resource
pharos graph related 1

# Get neighbors for visualization
pharos graph neighbors 1 --limit 15

# Find similar resources
pharos recommend similar 1
```

### Literature-Based Discovery

```bash
# Discover connections between concepts
pharos graph discover "machine learning" "drug discovery"

# With time constraints
pharos graph discover "AI" "healthcare" \
  --start-date 2020-01-01 \
  --end-date 2024-12-31

# Limit results
pharos graph discover "neural networks" "biology" --limit 20
```

### Checking for Contradictions

```bash
# Find contradictions in your knowledge base
pharos graph contradictions
```

### Entity Exploration

```bash
# List all entities
pharos graph entities

# Filter by type
pharos graph entities --type Concept
pharos graph entities --type Person

# Search entities
pharos graph entities --name "transformer" --limit 20
```

### Graph Traversal

```bash
# Traverse from an entity
pharos graph traverse entity-id-123

# With specific relations
pharos graph traverse entity-id-123 \
  --relations EXTENDS,SUPPORTS \
  --hops 3
```

### Exporting Graph

```bash
# Export as GraphML for visualization
pharos graph export --format graphml -o knowledge_graph.graphml

# Export as JSON
pharos graph export --format json -o graph_data.json

# Export as CSV
pharos graph export --format csv -o graph_data.csv
```

### Generating Embeddings

```bash
# Generate graph embeddings
pharos graph embeddings

# With custom parameters
pharos graph embeddings \
  --algorithm node2vec \
  --dimensions 256 \
  --walk-length 100
```

---

## Quality Assurance

Workflow for maintaining quality in your knowledge base.

### Regular Quality Checks

```bash
# Check overall quality module health
pharos quality health

# View quality distribution
pharos quality distribution

# View dimension averages
pharos quality dimensions
```

### Finding Issues

```bash
# List quality outliers
pharos quality outliers

# Filter by severity
pharos quality outliers --min-score 0.5

# Get review queue
pharos quality review-queue
```

### Addressing Quality Issues

```bash
# Get details for a specific resource
pharos quality score 1 --verbose

# Recompute quality
pharos quality recompute 1

# Recompute asynchronously
pharos quality recompute 1 --async

# Generate report for collection
pharos quality report 1 --output quality_report.json
```

### Quality Trends

```bash
# View quality trends
pharos quality trends

# Over time period
pharos quality trends \
  --granularity monthly \
  --start-date 2024-01-01

# By dimension
pharos quality trends --dimension accuracy
```

### Collection Quality Report

```bash
# Generate comprehensive report
pharos quality report 1

# Save report
pharos quality report 1 --output collection_quality.json

# View recommendations
pharos quality report 1 | grep -A 5 "Recommendations"
```

---

## Batch Operations

Workflows for managing resources at scale.

### Bulk Import

```bash
# Import from directory
pharos resource import ./data/ \
  --recursive \
  --workers 8 \
  --skip-errors

# Import specific file types
pharos resource import ./project/ \
  --pattern "*.{py,js,ts,java}" \
  --type code \
  --workers 4
```

### Bulk Delete

```bash
# Delete by IDs
pharos batch delete "1,2,3,4,5"

# Preview first
pharos batch delete "1,2,3,4,5" --dry-run

# Force delete
pharos batch delete "1,2,3,4,5" --force
```

### Bulk Update

```bash
# Create update file
cat > updates.json << 'EOF'
{
  "updates": [
    {"id": 1, "tags": ["updated", "review"]},
    {"id": 2, "quality_score": null},
    {"id": 3, "title": "New Title"}
  ]
}
EOF

# Apply updates
pharos batch update updates.json

# Preview
pharos batch update updates.json --dry-run
```

### Bulk Export

```bash
# Export entire collection
pharos batch export --collection 1 \
  --format zip \
  --output backup.zip

# Export specific resources
pharos batch export --ids "1,2,3,4,5" \
  --format json \
  --output resources.json

# Export as markdown
pharos batch export --collection 1 \
  --format markdown \
  --output ./docs/
```

### Parallel Processing

```bash
# Use multiple workers for speed
pharos resource import ./large_project/ --workers 10

pharos batch delete "1-100" --workers 10

pharos batch export --collection 1 --workers 8
```

---

## CI/CD Integration

Workflows for integrating Pharos into development pipelines.

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Analyze new/changed files
for file in $(git diff --cached --name-only | grep -E '\.(py|js|ts)$'); do
  echo "Analyzing: $file"
  pharos code analyze "$file"
  
  # Check quality
  RESOURCE_ID=$(pharos resource add "$file" --format quiet 2>/dev/null)
  if [ -n "$RESOURCE_ID" ]; then
    QUALITY=$(pharos quality score "$RESOURCE_ID" --format json | jq '.overall_score')
    if (( $(echo "$QUALITY < 0.5" | bc -l) )); then
      echo "Warning: Low quality score ($QUALITY) for $file"
    fi
  fi
done
```

### GitHub Actions Workflow

```yaml
name: Pharos Analysis

on:
  push:
    paths:
      - '**.py'
      - '**.js'
      - '**.ts'

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
      
      - name: Configure
        run: |
          pharos config init --non-interactive \
            --url ${{ secrets.PHAROS_URL }} \
            --api-key ${{ secrets.PHAROS_API_KEY }}
      
      - name: Import code
        run: |
          pharos resource import ./src/ \
            --pattern "*.py" \
            --type code \
            --workers 4
      
      - name: Analyze
        run: |
          pharos code scan ./src/ --format json > analysis.json
          
      - name: Quality Check
        run: |
          pharos quality outliers --format json > quality.json
          if [ $(jq '.total' quality.json) -gt 0 ]; then
            echo "Quality issues found:"
            jq '.outliers[] | "\(.resource_id): \(.quality_overall)"' quality.json
            exit 1
          fi
```

### Automated Backup

```bash
#!/bin/bash
# daily_backup.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="./backups"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Export all resources
pharos batch export \
  --format json \
  --output "$BACKUP_DIR/full_backup_$DATE.json"

# Export collections
pharos collection export 1 --format json -o "$BACKUP_DIR/collection1_$DATE.json"
pharos collection export 2 --format json -o "$BACKUP_DIR/collection2_$DATE.json"

# Export graph
pharos graph export --format graphml -o "$BACKUP_DIR/graph_$DATE.graphml"

# Verify backups
pharos backup verify "$BACKUP_DIR/full_backup_$DATE.json"

echo "Backup complete: $BACKUP_DIR/"
```

---

## Data Export and Reporting

Workflows for exporting data and generating reports.

### Collection Report

```bash
# Generate collection statistics
pharos collection stats 1

# Generate quality report
pharos quality report 1 --output collection_report.json

# Export collection
pharos collection export 1 --format json --output collection_data.json
```

### Resource Report

```bash
# Get all resources with quality
pharos resource list --format json | jq '.items[] | {id, title, quality_score}'

# Filter by quality
pharos resource list --min-quality 0.8 --format json > high_quality_resources.json

# Export annotations
pharos annotate export 1 --format md > annotations.md
```

### Graph Report

```bash
# Graph statistics
pharos graph stats --format json > graph_stats.json

# Centrality scores
pharos graph centrality --top 50 --format json > centrality_scores.json

# Entity list
pharos graph entities --format json > entities.json

# Contradictions
pharos graph contradictions --format json > contradictions.json
```

### Taxonomy Report

```bash
# Taxonomy statistics
pharos taxonomy stats

# Category distribution
pharos taxonomy distribution

# Model information
pharos taxonomy model

# Export taxonomy
pharos taxonomy export --format json -o taxonomy.json
```

### Comprehensive Report

```bash
#!/bin/bash
# generate_report.sh

OUTPUT_DIR="./reports/$(date +%Y%m%d)"
mkdir -p "$OUTPUT_DIR"

echo "Generating comprehensive report..."

# System stats
pharos stats --format json > "$OUTPUT_DIR/system_stats.json"

# Resources
pharos resource list --format json > "$OUTPUT_DIR/resources.json"

# Collections
pharos collection list --format json > "$OUTPUT_DIR/collections.json"

# Quality
pharos quality outliers --format json > "$OUTPUT_DIR/quality_outliers.json"
pharos quality distribution --format json > "$OUTPUT_DIR/quality_distribution.json"

# Graph
pharos graph stats --format json > "$OUTPUT_DIR/graph_stats.json"
pharos graph centrality --format json > "$OUTPUT_DIR/centrality.json"

# Taxonomy
pharos taxonomy stats --format json > "$OUTPUT_DIR/taxonomy_stats.json"

echo "Report generated in $OUTPUT_DIR/"
```

---

## Troubleshooting Workflows

Common troubleshooting workflows.

### Connection Issues

```bash
# Check API URL
pharos config show | grep api_url

# Test connection
pharos health

# Verbose health check
pharos health --verbose

# Check version
pharos version
```

### Authentication Issues

```bash
# Check auth status
pharos auth status

# Re-authenticate
pharos auth logout
pharos auth login --api-key YOUR_API_KEY

# Verify API key
pharos auth whoami
```

### Resource Not Found

```bash
# List available resources
pharos resource list

# Search for resource
pharos search "resource title"

# Check specific ID
pharos resource get 1
```

### Quality Issues

```bash
# Check quality module health
pharos quality health

# Recompute quality
pharos quality recompute 1

# Check for outliers
pharos quality outliers --min-score 0.3
```

### Performance Issues

```bash
# Check system stats
pharos stats

# Clear cache
pharos cache clear --force

# Check for large collections
pharos collection list | head -20
```

### Export Issues

```bash
# Verify backup file
pharos backup verify backup.json

# Check file format
pharos backup info backup.json

# Try different format
pharos collection export 1 --format json  # Instead of zip
```

### Debug Mode

```bash
# Enable verbose output
pharos resource get 1 --verbose

# Use JSON format for parsing
pharos resource get 1 --format json | jq '.'

# Check logs (if available)
cat ~/.pharos/logs/*.log 2>/dev/null || echo "No logs found"
```

---

## See Also

- [Command Reference](command-reference.md)
- [Usage Patterns](usage-patterns.md)
- [Cheat Sheet](cheat-sheet.md)
- [Installation Guide](installation.md)
- [Configuration Guide](configuration.md)