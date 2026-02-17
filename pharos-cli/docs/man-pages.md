# Pharos CLI Man Pages

This document provides Unix-style man page references for Pharos CLI commands.

## Table of Contents

- [pharos(1)](#pharos1)
- [pharos-auth-login(1)](#pharos-auth-login1)
- [pharos-auth-logout(1)](#pharos-auth-logout1)
- [pharos-auth-whoami(1)](#pharos-auth-whoami1)
- [pharos-config-init(1)](#pharos-config-init1)
- [pharos-config-show(1)](#pharos-config-show1)
- [pharos-resource-add(1)](#pharos-resource-add1)
- [pharos-resource-list(1)](#pharos-resource-list1)
- [pharos-resource-get(1)](#pharos-resource-get1)
- [pharos-search(1)](#pharos-search1)
- [pharos-collection-create(1)](#pharos-collection-create1)
- [pharos-collection-show(1)](#pharos-collection-show1)
- [pharos-ask(1)](#pharos-ask1)
- [pharos-chat(1)](#pharos-chat1)
- [pharos-health(1)](#pharos-health1)
- [pharos-backup-create(1)](#pharos-backup-create1)
- [pharos-backup-restore(1)](#pharos-backup-restore1)

---

## pharos(1)

### Name

`pharos` - Command-line interface for Pharos knowledge management system

### Synopsis

```
pharos [OPTIONS] COMMAND [ARGS]...
```

### Description

Pharos CLI is a command-line interface for the Pharos knowledge management system. It allows developers and researchers to manage resources, search knowledge bases, analyze code, and interact with knowledge graphs from the terminal.

### Global Options

| Option | Description |
|--------|-------------|
| `--color auto\|always\|never` | Color output mode (default: auto) |
| `--no-color` | Disable color output |
| `--pager auto\|always\|never` | Pager mode (default: auto) |
| `--no-pager` | Disable pager output |
| `--help, -h` | Show help message |
| `--version` | Show version information |

### Commands

| Command | Description |
|---------|-------------|
| `auth` | Authentication commands |
| `config` | Configuration commands |
| `resource` | Resource management |
| `search` | Search resources |
| `collection` | Collection management |
| `annotate` | Annotation management |
| `graph` | Knowledge graph commands |
| `quality` | Quality assessment |
| `taxonomy` | Taxonomy and classification |
| `recommend` | Recommendations |
| `code` | Code analysis |
| `ask` | RAG question answering |
| `chat` | Interactive chat |
| `batch` | Batch operations |
| `system` | System management |
| `backup` | Backup and restore |

### Examples

```bash
# Show help
pharos --help

# Show version
pharos version

# Check health
pharos health

# List resources
pharos resource list
```

### Files

- `~/.pharos/config.yaml` - Configuration file
- `~/.pharos/chat_history.txt` - Chat history

### See Also

`pharos-command(1)` for specific command documentation

---

## pharos-auth-login(1)

### Name

`pharos-auth-login` - Authenticate with the Pharos API

### Synopsis

```
pharos auth login [OPTIONS]
```

### Description

Authenticates the user with the Pharos API using either an API key or OAuth2 interactive flow.

### Options

| Option | Description |
|--------|-------------|
| `--api-key, -k TEXT` | API key for authentication |
| `--url, -u TEXT` | API URL (for first-time setup) |
| `--oauth, -o` | Use OAuth2 interactive login |
| `--provider TEXT` | OAuth2 provider (google, github; default: google) |
| `--help` | Show help message |

### Examples

```bash
# API key authentication
pharos auth login --api-key YOUR_API_KEY

# OAuth2 with Google
pharos auth login --oauth

# OAuth2 with GitHub
pharos auth login --oauth --provider github

# With custom API URL
pharos auth login --api-key KEY --url https://pharos.example.com
```

### See Also

`pharos-auth-logout(1)`, `pharos-auth-whoami(1)`

---

## pharos-auth-logout(1)

### Name

`pharos-auth-logout` - Logout from Pharos and clear credentials

### Synopsis

```
pharos auth logout
```

### Description

Logs out from Pharos by clearing stored credentials from both the configuration file and the system keyring.

### Examples

```bash
pharos auth logout
```

### See Also

`pharos-auth-login(1)`, `pharos-auth-whoami(1)`

---

## pharos-auth-whoami(1)

### Name

`pharos-auth-whoami` - Show current user information

### Synopsis

```
pharos auth whoami
```

### Description

Displays information about the currently authenticated user, including username, email, and user ID.

### Examples

```bash
pharos auth whoami
```

### Output

```
User Information
  Username: johndoe
  Email: john@example.com
  ID: 12345
```

### See Also

`pharos-auth-login(1)`, `pharos-auth-status(1)`

---

## pharos-config-init(1)

### Name

`pharos-config-init` - Initialize Pharos CLI configuration

### Synopsis

```
pharos config init [OPTIONS]
```

### Description

Initializes the Pharos CLI configuration by creating the configuration file and prompting for API settings.

### Options

| Option | Description |
|--------|-------------|
| `--url, -u TEXT` | API URL to use |
| `--api-key, -k TEXT` | API key for authentication |
| `--non-interactive, -n` | Run in non-interactive mode |
| `--help` | Show help message |

### Examples

```bash
# Interactive setup
pharos config init

# Non-interactive with values
pharos config init --url https://pharos.onrender.com --api-key KEY
```

### Files

Creates `~/.pharos/config.yaml`

### See Also

`pharos-config-show(1)`

---

## pharos-config-show(1)

### Name

`pharos-config-show` - Show current configuration

### Synopsis

```
pharos config show [OPTIONS]
```

### Description

Displays the current Pharos CLI configuration, including API settings, output preferences, and behavior settings.

### Options

| Option | Description |
|--------|-------------|
| `--profile, -p TEXT` | Profile to show (default: active profile) |
| `--show-api-key, -s` | Show API key (use with caution) |
| `--format, -f TEXT` | Output format: rich, json, yaml |
| `--help` | Show help message |

### Examples

```bash
# Show active profile
pharos config show

# Show specific profile
pharos config show --profile production

# Show as JSON
pharos config show --format json
```

### See Also

`pharos-config-init(1)`

---

## pharos-resource-add(1)

### Name

`pharos-resource-add` - Add a new resource

### Synopsis

```
pharos resource add [OPTIONS] [FILE]
```

### Description

Adds a new resource to the knowledge base from a file, URL, or stdin.

### Arguments

| Argument | Description |
|----------|-------------|
| `FILE` | File path to add as a resource |

### Options

| Option | Description |
|--------|-------------|
| `--url, -u TEXT` | URL to add as a resource |
| `--title, -t TEXT` | Title for the resource |
| `--type, -T TEXT` | Resource type (code, paper, documentation, etc.) |
| `--language, -l TEXT` | Programming language or natural language |
| `--stdin, -s` | readFile content from stdin |
| `--content, -c TEXT` | Content directly |
| `--help` | Show help message |

### Examples

```bash
# Add from file
pharos resource add ./myfile.py

# Add from URL
pharos resource add --url https://example.com/paper.pdf --type paper

# Add from stdin
cat file.txt | pharos resource add --stdin --title "My Note"

# Add with type and language
pharos resource add ./script.py --type code --language python
```

### See Also

`pharos-resource-list(1)`, `pharos-resource-get(1)`

---

## pharos-resource-list(1)

### Name

`pharos-resource-list` - List resources

### Synopsis

```
pharos resource list [OPTIONS]
```

### Description

Lists resources in the knowledge base with optional filtering and pagination.

### Options

| Option | Description |
|--------|-------------|
| `--type, -T TEXT` | Filter by resource type |
| `--language, -l TEXT` | Filter by programming language |
| `--query, -q TEXT` | Search query for title/content |
| `--min-quality FLOAT` | Minimum quality score (0.0-1.0) |
| `--collection, -c INTEGER` | Filter by collection ID |
| `--tags TEXT` | Filter by tags (comma-separated) |
| `--page, -p INTEGER` | Page number (default: 1) |
| `--per-page INTEGER` | Items per page (1-100, default: 25) |
| `--format, -f TEXT` | Output format: json, table, csv, quiet |
| `--help` | Show help message |

### Examples

```bash
# List all resources
pharos resource list

# Filter by type and language
pharos resource list --type code --language python

# Search with filters
pharos resource list --query "machine learning" --min-quality 0.8

# Pagination
pharos resource list --page 2 --per-page 50

# JSON output
pharos resource list --format json
```

### See Also

`pharos-resource-add(1)`, `pharos-resource-get(1)`

---

## pharos-resource-get(1)

### Name

`pharos-resource-get` - Get resource details

### Synopsis

```
pharos resource get RESOURCE_ID [OPTIONS]
```

### Description

Retrieves detailed information about a specific resource.

### Arguments

| Argument | Description |
|----------|-------------|
| `RESOURCE_ID` | Resource ID to retrieve |

### Options

| Option | Description |
|--------|-------------|
| `--format, -f TEXT` | Output format: json, table, tree |
| `--content` | Show resource content |
| `--content-lines INTEGER` | Number of content lines to show |
| `--help` | Show help message |

### Examples

```bash
# Get resource details
pharos resource get 1

# Get with content
pharos resource get 1 --content

# JSON output
pharos resource get 1 --format json
```

### See Also

`pharos-resource-list(1)`, `pharos-resource-update(1)`

---

## pharos-search(1)

### Name

`pharos-search` - Search for resources

### Synopsis

```
pharos search QUERY [OPTIONS]
```

### Description

Searches for resources in the knowledge base using keyword, semantic, or hybrid search.

### Arguments

| Argument | Description |
|----------|-------------|
| `QUERY` | Search query |

### Options

| Option | Description |
|--------|-------------|
| `--semantic, -s` | Use semantic search |
| `--hybrid, -h` | Use hybrid search |
| `--weight, -w FLOAT` | Weight for hybrid search (0.0-1.0) |
| `--type, -t TEXT` | Filter by resource type |
| `--language, -l TEXT` | Filter by language |
| `--min-quality, -q FLOAT` | Minimum quality score |
| `--max-quality FLOAT` | Maximum quality score |
| `--tags TEXT` | Filter by tags (comma-separated) |
| `--collection, -c INTEGER` | Filter by collection ID |
| `--page, -p INTEGER` | Page number |
| `--per-page INTEGER` | Results per page |
| `--output, -o PATH` | Save results to file |
| `--format, -f TEXT` | Output format: table, json, csv, tree, quiet |
| `--verbose, -v` | Show verbose output |
| `--help` | Show help message |

### Examples

```bash
# Basic search
pharos search "machine learning"

# Semantic search
pharos search "neural networks" --semantic

# Hybrid search
pharos search "AI" --hybrid --weight 0.7

# With filters
pharos search "python" --type code --language python --min-quality 0.8

# Save results
pharos search "machine learning" --output results.json
```

### See Also

`pharos-resource-list(1)`, `pharos-ask(1)`

---

## pharos-collection-create(1)

### Name

`pharos-collection-create` - Create a new collection

### Synopsis

```
pharos collection create NAME [OPTIONS]
```

### Description

Creates a new collection for organizing resources.

### Arguments

| Argument | Description |
|----------|-------------|
| `NAME` | Name for the new collection |

### Options

| Option | Description |
|--------|-------------|
| `--description, -d TEXT` | Description for the collection |
| `--public` | Make the collection public |
| `--format, -f TEXT` | Output format: json, table |
| `--help` | Show help message |

### Examples

```bash
# Create collection
pharos collection create "ML Papers"

# With description
pharos collection create "Research" --description "Academic papers"

# Public collection
pharos collection create "Public Docs" --public
```

### See Also

`pharos-collection-show(1)`, `pharos-collection-list(1)`

---

## pharos-collection-show(1)

### Name

`pharos-collection-show` - Show collection details

### Synopsis

```
pharos collection show COLLECTION_ID [OPTIONS]
```

### Description

Displays detailed information about a collection, including its resources.

### Arguments

| Argument | Description |
|----------|-------------|
| `COLLECTION_ID` | Collection ID to show |

### Options

| Option | Description |
|--------|-------------|
| `--format, -f TEXT` | Output format: json, table, tree |
| `--contents, -c` | Show resources in the collection |
| `--contents-limit INTEGER` | Number of resources to show |
| `--help` | Show help message |

### Examples

```bash
# Show collection details
pharos collection show 1

# Show with contents
pharos collection show 1 --contents

# Limit contents
pharos collection show 1 --contents --contents-limit 20
```

### See Also

`pharos-collection-create(1)`, `pharos-collection-list(1)`

---

## pharos-ask(1)

### Name

`pharos-ask` - Ask a question using RAG

### Synopsis

```
pharos ask QUESTION [OPTIONS]
```

### Description

Asks a question and gets an answer from the knowledge base using Retrieval-Augmented Generation (RAG).

### Arguments

| Argument | Description |
|----------|-------------|
| `QUESTION` | The question to ask |

### Options

| Option | Description |
|--------|-------------|
| `--show-sources, -s` | Show source citations |
| `--strategy, -t TEXT` | Retrieval strategy: hybrid, graphrag, semantic |
| `--collection, -c INTEGER` | Limit search to a collection |
| `--resources, -r TEXT` | Comma-separated resource IDs |
| `--max-sources, -m INTEGER` | Maximum sources (1-20, default: 5) |
| `--output, -o PATH` | Save answer to file |
| `--format, -f TEXT` | Output format: markdown, text, json |
| `--help` | Show help message |

### Examples

```bash
# Ask a question
pharos ask "What is machine learning?"

# With sources
pharos ask "Explain neural networks" --show-sources

# Using graphrag strategy
pharos ask "How does attention work?" --strategy graphrag

# Limit to collection
pharos ask "Summarize these papers" --collection 1

# Save answer
pharos ask "Explain transformers" --output answer.md
```

### See Also

`pharos-search(1)`, `pharos-chat(1)`

---

## pharos-chat(1)

### Name

`pharos-chat` - Interactive chat session

### Synopsis

```
pharos chat [OPTIONS]
```

### Description

Starts an interactive chat session with the knowledge base. Supports multi-line input, command history, and various chat commands.

### Options

| Option | Description |
|--------|-------------|
| `--strategy, -s TEXT` | Retrieval strategy: hybrid, graphrag, semantic |
| `--sources, -S` | Show source citations for answers |
| `--help` | Show help message |

### Chat Commands

| Command | Description |
|---------|-------------|
| `/help, /h` | Show help message |
| `/exit, /quit, /q` | Exit the chat |
| `/clear, /cls` | Clear the screen |
| `/history, /hist` | Show command history |
| `/sources on/off` | Toggle source citations |
| `/strategy <name>` | Set retrieval strategy |
| `/system` | Show current configuration |
| `/reset` | Reset conversation context |

### Examples

```bash
# Start chat
pharos chat

# With graphrag strategy
pharos chat --strategy graphrag

# With sources enabled
pharos chat --sources
```

### Interactive Example

```
$ pharos chat
Welcome to Pharos Chat!

You: How does authentication work?
[Answer displayed]

You: /sources on
Sources enabled.

You: What about authorization?
[Answer with sources]

You: /exit
Goodbye!
```

### See Also

`pharos-ask(1)`

---

## pharos-health(1)

### Name

`pharos-health` - Check system health

### Synopsis

```
pharos health [OPTIONS]
```

### Description

Checks the health of the Pharos backend and its components.

### Options

| Option | Description |
|--------|-------------|
| `--verbose, -v` | Show detailed health information |
| `--format, -f TEXT` | Output format: panel, json, table |
| `--help` | Show help message |

### Examples

```bash
# Basic health check
pharos health

# Verbose output
pharos health --verbose

# JSON output
pharos health --format json
```

### Output

```
System Health
Status: healthy
```

### See Also

`pharos-stats(1)`, `pharos-version(1)`

---

## pharos-backup-create(1)

### Name

`pharos-backup-create` - Create a database backup

### Synopsis

```
pharos backup create --output OUTPUT [OPTIONS]
```

### Description

Creates a backup of the Pharos database.

### Options

| Option | Description |
|--------|-------------|
| `--output, -o PATH` | Output file path for the backup |
| `--format, -f TEXT` | Backup format: json, sql |
| `--verify/--no-verify` | Verify the backup after creation |
| `--help` | Show help message |

### Examples

```bash
# Create backup
pharos backup create --output backup.json

# SQL format
pharos backup create --output backup.sql --format sql

# Skip verification
pharos backup create --output backup.json --no-verify
```

### See Also

`pharos-backup-restore(1)`, `pharos-backup-verify(1)`

---

## pharos-backup-restore(1)

### Name

`pharos-backup-restore` - Restore database from backup

### Synopsis

```
pharos backup restore BACKUP_FILE [OPTIONS]
```

### Description

Restores the Pharos database from a backup file.

### Arguments

| Argument | Description |
|----------|-------------|
| `BACKUP_FILE` | Path to the backup file |

### Options

| Option | Description |
|--------|-------------|
| `--force, -f` | Skip confirmation prompt |
| `--verify/--no-verify` | Verify backup before restoring |
| `--help` | Show help message |

### Examples

```bash
# Restore backup
pharos restore backup.json

# Force restore (skip confirmation)
pharos restore backup.json --force

# Skip verification
pharos restore backup.json --no-verify
```

### Warning

This will overwrite all existing data. Use with caution.

### See Also

`pharos-backup-create(1)`, `pharos-backup-verify(1)`

---

## Generating Man Pages

To generate proper man pages for your system, use the following commands:

```bash
# Generate man page for pharos
pharos --man > pharos.1

# Generate man page for a specific command
pharos resource add --man > pharos-resource-add.1

# Install man pages
sudo cp pharos*.1 /usr/share/man/man1/
sudo gzip /usr/share/man/man1/pharos*.1
```

### Man Page Sections

| Section | Content |
|---------|---------|
| NAME | Command name and brief description |
| SYNOPSIS | Command syntax |
| DESCRIPTION | Detailed description |
| OPTIONS | Command-line options |
| ARGUMENTS | Positional arguments |
| EXAMPLES | Usage examples |
| FILES | Related files |
| SEE ALSO | Related commands |
| AUTHOR | Author information |
| BUGS | Known bugs |

---

## See Also

- [Command Reference](command-reference.md)
- [Usage Patterns](usage-patterns.md)
- [Workflows](workflows.md)
- [Cheat Sheet](cheat-sheet.md)