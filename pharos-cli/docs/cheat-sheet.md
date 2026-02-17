# Pharos CLI Cheat Sheet

Quick reference guide for Pharos CLI commands.

## Installation & Setup

```bash
# Install
pip install pharos-cli

# Verify installation
pharos --version

# Initialize configuration
pharos config init

# Authenticate
pharos auth login --api-key YOUR_KEY

# Check health
pharos health
```

---

## Global Options

```bash
--color auto|always|never   # Color output
--no-color                  # Disable colors
--pager auto|always|never   # Pager mode
--no-pager                  # Disable pager
--help, -h                  # Show help
--version                   # Show version
```

---

## Authentication

```bash
# Login with API key
pharos auth login --api-key KEY

# Login with OAuth2
pharos auth login --oauth

# Check status
pharos auth status

# Show current user
pharos auth whoami

# Logout
pharos auth logout
```

---

## Configuration

```bash
# Initialize config
pharos config init

# Show config
pharos config show
pharos config show --format json

# Show config path
pharos config path
```

---

## Resources

```bash
# Add resource
pharos resource add ./file.py
pharos resource add --url URL --type paper
cat file.txt | pharos resource add --stdin

# List resources
pharos resource list
pharos resource list --type code --language python
pharos resource list --min-quality 0.8
pharos resource list --page 2 --per-page 50

# Get resource
pharos resource get 1
pharos resource get 1 --content

# Update resource
pharos resource update 1 --title "New Title"

# Delete resource
pharos resource delete 1
pharos resource delete 1 --force

# Import directory
pharos resource import ./dir/ --recursive --workers 4

# Resource quality
pharos resource quality 1
pharos resource annotations 1
```

---

## Search

```bash
# Basic search
pharos search "machine learning"

# Semantic search
pharos search "neural networks" --semantic

# Hybrid search
pharos search "AI" --hybrid --weight 0.7

# With filters
pharos search "python" --type code --language python
pharos search "tutorial" --min-quality 0.8
pharos search "query" --collection 1

# Save results
pharos search "query" --output results.json

# Output formats
pharos search "query" --format json
pharos search "query" --format csv
pharos search "query" --format quiet  # IDs only
```

---

## Collections

```bash
# Create collection
pharos collection create "My Collection"
pharos collection create "Name" --description "Desc" --public

# List collections
pharos collection list
pharos collection list --query "search"

# Show collection
pharos collection show 1
pharos collection show 1 --contents

# Add/remove resource
pharos collection add 1 5      # Add resource 5 to collection 1
pharos collection remove 1 5   # Remove resource 5 from collection 1

# Update collection
pharos collection update 1 --name "New Name"

# Delete collection
pharos collection delete 1
pharos collection delete 1 --force

# Export collection
pharos collection export 1
pharos collection export 1 --format zip --output file.zip

# Collection stats
pharos collection stats 1
```

---

## Annotations

```bash
# Create annotation
pharos annotate 1 --text "Note" --start 100 --end 200

# List annotations
pharos annotate list 1

# Search annotations
pharos annotate search "TODO"

# Delete annotation
pharos annotate delete 1

# Export annotations
pharos annotate export 1
pharos annotate export 1 --format md

# Import annotations
pharos annotate import file.json
```

---

## Knowledge Graph

```bash
# Graph stats
pharos graph stats

# Citations
pharos graph citations 1

# Related resources
pharos graph related 1
pharos graph related 1 --limit 20

# Neighbors
pharos graph neighbors 1
pharos graph neighbors 1 --limit 15

# Graph overview
pharos graph overview
pharos graph overview --limit 100 --threshold 0.8

# Export graph
pharos graph export --format graphml -o graph.graphml

# Contradictions
pharos graph contradictions

# Discover hypotheses
pharos graph discover "A" "C"
pharos graph discover "AI" "healthcare" --limit 20

# Centrality
pharos graph centrality
pharos graph centrality --top 20

# Entities
pharos graph entities
pharos graph entities --type Concept
pharos graph entities --name "transformer"

# Traverse
pharos graph traverse entity-id
pharos graph traverse entity-id --relations EXTENDS --hops 3

# Generate embeddings
pharos graph embeddings
pharos graph embeddings --algorithm deepwalk --dimensions 256
```

---

## Quality Assessment

```bash
# Quality score
pharos quality score 1
pharos quality score 1 --verbose

# Outliers
pharos quality outliers
pharos quality outliers --min-score 0.3
pharos quality outliers --format json

# Recompute
pharos quality recompute 1
pharos quality recompute 1 --async

# Collection report
pharos quality report 1
pharos quality report 1 --output report.json

# Distribution
pharos quality distribution
pharos quality distribution --dimension accuracy

# Dimensions
pharos quality dimensions

# Trends
pharos quality trends
pharos quality trends --granularity monthly

# Review queue
pharos quality review-queue

# Health
pharos quality health
```

---

## Taxonomy

```bash
# List categories
pharos taxonomy list
pharos taxonomy list --parent cat-1
pharos taxonomy list --depth 2

# Classify resource
pharos taxonomy classify 1
pharos taxonomy classify 1 --force
pharos taxonomy classify 1 --verbose

# Train model
pharos taxonomy train
pharos taxonomy train --categories cat-1,cat-2
pharos taxonomy train --no-wait

# Stats
pharos taxonomy stats

# Category details
pharos taxonomy category cat-1
pharos taxonomy category cat-1 --children --similar

# Search categories
pharos taxonomy search "machine learning"

# Distribution
pharos taxonomy distribution
pharos taxonomy distribution --dimension confidence

# Model info
pharos taxonomy model

# Health
pharos taxonomy health

# Export
pharos taxonomy export
pharos taxonomy export --format json -o taxonomy.json
```

---

