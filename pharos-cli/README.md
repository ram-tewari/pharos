# Pharos CLI

Command-line interface for Pharos knowledge management system. Interact with your code intelligence and research management platform directly from the terminal.

## Features

- **Resource Management**: Add, list, update, and delete resources
- **Search**: Keyword, semantic, and hybrid search capabilities
- **Collections**: Organize resources into collections
- **Annotations**: Create and manage highlights and notes
- **Knowledge Graph**: Explore citations, relationships, and discoveries
- **Quality Assessment**: View quality scores and outliers
- **Code Analysis**: Analyze code files and repositories
- **RAG Interface**: Ask questions and chat with your knowledge base
- **System Management**: Health checks, backups, and monitoring

## Installation

### From PyPI (Recommended)

```bash
pip install pharos-cli
```

### Using pipx (Isolated Installation)

```bash
pipx install pharos-cli
```

### From Source

```bash
git clone https://github.com/pharos-project/pharos-cli
cd pharos-cli
pip install -e .
```

### From GitHub

```bash
pip install git+https://github.com/pharos-project/pharos-cli
```

## Quick Start

### 1. Initialize Configuration

```bash
pharos init
```

This will create a configuration file at `~/.pharos/config.yaml` and guide you through the setup process.

### 2. Authenticate

```bash
# Using API key
pharos auth login --api-key YOUR_API_KEY

# Using OAuth2 (interactive)
pharos auth login --oauth
```

### 3. Verify Installation

```bash
pharos --version
pharos health
```

## Usage

### Resource Management

```bash
# Add a file as a resource
pharos resource add ./my_script.py

# Add a resource from URL
pharos resource add --url https://example.com/paper.pdf

# Add from stdin
cat file.py | pharos resource add --stdin

# List resources with filters
pharos resource list --type code --language python

# Get resource details
pharos resource get 123

# Update resource metadata
pharos resource update 123 --title "New Title"

# Delete a resource
pharos resource delete 123

# Batch import from directory
pharos resource import ./papers/ --recursive
```

### Search

```bash
# Keyword search
pharos search "machine learning"

# Semantic search
pharos search "neural networks" --semantic

# Hybrid search with weight
pharos search "AI" --hybrid --weight 0.7

# With filters
pharos search "python" --type code --min-quality 0.8

# Save results to file
pharos search "AI" --output results.json

# Output as JSON
pharos search "query" --format json
```

### Collections

```bash
# Create a collection
pharos collection create "ML Papers"

# List collections
pharos collection list

# Show collection contents
pharos collection show 456

# Add resource to collection
pharos collection add 456 123

# Remove resource from collection
pharos collection remove 456 123

# Export collection
pharos collection export 456 --output ./export/
```

### Annotations

```bash
# Create annotation
pharos annotate 123 --text "Important concept" --start 100 --end 200

# List annotations for a resource
pharos annotate list 123

# Search annotations
pharos annotate search "TODO"

# Export annotations to Markdown
pharos annotate export 123 --format md
```

### Knowledge Graph

```bash
# Show graph statistics
pharos graph stats

# Find citations for a resource
pharos graph citations 123

# Find related resources
pharos graph related 123 --limit 10

# Detect contradictions
pharos graph contradictions

# Show centrality scores
pharos graph centrality --top 20
```

### Quality Assessment

```bash
# Get quality score
pharos quality score 123

# List quality outliers
pharos quality outliers --threshold 0.3

# Recompute quality
pharos quality recompute 123

# Quality report for collection
pharos quality report 456
```

### Code Analysis

```bash
# Analyze a code file
pharos code analyze ./script.py

# Extract AST
pharos code ast ./script.py --format json

# Find dependencies
pharos code deps ./script.py

# Chunk code file
pharos code chunk ./script.py --strategy ast

# Batch scan repository
pharos code scan ./my_repo/ --recursive
```

### RAG & Chat

```bash
# Ask a question
pharos ask "How does authentication work?"

# With evidence sources
pharos ask "What is the architecture?" --show-sources

# Specify retrieval strategy
pharos ask "Explain the design" --strategy graphrag

# Interactive chat mode
pharos chat
```

