# Getting Started with Pharos CLI

A step-by-step tutorial to help you install, configure, and start using the Pharos CLI effectively.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Initial Configuration](#initial-configuration)
- [Authentication](#authentication)
- [Your First Commands](#your-first-commands)
- [Adding Resources](#adding-resources)
- [Searching Your Knowledge Base](#searching-your-knowledge-base)
- [Managing Collections](#managing-collections)
- [Asking Questions](#asking-questions)
- [Next Steps](#next-steps)

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8 or later** - Check with `python --version`
- **pip or pipx** - For installing the CLI
- **API access** - You need a Pharos backend URL and API key
- **Terminal access** - Command-line experience

```bash
# Verify Python version
python --version

# Verify pip is available
pip --version
```

---

## Installation

### Option 1: Install via pip (Recommended)

```bash
pip install pharos-cli
```

### Option 2: Install via pipx (Isolated Installation)

```bash
pipx install pharos-cli
```

### Option 3: Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/pharos-cli
cd pharos-cli

# Install in development mode
pip install -e .
```

### Verify Installation

```bash
# Check version
pharos --version

# Show help
pharos --help
```

You should see output similar to:

```
Pharos CLI v0.1.0
Usage: pharos [OPTIONS] COMMAND [ARGUMENTS]

Commands:
  auth        Authentication commands
  resource    Resource management
  search      Search knowledge base
  collection  Collection management
  annotate    Annotation commands
  graph       Knowledge graph commands
  quality     Quality assessment
  taxonomy    Taxonomy and classification
  recommend   Recommendations
  code        Code analysis
  ask         Ask questions (RAG)
  chat        Interactive chat mode
  batch       Batch operations
  health      System health check
  config      Configuration management
  completion  Shell completion setup
  version     Show version

Options:
  --help     Show this message and exit.
  --version  Show version information.
```

---

## Initial Configuration

### Interactive Setup

Run the configuration wizard:

```bash
pharos config init
```

The wizard will prompt you for:

1. **API URL** - Your Pharos backend URL (e.g., `https://pharos.onrender.com`)
2. **API Key** - Your authentication key
3. **Default output format** - table, json, csv, or quiet
4. **Color output preference** - auto, always, or never

### Non-Interactive Setup

For scripts or CI/CD environments:

```bash
pharos config init \
  --url https://pharos.onrender.com \
  --api-key YOUR_API_KEY \
  --non-interactive
```

### Environment Variables

You can also configure via environment variables:

```bash
export PHAROS_API_URL="https://pharos.onrender.com"
export PHAROS_API_KEY="your-api-key-here"
export PHAROS_OUTPUT_FORMAT="json"
export PHAROS_NO_COLOR="1"
```

### Verify Configuration

```bash
# Show current configuration
pharos config show

# Show config file location
pharos config path
```

---

## Authentication

### Login with API Key

```bash
pharos auth login --api-key YOUR_API_KEY
```

### Login with OAuth2 (Interactive)

```bash
pharos auth login --oauth
```

This opens a browser for authentication with your identity provider.

### Verify Authentication

```bash
# Check current user
pharos auth whoami

# Check authentication status
pharos auth status
```

### Logout

```bash
pharos auth logout
```

---

## Your First Commands

### Health Check

Verify your connection to the Pharos backend:

```bash
pharos health
```

Expected output:

```
✓ Pharos API is healthy
Version: 0.1.0
Uptime: 2h 15m
```

### Check System Status

```bash
# Get system statistics
pharos stats

# Show version details
pharos version --extended
```

---

## Adding Resources

### Add a Single File

```bash
# Add a Python file
pharos resource add ./example.py

# Add with explicit type
pharos resource add ./document.pdf --type paper

# Add with title
pharos resource add ./readme.md --title "Project README"
```

### Add from URL

```bash
pharos resource add --url https://example.com/article --type documentation
```

### Add from stdin

```bash
cat ./notes.txt | pharos resource add --stdin --title "My Notes"
```

### List Your Resources

```bash
# List all resources
pharos resource list

# List with pagination
pharos resource list --page 1 --per-page 20

# List with filters
pharos resource list --type code --language python

# List high-quality resources only
pharos resource list --min-quality 0.8
```

### Get Resource Details

```bash
# Get by ID (replace 1 with your resource ID)
pharos resource get 1

# Include content
pharos resource get 1 --content

# Get in JSON format
pharos resource get 1 --format json
```

---

## Searching Your Knowledge Base

### Basic Search

```bash
# Keyword search
pharos search "machine learning"

# Search with type filter
pharos search "API" --type code

# Search with quality filter
pharos search "tutorial" --min-quality 0.8
```

### Semantic Search

Semantic search finds conceptually similar content, not just keyword matches:

```bash
# Find conceptually related content
pharos search "how neural networks learn" --semantic

# Hybrid search (keyword + semantic)
pharos search "python decorators" --hybrid --weight 0.7
```

### Advanced Search

```bash
# Multiple filters
pharos search "python" \
  --type code \
  --language python \
  --min-quality 0.7 \
  --tags tutorial

# Search within a collection
pharos search "transformers" --collection 1

# Limit results
pharos search "query" --limit 10
```

### Save Search Results

```bash
# Save results to file
pharos search "machine learning" --output results.json

# Save as CSV
pharos search "python" --format csv --output results.csv
```

---

## Managing Collections

Collections help you organize related resources.

### Create a Collection

```bash
# Create a basic collection
pharos collection create "Machine Learning Papers"

# Create with description
pharos collection create "Python Tutorials" \
  --description "Helpful Python programming guides"
```

### Add Resources to Collection

```bash
# Add by resource ID
pharos collection add 1 5    # Add resource 5 to collection 1

# Add multiple resources
pharos collection add 1 5,6,7,8
```

### View Collection Contents

```bash
# Show collection details
pharos collection show 1

# Show with contents
pharos collection show 1 --contents

# Limit contents shown
pharos collection show 1 --contents --contents-limit 10
```

### List Your Collections

```bash
# List all collections
pharos collection list

# Search collections
pharos collection list --query "machine learning"
```

### Export a Collection

```bash
# Export as ZIP
pharos collection export 1 --format zip --output ml_papers.zip

# Export as JSON
pharos collection export 1 --format json --output ml_papers.json
```

### Delete a Collection

```bash
pharos collection delete 1
```

---

## Asking Questions

Use the RAG (Retrieval-Augmented Generation) feature to ask questions about your knowledge base.

### Basic Question

```bash
pharos ask "What is machine learning?"
```

### With Source Citations

```bash
pharos ask "Explain neural networks" --show-sources
```

### Specify Resources

```bash
# Ask about specific resources
pharos ask "What are the key findings?" --resources 1,2,3

# Ask within a collection
pharos ask "Summarize the main concepts" --collection 1
```

### Different Retrieval Strategies

```bash
# GraphRAG (uses knowledge graph)
pharos ask "How are these concepts connected?" --strategy graphrag

# Hybrid search
pharos ask "Compare approaches" --strategy hybrid
```

### Save Answer

```bash
pharos ask "Explain transformers architecture" --output answer.md
```

### Interactive Chat Mode

For ongoing conversations:

```bash
pharos chat
```

Chat commands:
- `/help` - Show help
- `/exit` or `/quit` - Exit chat
- `/clear` - Clear conversation
- `/history` - Show conversation history
- `/sources on/off` - Toggle source citations
- `/strategy <name>` - Change retrieval strategy

---

## Next Steps

Now that you've completed the basics, explore these areas:

### 1. Code Analysis

```bash
# Analyze a code file
pharos code analyze ./your_file.py

# Extract AST
pharos code ast ./your_file.py

# Find dependencies
pharos code deps ./your_file.py

# Scan entire project
pharos code scan ./project/
```

### 2. Knowledge Graph

```bash
# View graph statistics
pharos graph stats

# Find related resources
pharos graph related 1

# Discover connections
pharos graph discover "AI" "healthcare"
```

### 3. Quality Assessment

```bash
# Check quality score
pharos quality score 1

# Find low-quality resources
pharos quality outliers

# Generate collection report
pharos quality report 1
```

### 4. Batch Operations

```bash
# Import multiple files
pharos resource import ./project/ --pattern "*.py" --recursive

# Batch delete
pharos batch delete "1,2,3,4,5"

# Batch update
pharos batch update updates.json
```

### 5. Annotations

```bash
# Create annotation
pharos annotate 1 --text "Important concept" --start 100 --end 200

# List annotations
pharos annotate list 1

# Export annotations
pharos annotate export 1 --format md
```

### 6. Recommendations

```bash
# Get similar resources
pharos recommend similar 1

# Get recommendations for user
pharos recommend for-user 1
```

---

## Common Issues

### Connection Refused

```bash
# Check API URL
pharos config show | grep api_url

# Test connection
pharos health --verbose
```

### Authentication Failed

```bash
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
```

### Slow Performance

```bash
# Check system stats
pharos stats

# Clear cache
pharos cache clear --force
```

---

## Getting Help

```bash
# General help
pharos --help

# Command-specific help
pharos resource --help
pharos search --help

# Subcommand help
pharos resource add --help
pharos collection create --help
```

---

## See Also

- [Command Reference](command-reference.md)
- [Usage Patterns](usage-patterns.md)
- [Workflows](workflows.md)
- [Cheat Sheet](cheat-sheet.md)
- [Installation Guide](installation.md)
- [Configuration Guide](configuration.md)