## Recommendations

```bash
# User recommendations
pharos recommend for-user 1
pharos recommend for-user 1 --limit 20
pharos recommend for-user 1 --explain

# Similar resources
pharos recommend similar 1
pharos recommend similar 1 --limit 20

# Explain recommendation
pharos recommend explain 1
pharos recommend explain 1 --user 1

# Trending
pharos recommend trending
pharos recommend trending --limit 20
pharos recommend trending --time-range day

# Personalized feed
pharos recommend feed 1
pharos recommend feed 1 --limit 50
```

---

## Code Analysis

```bash
# Analyze file
pharos code analyze ./file.py
pharos code analyze ./file.py --format json

# Extract AST
pharos code ast ./file.py
pharos code ast ./file.py --format json -o ast.json

# Dependencies
pharos code deps ./file.py
pharos code deps ./file.py --transitive

# Chunk code
pharos code chunk ./file.py
pharos code chunk ./file.py --strategy semantic --chunk-size 1000

# Scan directory
pharos code scan ./project/
pharos code scan ./project/ --pattern "*.py"
pharos code scan ./project/ --format json

# List languages
pharos code languages

# Code stats
pharos code stats ./project/
pharos code stats ./file.py
```

---

## RAG & Chat

```bash
# Ask question
pharos ask "What is machine learning?"
pharos ask "Explain neural networks" --show-sources
pharos ask "How does auth work?" --strategy graphrag
pharos ask "Question" --collection 1
pharos ask "Question" --output answer.md

# Streaming answer
pharos ask stream "What is AI?"

# Find sources
pharos ask sources "What is neural networks?"
pharos ask sources "Question" --format json --output sources.json

# List strategies
pharos ask strategies

# Health check
pharos ask health

# Interactive chat
pharos chat
pharos chat --strategy graphrag
pharos chat --sources

# Chat commands
/help           # Show help
/exit, /quit    # Exit chat
/clear          # Clear screen
/history        # Show history
/sources on/off # Toggle sources
/strategy <name> # Set strategy
/system         # Show config
/reset          # Reset context
```

---

## Batch Operations

```bash
# Batch delete
pharos batch delete "1,2,3"
pharos batch delete "1,2,3" --dry-run
pharos batch delete "1,2,3" --force
pharos batch delete "1,2,3" --workers 8

# Batch update
pharos batch update updates.json
pharos batch update updates.json --dry-run

# Batch export
pharos batch export --collection 1
pharos batch export --ids "1,2,3" --format zip
pharos batch export --collection 1 --output ./exports/
```

**Update file format:**
```json
{
  "updates": [
    {"id": 1, "title": "New Title"},
    {"id": 2, "tags": ["important"]}
  ]
}
```

---

## System Commands

```bash
# Health check
pharos health
pharos health --verbose
pharos health --format json

# System stats
pharos stats
pharos stats --format json

# Version
pharos version
pharos version --extended

# Backup
pharos backup --output backup.json
pharos backup --output backup.json --verbose

# Restore
pharos restore backup.json
pharos restore backup.json --force

# Verify backup
pharos verify-backup backup.json

# Clear cache
pharos cache clear
pharos cache clear --force

# Run migrations
pharos migrate
pharos migrate --force
```

---

## Backup Commands

```bash
# Create backup
pharos backup create --output backup.json
pharos backup create --output backup.sql --format sql
pharos backup create --output backup.json --no-verify

# Verify backup
pharos backup verify backup.json
pharos backup verify backup.json --detailed

# Restore backup
pharos backup restore backup.json
pharos backup restore backup.json --force
pharos backup restore backup.json --no-verify

# Backup info
pharos backup info backup.json
```

---

## Output Formats

```bash
# All commands support these formats
--format table    # Default, rich tables
--format json     # JSON for scripting
--format csv      # CSV for spreadsheets
--format tree     # Tree for hierarchy
--format quiet    # IDs only for piping
```

---

## Shell Completion

```bash
# Bash
pharos completion bash >> ~/.bashrc

# Zsh
pharos completion zsh >> ~/.zshrc

# Fish
pharos completion fish > ~/.config/fish/completions/pharos.fish
```

---

## Environment Variables

```bash
export PHAROS_API_URL="https://pharos.onrender.com"
export PHAROS_API_KEY="your-api-key"
export PHAROS_PROFILE="production"
export PHAROS_OUTPUT_FORMAT="json"
export PHAROS_NO_COLOR="1"
export PHAROS_VERIFY_SSL="1"
```

---

## Common Patterns

```bash
# Find and get details
pharos resource list --type paper --format quiet | head -5 | \
  xargs -I {} pharos resource get {}

# Search and export
pharos search "machine learning" --format json | \
  jq '.items[:10]' > top_results.json

# Batch quality check
pharos quality outliers --format json | \
  jq '.outliers[] | select(.quality_overall < 0.5)'

# Collection summary
pharos collection show 1 --contents --contents-limit 10

# Graph neighbors for visualization
pharos graph neighbors 1 --limit 20 --format json > neighbors.json
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Authentication error |
| 4 | Resource not found |
| 5 | Network error |

---

## Quick Reference

| Task | Command |
|------|---------|
| Add file | `pharos resource add ./file.py` |
| List all | `pharos resource list` |
| Search | `pharos search "query"` |
| Ask question | `pharos ask "question"` |
| Start chat | `pharos chat` |
| Check health | `pharos health` |
| Create backup | `pharos backup --output backup.json` |
| Get help | `pharos --help` |

---

## See Also

- [Command Reference](command-reference.md)
- [Usage Patterns](usage-patterns.md)
- [Workflows](workflows.md)
- [Man Pages](man-pages.md)
- [Installation Guide](installation.md)
- [Configuration Guide](configuration.md)