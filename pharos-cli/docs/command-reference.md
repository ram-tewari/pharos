# Pharos CLI Command Reference

Complete reference for all Pharos CLI commands with examples.

## Table of Contents

- [Global Options](#global-options)
- [Authentication Commands](#authentication-commands)
- [Configuration Commands](#configuration-commands)
- [Resource Commands](#resource-commands)
- [Search Commands](#search-commands)
- [Collection Commands](#collection-commands)
- [Annotation Commands](#annotation-commands)
- [Graph Commands](#graph-commands)
- [Quality Commands](#quality-commands)
- [Taxonomy Commands](#taxonomy-commands)
- [Recommendation Commands](#recommendation-commands)
- [Code Analysis Commands](#code-analysis-commands)
- [RAG Commands](#rag-commands)
- [Chat Command](#chat-command)
- [Batch Commands](#batch-commands)
- [System Commands](#system-commands)
- [Backup Commands](#backup-commands)
- [Output Formats](#output-formats)

---

## Global Options

These options apply to all commands:

| Option | Description |
|--------|-------------|
| `--color auto\|always\|never` | Color output mode (default: auto) |
| `--no-color` | Disable color output |
| `--pager auto\|always\|never` | Pager mode for long output (default: auto) |
| `--no-pager` | Disable pager output |

### Examples

```bash
# Disable colors for CI/CD pipelines
pharos --no-color resource list

# Force colors even in non-TTY
pharos --color always search "machine learning"

# Disable pager for scripting
pharos --no-pager collection list
```

---

## Authentication Commands

### `pharos auth login`

Authenticate with the Pharos API.

```bash
# API key authentication
pharos auth login --api-key YOUR_API_KEY

# OAuth2 interactive login (opens browser)
pharos auth login --oauth

# OAuth2 with specific provider
pharos auth login --oauth --provider github

# Set API URL during login
pharos auth login --api-key KEY --url https://pharos.onrender.com
```

**Options:**
- `--api-key, -k` - API key for authentication
- `--url, -u` - API URL (for first-time setup)
- `--oauth, -o` - Use OAuth2 interactive login
- `--provider` - OAuth2 provider (google, github)

### `pharos auth logout`

Logout and clear stored credentials.

```bash
pharos auth logout
```

### `pharos auth whoami`

Show current user information.

```bash
pharos auth whoami
```

### `pharos auth status`

Show authentication status.

```bash
pharos auth status
```

---

## Configuration Commands

### `pharos config init`

Initialize Pharos CLI configuration.

```bash
# Interactive setup
pharos config init

# Non-interactive with provided values
pharos config init --url https://pharos.onrender.com --api-key KEY
```

**Options:**
- `--url, -u` - API URL to use
- `--api-key, -k` - API key for authentication
- `--non-interactive, -n` - Run in non-interactive mode

### `pharos config show`

Show current configuration.

```bash
# Show active profile
pharos config show

# Show specific profile
pharos config show --profile production

# Show API key (use with caution)
pharos config show --show-api-key

# Output as JSON
pharos config show --format json
```

**Options:**
- `--profile, -p` - Profile to show
- `--show-api-key, -s` - Show API key
- `--format, -f` - Output format (rich, json, yaml)

### `pharos config path`

Show configuration file path.

```bash
pharos config path
```

### `pharos config dir`

Show configuration directory path.

```bash
pharos config dir
```

---

## Resource Commands

### `pharos resource add`

Add a new resource from file, URL, or stdin.

```bash
# Add from file
pharos resource add ./myfile.py
pharos resource add ./myfile.py --type code --language python

# Add from URL
pharos resource add --url https://example.com/paper.pdf --type paper

# Add from stdin
cat file.txt | pharos resource add --stdin --title "My Note"

# Add with content directly
pharos resource add --content "Hello World" --title "Greeting"
```

**Options:**
- `--url, -u` - URL to add as a resource
- `--title, -t` - Title for the resource
- `--type, -T` - Resource type (code, paper, documentation, etc.)
- `--language, -l` - Programming language or natural language
- `--stdin, -s` - readFile content from stdin
- `--content, -c` - Content directly

### `pharos resource list`

List resources with optional filters.

```bash
# List all resources
pharos resource list

# Filter by type and language
pharos resource list --type code --language python

# Search query
pharos resource list --query "machine learning"

# Filter by quality
pharos resource list --min-quality 0.8

# Filter by tags
pharos resource list --tags important,python

# Pagination
pharos resource list --page 2 --per-page 50

# Output formats
pharos resource list --format json
pharos resource list --format csv
pharos resource list --format quiet  # Just IDs
```

**Options:**
- `--type, -T` - Filter by resource type
- `--language, -l` - Filter by programming language
- `--query, -q` - Search query for title/content
- `--min-quality` - Minimum quality score (0.0-1.0)
- `--collection, -c` - Filter by collection ID
- `--tags` - Filter by tags (comma-separated)
- `--page, -p` - Page number
- `--per-page` - Items per page (1-100)
- `--format, -f` - Output format (json, table, csv, quiet)

### `pharos resource get`

Get resource details by ID.

```bash
pharos resource get 1
pharos resource get 1 --format json
pharos resource get 1 --content
pharos resource get 1 --content --content-lines 100
```

**Options:**
- `--format, -f` - Output format (json, table, tree)
- `--content` - Show resource content
- `--content-lines` - Number of content lines to show

### `pharos resource update`

Update resource metadata.

```bash
pharos resource update 1 --title "New Title"
pharos resource update 1 --type paper --language english
```

**Options:**
- `--title, -t` - New title
- `--content, -c` - New content
- `--type, -T` - New resource type
- `--language, -l` - New programming language

### `pharos resource delete`

Delete a resource by ID.

```bash
pharos resource delete 1
pharos resource delete 1 --force  # Skip confirmation
```

**Options:**
- `--force, -f` - Skip confirmation prompt

### `pharos resource quality`

Get quality score for a resource.

```bash
pharos resource quality 1
pharos resource quality 1 --format json
```

### `pharos resource annotations`

Get annotations for a resource.

```bash
pharos resource annotations 1
pharos resource annotations 1 --format json
```

### `pharos resource import`

Import resources from a directory.

```bash
# Import from directory
pharos resource import ./my_code/

# Recursive import
pharos resource import ./papers/ --recursive

# With custom workers
pharos resource import ./code/ --workers 8

# Dry run (show what would be imported)
pharos resource import ./code/ --dry-run
```

**Options:**
- `--recursive, -r` - Recursively scan subdirectories
- `--pattern, -p` - File pattern to match
- `--type, -T` - Resource type for all files
- `--language, -l` - Programming language for all files
- `--workers, -w` - Number of parallel workers (1-10)
- `--skip-errors/--no-skip-errors` - Skip files that fail
- `--dry-run` - Show what would be imported

---

## Search Commands

### `pharos search`

Search for resources in your knowledge base.

```bash
# Basic keyword search
pharos search "machine learning"

# Semantic search
pharos search "neural networks" --semantic

# Hybrid search
pharos search "AI" --hybrid --weight 0.7

# With filters
pharos search "python" --type code --language python

# Quality filter
pharos search "documentation" --min-quality 0.8

# Pagination
pharos search "query" --page 2 --per-page 50

# Save results
pharos search "machine learning" --output results.json

# Verbose output
pharos search "query" --verbose
```

**Options:**
- `--semantic, -s` - Use semantic search
- `--hybrid, -h` - Use hybrid search
- `--weight, -w` - Weight for hybrid search (0.0-1.0)
- `--type, -t` - Filter by resource type
- `--language, -l` - Filter by language
- `--min-quality, -q` - Minimum quality score
- `--max-quality` - Maximum quality score
- `--tags` - Filter by tags (comma-separated)
- `--collection, -c` - Filter by collection ID
- `--page, -p` - Page number
- `--per-page` - Results per page
- `--output, -o` - Save results to file
- `--format, -f` - Output format (table, json, csv, tree, quiet)
- `--verbose, -v` - Show verbose output

---

## Collection Commands

### `pharos collection create`

Create a new collection.

```bash
pharos collection create "ML Papers"
pharos collection create "My Collection" --description "Research papers"
pharos collection create "Public Docs" --public
```

**Options:**
- `--description, -d` - Description for the collection
- `--public` - Make the collection public

### `pharos collection list`

List collections.

```bash
pharos collection list
pharos collection list --query "machine learning"
pharos collection list --page 2 --per-page 50
```

### `pharos collection show`

Show collection details.

```bash
pharos collection show 1
pharos collection show 1 --contents  # Show resources in collection
pharos collection show 1 --contents-limit 20
```

**Options:**
- `--contents, -c` - Show resources in the collection
- `--contents-limit` - Number of resources to show

### `pharos collection add`

Add a resource to a collection.

```bash
pharos collection add 1 5  # Add resource 5 to collection 1
```

### `pharos collection remove`

Remove a resource from a collection.

```bash
pharos collection remove 1 5  # Remove resource 5 from collection 1
```

### `pharos collection update`

Update collection metadata.

```bash
pharos collection update 1 --name "New Name"
pharos collection update 1 --description "New description" --public
```

### `pharos collection delete`

Delete a collection.

```bash
pharos collection delete 1
pharos collection delete 1 --force
```

### `pharos collection export`

Export a collection.

```bash
pharos collection export 1
pharos collection export 1 --format zip --output collection.zip
pharos collection export 1 --format json --output collection.json
```

**Options:**
- `--format, -f` - Export format (json, csv, zip)
- `--output, -o` - Output file path

### `pharos collection stats`

Get statistics for a collection.

```bash
pharos collection stats 1
pharos collection stats 1 --format json
```

---

## Annotation Commands

### `pharos annotate`

Create an annotation on a resource.

```bash
pharos annotate 1 --text "Important note" --start 100 --end 200
```

**Options:**
- `--text, -t` - Annotation text
- `--start, -s` - Start position
- `--end, -e` - End position
- `--type` - Annotation type (highlight, note, tag)

### `pharos annotate list`

List annotations for a resource.

```bash
pharos annotate list 1
```

### `pharos annotate search`

Search annotations.

```bash
pharos annotate search "TODO"
```

### `pharos annotate delete`

Delete an annotation.

```bash
pharos annotate delete 1
```

### `pharos annotate export`

Export annotations for a resource.

```bash
pharos annotate export 1
pharos annotate export 1 --format md
```

### `pharos annotate import`

Import annotations from a file.

```bash
pharos annotate import annotations.json
```

---

## Graph Commands

### `pharos graph stats`

Show graph statistics.

```bash
pharos graph stats
pharos graph stats --format json
```

### `pharos graph citations`

Show citations for a resource.

```bash
pharos graph citations 1
pharos graph citations 1 --format json
```

### `pharos graph related`

Find related resources using graph embeddings.

```bash
pharos graph related 1
pharos graph related 1 --limit 20
pharos graph related 1 --format json
```

**Options:**
- `--limit, -l` - Maximum number of related resources (1-100)

### `pharos graph neighbors`

Get hybrid neighbors for mind-map visualization.

```bash
pharos graph neighbors 1
pharos graph neighbors 1 --limit 15
```

### `pharos graph overview`

Show global overview of strongest connections.

```bash
pharos graph overview
pharos graph overview --limit 100 --threshold 0.8
```

### `pharos graph export`

Export graph data.

```bash
pharos graph export --format graphml -o graph.graphml
pharos graph export --format json
```

**Options:**
- `--format, -f` - Export format (graphml, json, csv)
- `--output, -o` - Output file path

### `pharos graph contradictions`

Show detected contradictions in the knowledge graph.

```bash
pharos graph contradictions
```

### `pharos graph discover`

Discover hypotheses using ABC pattern (Literature-Based Discovery).

```bash
pharos graph discover "machine learning" "drug discovery"
pharos graph discover "AI" "healthcare" --limit 20
pharos graph discover "neural networks" "biology" --start-date 2020-01-01
```

**Options:**
- `--limit, -l` - Maximum hypotheses (1-100)
- `--start-date` - Start date for time-slicing
- `--end-date` - End date for time-slicing

### `pharos graph centrality`

Show centrality scores for nodes.

```bash
pharos graph centrality
pharos graph centrality --top 20
```

### `pharos graph entities`

List entities in the knowledge graph.

```bash
pharos graph entities
pharos graph entities --type Concept
pharos graph entities --name "gradient" --limit 20
```

### `pharos graph traverse`

Traverse the knowledge graph from an entity.

```bash
pharos graph traverse entity-uuid-1
pharos graph traverse entity-uuid-1 --relations EXTENDS,SUPPORTS --hops 3
```

### `pharos graph embeddings`

Generate graph embeddings.

```bash
pharos graph embeddings
pharos graph embeddings --algorithm deepwalk --dimensions 256
```

---

## Quality Commands

### `pharos quality score`

Show quality score for a resource.

```bash
pharos quality score 1
pharos quality score 1 --verbose
```

### `pharos quality outliers`

List quality outliers.

```bash
pharos quality outliers
pharos quality outliers --page 2 --limit 50
pharos quality outliers --min-score 0.5 --format json
```

### `pharos quality recompute`

Recompute quality score for a resource.

```bash
pharos quality recompute 1
pharos quality recompute 1 --async
```

### `pharos quality report`

Generate quality report for a collection.

```bash
pharos quality report 1
pharos quality report 1 --output report.json
```

### `pharos quality distribution`

Show quality score distribution.

```bash
pharos quality distribution
pharos quality distribution --dimension accuracy --bins 20
```

### `pharos quality dimensions`

Show average quality dimensions across all resources.

```bash
pharos quality dimensions
```

### `pharos quality trends`

Show quality trends over time.

```bash
pharos quality trends
pharos quality trends --granularity monthly --start-date 2024-01-01
```

### `pharos quality review-queue`

Show resources needing quality review.

```bash
pharos quality review-queue
pharos quality review-queue --page 2 --sort quality_overall
```

### `pharos quality health`

Check quality module health.

```bash
pharos quality health
```

---

## Taxonomy Commands

### `pharos taxonomy list`

List taxonomy categories.

```bash
pharos taxonomy list
pharos taxonomy list --parent cat-1
pharos taxonomy list --depth 2 --format table
```

### `pharos taxonomy classify`

Classify a resource using the taxonomy.

```bash
pharos taxonomy classify 1
pharos taxonomy classify 1 --force
pharos taxonomy classify 1 --verbose
```

### `pharos taxonomy train`

Train or retrain the taxonomy classification model.

```bash
pharos taxonomy train
pharos taxonomy train --categories cat-1,cat-2,cat-3
pharos taxonomy train --no-wait
```

### `pharos taxonomy stats`

Show taxonomy statistics.

```bash
pharos taxonomy stats
pharos taxonomy stats --format json
```

### `pharos taxonomy category`

Show details for a specific category.

```bash
pharos taxonomy category cat-1
pharos taxonomy category cat-1 --children
pharos taxonomy category cat-1 --similar
```

### `pharos taxonomy search`

Search taxonomy categories.

```bash
pharos taxonomy search "machine learning"
pharos taxonomy search "neural" --limit 10
```

### `pharos taxonomy distribution`

Show classification distribution.

```bash
pharos taxonomy distribution
pharos taxonomy distribution --dimension confidence
```

### `pharos taxonomy model`

Show information about the current classification model.

```bash
pharos taxonomy model
```

### `pharos taxonomy health`

Check taxonomy module health.

```bash
pharos taxonomy health
```

### `pharos taxonomy export`

Export taxonomy data.

```bash
pharos taxonomy export
pharos taxonomy export --format json -o taxonomy.json
```

---

## Recommendation Commands

### `pharos recommend for-user`

Get recommendations for a specific user.

```bash
pharos recommend for-user 1
pharos recommend for-user 1 --limit 20
pharos recommend for-user 1 --explain
pharos recommend for-user 1 --format json --output recommendations.json
```

### `pharos recommend similar`

Find resources similar to the specified resource.

```bash
pharos recommend similar 1
pharos recommend similar 1 --limit 20
pharos recommend similar 1 --explain
```

### `pharos recommend explain`

Get explanation for why a resource is recommended.

```bash
pharos recommend explain 1
pharos recommend explain 1 --user 1
pharos recommend explain 1 --output explanation.md --format markdown
```

### `pharos recommend trending`

Get trending resources.

```bash
pharos recommend trending
pharos recommend trending --limit 20
pharos recommend trending --time-range day
```

### `pharos recommend feed`

Get a personalized feed of recommendations.

```bash
pharos recommend feed 1
pharos recommend feed 1 --limit 50
pharos recommend feed 1 --offset 20
```

---

## Code Analysis Commands

### `pharos code analyze`

Analyze a code file for metrics and quality.

```bash
pharos code analyze ./myfile.py
pharos code analyze ./myfile.py --language python
pharos code analyze ./myfile.py --format json
```

### `pharos code ast`

Extract and display Abstract Syntax Tree from a code file.

```bash
pharos code ast ./myfile.py
pharos code ast ./myfile.py --format text
pharos code ast ./myfile.py -o ast.json
```

### `pharos code deps`

Show dependencies for a code file.

```bash
pharos code deps ./myfile.py
pharos code deps ./myfile.py --transitive
```

### `pharos code chunk`

Chunk a code file for indexing.

```bash
pharos code chunk ./myfile.py
pharos code chunk ./myfile.py --strategy semantic --chunk-size 1000
pharos code chunk ./myfile.py -o chunks.txt
```

### `pharos code scan`

Scan a directory for code files and analyze them.

```bash
pharos code scan ./myproject/
pharos code scan ./myproject/ --no-recursive
pharos code scan ./myproject/ --pattern "*.py" --limit 100
pharos code scan ./myproject/ --format json
```

### `pharos code languages`

List supported programming languages.

```bash
pharos code languages
```

### `pharos code stats`

Show code statistics for a file or directory.

```bash
pharos code stats ./myproject/
pharos code stats ./myfile.py
```

---

## RAG Commands

### `pharos ask`

Ask a question and get an answer from your knowledge base.

```bash
pharos ask "What is gradient descent?"
pharos ask "Explain neural networks" --show-sources
pharos ask "How does authentication work?" --strategy graphrag
pharos ask "Question" --collection 5
pharos ask "Question" --resources 1,2,3
pharos ask "Question" --output answer.md
```

**Options:**
- `--show-sources, -s` - Show source citations
- `--strategy, -t` - Retrieval strategy (hybrid, graphrag, semantic)
- `--collection, -c` - Limit search to a collection
- `--resources, -r` - Comma-separated resource IDs
- `--max-sources, -m` - Maximum sources (1-20)
- `--output, -o` - Save answer to file
- `--format, -f` - Output format (markdown, text, json)

### `pharos ask stream`

Ask a question with streaming response.

```bash
pharos ask stream "What is machine learning?"
pharos ask stream "Explain deep learning" --strategy graphrag
```

### `pharos ask sources`

Find relevant sources for a question.

```bash
pharos ask sources "What is neural networks?"
pharos ask sources "Python tips" --collection 5 --max-sources 10
pharos ask sources "Code review" --format json --output sources.json
```

### `pharos ask strategies`

List available RAG strategies.

```bash
pharos ask strategies
```

### `pharos ask health`

Check RAG service health.

```bash
pharos ask health
```

---

## Chat Command

### `pharos chat`

Start an interactive chat session with your knowledge base.

```bash
pharos chat
pharos chat --strategy graphrag
pharos chat --sources
```

**Interactive Commands:**
- `/help, /h` - Show help
- `/exit, /quit, /q` - Exit the chat
- `/clear, /cls` - Clear the screen
- `/history, /hist` - Show command history
- `/sources on/off` - Toggle source citations
- `/strategy <name>` - Set retrieval strategy
- `/system` - Show current system configuration
- `/reset` - Reset conversation context

---

## Batch Commands

### `pharos batch delete`

Delete multiple resources in batch.

```bash
pharos batch delete "1,2,3"
pharos batch delete "1 2 3" --workers 8
pharos batch delete "1,2,3" --dry-run
pharos batch delete "1,2,3" --force
```

**Options:**
- `--workers, -w` - Number of parallel workers (1-10)
- `--dry-run` - Show what would be deleted
- `--force, -f` - Skip confirmation
- `--format, -f` - Output format (json, table, quiet)

### `pharos batch update`

Update multiple resources from a JSON file.

```bash
pharos batch update updates.json
pharos batch update updates.json --dry-run
pharos batch update updates.json --workers 8
```

**File format:**
```json
{
  "updates": [
    {"id": 1, "title": "New Title", "content": "New content"},
    {"id": 2, "title": "Another Title", "language": "python"}
  ]
}
```

### `pharos batch export`

Export multiple resources to a file or ZIP archive.

```bash
pharos batch export --collection 1
pharos batch export --ids "1,2,3" --format zip
pharos batch export --collection 1 --output ./exports/
pharos batch export --ids "1,2,3" --dry-run
```

**Options:**
- `--collection, -c` - Collection ID to export
- `--ids` - Comma-separated resource IDs
- `--format, -f` - Export format (json, csv, zip, markdown)
- `--output, -o` - Output file or directory path
- `--workers, -w` - Number of parallel workers
- `--dry-run` - Show what would be exported
- `--content-only` - Export only resource content

---

## System Commands

### `pharos health`

Check system health.

```bash
pharos health
pharos health --verbose
pharos health --format json
```

### `pharos stats`

Show system statistics.

```bash
pharos stats
pharos stats --format json
```

### `pharos version`

Show version information.

```bash
pharos version
pharos version --extended
```

### `pharos backup`

Create a database backup.

```bash
pharos backup --output backup.json
pharos backup --output backup.json --verbose
```

### `pharos restore`

Restore database from backup.

```bash
pharos restore backup.json
pharos restore backup.json --force
```

### `pharos verify-backup`

Verify a backup file.

```bash
pharos verify-backup backup.json
```

### `pharos cache clear`

Clear the system cache.

```bash
pharos cache clear
pharos cache clear --force
```

### `pharos migrate`

Run database migrations.

```bash
pharos migrate
pharos migrate --force
```

---

## Backup Commands

### `pharos backup create`

Create a backup of the Pharos database.

```bash
pharos backup create --output ./backup.json
pharos backup create --output ./backup.json --format json
pharos backup create --output ./backup.sql --format sql
pharos backup create --output ./backup.json --no-verify
```

### `pharos backup verify`

Verify a backup file.

```bash
pharos backup verify ./backup.json
pharos backup verify ./backup.json --detailed
```

### `pharos backup restore`

Restore the Pharos database from a backup file.

```bash
pharos backup restore ./backup.json
pharos backup restore ./backup.json --force
pharos backup restore ./backup.json --no-verify
```

### `pharos backup info`

Show information about a backup file.

```bash
pharos backup info ./backup.json
```

---

## Output Formats

All commands support multiple output formats:

| Format | Description | Use Case |
|--------|-------------|----------|
| `table` | Rich table output (default) | Interactive use |
| `json` | JSON output | Scripting, API integration |
| `csv` | CSV output | Spreadsheet import |
| `tree` | Tree output for hierarchical data | Graph, taxonomy visualization |
| `quiet` | IDs only | Piping to other commands |

### Examples

```bash
# Table output (default)
pharos resource list

# JSON for scripting
pharos resource list --format json | jq '.items[].id'

# CSV for Excel
pharos resource list --format csv > resources.csv

# Tree for hierarchy
pharos taxonomy list --format tree

# Quiet for IDs
pharos resource list --format quiet | xargs pharos resource get
```

---

## Shell Completion

Generate shell completion scripts:

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

Override configuration with environment variables:

| Variable | Description |
|----------|-------------|
| `PHAROS_API_URL` | API URL |
| `PHAROS_API_KEY` | API key |
| `PHAROS_PROFILE` | Active profile |
| `PHAROS_OUTPUT_FORMAT` | Default output format |
| `PHAROS_NO_COLOR` | Disable colors (any value) |
| `PHAROS_VERIFY_SSL` | Verify SSL certificates |

---

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Authentication error |
| 4 | Resource not found |
| 5 | Network error |

---

## See Also

- [Installation Guide](installation.md)
- [Configuration Guide](configuration.md)
- [Authentication Guide](authentication.md)
- [Usage Patterns](usage-patterns.md)
- [Workflows](workflows.md)
- [Cheat Sheet](cheat-sheet.md)