### System Management

```bash
# Health check
pharos health

# System statistics
pharos stats

# Show version
pharos version

# Database backup
pharos backup --output backup.sql

# Clear cache
pharos cache clear
```

## Configuration

### Config File Location

- Linux/macOS: `~/.pharos/config.yaml` or `~/.config/pharos/config.yaml`
- Windows: `%APPDATA%\pharos\config.yaml`

### Example Config

```yaml
active_profile: default

profiles:
  default:
    api_url: http://localhost:8000
    api_key: null  # Stored securely in keyring
    timeout: 30
    verify_ssl: true

  production:
    api_url: https://pharos.onrender.com
    api_key: null
    timeout: 60
    verify_ssl: true

output:
  format: table
  color: auto
  pager: auto

behavior:
  confirm_destructive: true
  show_progress: true
  parallel_batch: true
  max_workers: 4
```

### Environment Variables

Override config values with environment variables:

```bash
export PHAROS_API_URL="https://pharos.onrender.com"
export PHAROS_API_KEY="sk_live_..."
export PHAROS_PROFILE="production"
export PHAROS_OUTPUT_FORMAT="json"
export PHAROS_NO_COLOR="1"
export PHAROS_VERIFY_SSL="0"
```

### Multiple Profiles

```bash
# Use a specific profile
pharos --profile production resource list

# Show current config
pharos config show
```

## Output Formatting

### Supported Formats

- **table**: Rich table output (default)
- **json**: JSON output
- **tree**: Tree output for hierarchical data
- **csv**: CSV output for spreadsheet compatibility
- **quiet**: IDs only

### Examples

```bash
# Table output (default)
pharos resource list

# JSON output
pharos resource list --format json

# CSV output
pharos search "python" --format csv > results.csv

# Quiet mode (IDs only)
pharos resource list --quiet
```

### Color Control

```bash
# Auto-detect TTY (default)
pharos resource list --color auto

# Always use colors
pharos resource list --color always

# Disable colors
pharos resource list --color never

# Or use NO_COLOR environment variable
NO_COLOR=1 pharos resource list
```

## Shell Completion

Enable shell completion for better UX:

### Bash

```bash
# Add to ~/.bashrc
eval "$(_PHAROS_COMPLETE=bash_source pharos)"
```

### Zsh

```bash
# Add to ~/.zshrc
eval "$(_PHAROS_COMPLETE=zsh_source pharos)"
```

### Fish

```bash
# Add to ~/.config/fish/completions/pharos.fish
_PHAROS_COMPLETE=fish_source pharos | source
```

Or use the installation script:

```bash
./scripts/install_completion.sh
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/pharos-project/pharos-cli
cd pharos-cli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pharos_cli --cov-report=html

# Run specific test file
pytest tests/test_config.py -v

# Run specific test
pytest tests/test_client.py::test_api_client_init -v
```

### Code Quality

```bash
# Format code
black pharos_cli tests

# Lint code
ruff check pharos_cli tests

# Type checking
mypy pharos_cli
```

### Building

```bash
# Build package
pip install build
python -m build

# Publish to PyPI
pip install twine
twine upload dist/*
```

## Documentation

- [Installation Guide](docs/installation.md) - Install Pharos CLI via pip, pipx, or from source
- [Configuration Guide](docs/configuration.md) - Configure profiles, environment variables, and settings
- [Authentication Guide](docs/authentication.md) - Set up API key or OAuth2 authentication
- [Troubleshooting Guide](docs/troubleshooting.md) - Common issues and solutions
- [FAQ](docs/faq.md) - Frequently asked questions
- [Command Reference](docs/commands.md) - Complete command documentation
- [Examples & Tutorials](docs/examples.md) - Common workflows and scripts
- [Development Guide](docs/development.md) - Contributing and development setup

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

See [CONTRIBUTING.md](docs/development.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- [GitHub Issues](https://github.com/pharos-project/pharos-cli/issues)
- [Documentation](https://pharos-cli.readthedocs.io)
- [Pharos Backend Documentation](https://pharos.onrender.com/docs)