# Frequently Asked Questions

This document answers common questions about Pharos CLI.

## Table of Contents

- [General Questions](#general-questions)
- [Installation](#installation)
- [Configuration](#configuration)
- [Authentication](#authentication)
- [Usage](#usage)
- [Output and Formatting](#output-and-formatting)
- [Performance](#performance)
- [Integrations](#integrations)
- [Troubleshooting](#troubleshooting)

---

## General Questions

### What is Pharos CLI?

Pharos CLI is a command-line interface for the Pharos knowledge management system. It allows you to interact with your code intelligence and research management platform directly from the terminal, enabling scripting, automation, and power-user workflows.

### What can I do with Pharos CLI?

- **Resource Management:** Add, list, update, and delete resources (code files, papers, documents)
- **Search:** Keyword, semantic, and hybrid search across your knowledge base
- **Collections:** Organize resources into collections
- **Annotations:** Create and manage highlights and notes
- **Knowledge Graph:** Explore citations, relationships, and discoveries
- **Quality Assessment:** View quality scores and outliers
- **Code Analysis:** Analyze code files and repositories
- **RAG Interface:** Ask questions and chat with your knowledge base
- **System Management:** Health checks, backups, and monitoring

### Is Pharos CLI free?

Yes, Pharos CLI is open-source and free to use. However, it connects to a Pharos backend API which may have its own pricing model depending on your deployment.

### What operating systems are supported?

- **macOS:** 10.15 (Catalina) and higher
- **Linux:** Ubuntu 20.04+, Fedora 35+, Debian 11+
- **Windows:** Windows 10 and Windows 11

Python 3.8 or higher is required on all platforms.

---

## Installation

### How do I install Pharos CLI?

**Using pip (recommended):**
```bash
pip install pharos-cli
```

**Using pipx (isolated installation):**
```bash
pipx install pharos-cli
```

**From source:**
```bash
git clone https://github.com/pharos-project/pharos-cli
cd pharos-cli
pip install -e .
```

See the [Installation Guide](installation.md) for detailed instructions.

### Do I need to install Python?

Yes, Pharos CLI requires Python 3.8 or higher. If you don't have Python installed:

- **macOS:** `brew install python@3.11`
- **Ubuntu/Debian:** `sudo apt install python3 python3-pip`
- **Windows:** Download from [python.org](https://www.python.org/downloads/)

### What's the difference between pip and pipx?

- **pip** installs packages globally or in your user site-packages
- **pipx** creates an isolated virtual environment for each CLI tool

We recommend **pipx** for CLI tools to avoid conflicts with other Python packages.

### Can I install from a specific version?

```bash
# Install specific version
pip install pharos-cli==0.1.0

# Install from specific branch
pip install git+https://github.com/pharos-project/pharos-cli.git@main

# Install from specific tag
pip install git+https://github.com/pharos-project/pharos-cli.git@v0.1.0
```

### How do I upgrade Pharos CLI?

```bash
# Using pip
pip install --upgrade pharos-cli

# Using pipx
pipx upgrade pharos-cli
```

### How do I uninstall Pharos CLI?

```bash
# Using pip
pip uninstall pharos-cli

# Using pipx
pipx uninstall pharos-cli

# Clean up configuration
rm -rf ~/.pharos/
```

---

## Configuration

### Where is the configuration file?

| Platform | Location |
|----------|----------|
| Linux | `~/.pharos/config.yaml` or `~/.config/pharos/config.yaml` |
| macOS | `~/.pharos/config.yaml` or `~/Library/Application Support/pharos/config.yaml` |
| Windows | `%APPDATA%\pharos\config.yaml` |

### How do I create a configuration?

Run the interactive setup:
```bash
pharos init
```

Or create the file manually:
```bash
mkdir -p ~/.pharos
touch ~/.pharos/config.yaml
```

See the [Configuration Guide](configuration.md) for details.

### Can I use multiple profiles?

Yes! Create multiple profiles in your config file:

```yaml
active_profile: development

profiles:
  development:
    api_url: http://localhost:8000
    api_key: null
    
  production:
    api_url: https://pharos.onrender.com
    api_key: null
```

Switch profiles with:
```bash
pharos --profile production resource list
```

### How do environment variables work?

Environment variables override config file settings:

```bash
export PHAROS_API_URL="https://pharos.example.com"
export PHAROS_API_KEY="your-key"
export PHAROS_OUTPUT_FORMAT="json"
```

See the [Configuration Guide](configuration.md#environment-variables) for all available variables.

### Can I have project-specific settings?

Yes! Create a `.pharos.yaml` file in your project root:

```yaml
api_url: https://pharos.company.com
output:
  format: json
```

This overrides user settings when run from that directory.

---

## Authentication

### How do I authenticate?

**Using API key:**
```bash
pharos auth login --api-key YOUR_API_KEY
```

**Using OAuth2 (interactive):**
```bash
pharos auth login --oauth
```

See the [Authentication Guide](authentication.md) for details.

### Where do I get an API key?

1. Log in to your Pharos instance (e.g., https://pharos.onrender.com)
2. Navigate to Settings → API
3. Generate a new API key
4. Copy the key (shown only once)

### How do I check if I'm authenticated?

```bash
pharos auth whoami
```

Output:
```
Logged in as: your@email.com
User ID: 12345
Plan: premium
```

### How do I switch accounts?

```bash
# Log out current account
pharos auth logout

# Log in with different credentials
pharos auth login --api-key DIFFERENT_KEY
```

Or use profiles for multiple accounts:
```bash
pharos --profile personal auth login --api-key PERSONAL_KEY
pharos --profile work auth login --api-key WORK_KEY
```

### How do credentials get stored?

Credentials are stored securely using your system's keyring:

- **macOS:** Keychain
- **Windows:** Credential Manager
- **Linux:** Secret Service (GNOME Keyring) or pass

### What if keyring is not available?

```bash
# Install with all backends
pip install keyring[all]

# Or use environment variable fallback
export PHAROS_API_KEY="your-key"
```

### How do I log out?

```bash
pharos auth logout

# Log out from all devices
pharos auth logout --all-devices
```

---

## Usage

### How do I add a resource?

```bash
# From a file
pharos resource add ./my_script.py

# From a URL
pharos resource add --url https://example.com/paper.pdf

# From stdin
cat file.py | pharos resource add --stdin
```

### How do I search?

```bash
# Keyword search
pharos search "machine learning"

# Semantic search
pharos search "neural networks" --semantic

# Hybrid search
pharos search "AI" --hybrid --weight 0.7

# With filters
pharos search "python" --type code --min-quality 0.8
```

### How do I export results?

```bash
# Save search results to JSON
pharos search "query" --output results.json

# Export collection
pharos collection export 123 --output ./export/

# Export resource
pharos resource export 123 --output file.pdf
```

### How do I batch import files?

```bash
# Import all files in directory
pharos resource import ./papers/

# Recursively import
pharos resource import ./papers/ --recursive

# With progress bar
pharos resource import ./papers/ --verbose
```

### How do I use shell completion?

**Bash:**
```bash
# Add to ~/.bashrc
eval "$(_PHAROS_COMPLETE=bash_source pharos)"
```

**Zsh:**
```bash
# Add to ~/.zshrc
eval "$(_PHAROS_COMPLETE=zsh_source pharos)"
```

**Fish:**
```bash
# Add to ~/.config/fish/completions/pharos.fish
_PHAROS_COMPLETE=fish_source pharos | source
```

### How do I run commands in CI/CD?

```bash
# Set environment variables
export PHAROS_API_URL="https://pharos.onrender.com"
export PHAROS_API_KEY="$PHAROS_API_KEY"
export PHAROS_OUTPUT_FORMAT="json"

# Run commands
pharos resource list
pharos search "security" --format json > results.json
```

See the [Authentication Guide](authentication.md#cicd-authentication) for CI/CD examples.

---

## Output and Formatting

### What output formats are supported?

| Format | Description | Use Case |
|--------|-------------|----------|
| `table` | Rich table output (default) | Interactive use |
| `json` | JSON output | Scripting, APIs |
| `tree` | Tree structure | Hierarchical data |
| `csv` | CSV format | Spreadsheets |
| `quiet` | IDs only | Piping to other commands |

```bash
pharos resource list --format json
pharos resource list --format csv > results.csv
pharos resource list --quiet
```

### How do I control colors?

```bash
# Auto-detect TTY (default)
pharos resource list --color auto

# Always use colors
pharos resource list --color always

# Disable colors
pharos resource list --color never

# Or use NO_COLOR
NO_COLOR=1 pharos resource list
```

### How do I disable the pager?

```bash
# Disable for single command
pharos resource list --pager never

# Or set environment variable
export PHAROS_PAGER=never
```

### How do I save output to a file?

```bash
# Use --output flag
pharos search "query" --output results.json

# Or redirect stdout
pharos resource list --format json > results.json
```

---

## Performance

### Why are commands slow?

Common causes:

1. **Network latency** - Check with `curl https://pharos.onrender.com/health`
2. **Large result sets** - Use pagination: `--page 1 --per-page 25`
3. **Verbose output** - Use `--quiet` or `--format json`
4. **High server load** - Try during off-peak hours

### How do I improve performance?

```bash
# Use pagination
pharos resource list --page 1 --per-page 25

# Use quiet mode
pharos resource list --quiet

# Reduce batch size
pharos resource import ./files/ --batch-size 50

# Limit parallel workers
pharos resource import ./files/ --max-workers 2
```

### What's the expected response time?

| Operation | Expected Time |
|-----------|---------------|
| Simple command (version, help) | < 100ms |
| Resource list (10 items) | < 500ms |
| Search query | < 1s |
| Resource import (batch) | Varies |

---

## Integrations

### Can I use Pharos CLI in Docker?

```dockerfile
FROM python:3.11-slim
RUN pip install pharos-cli
ENV PHAROS_API_URL=https://pharos.onrender.com
ENV PHAROS_API_KEY=${PHAROS_API_KEY}
CMD ["pharos", "resource", "list"]
```

```bash
docker run -e PHAROS_API_KEY="your-key" pharos-cli pharos resource list
```

### Can I use Pharos CLI in GitHub Actions?

```yaml
- name: Install Pharos CLI
  run: pip install pharos-cli

- name: Authenticate
  run: echo "${{ secrets.PHAROS_API_KEY }}" | pharos auth login --api-key
  env:
    PHAROS_API_KEY: ${{ secrets.PHAROS_API_KEY }}

- name: Run Pharos
  run: pharos resource list
```

### Can I use Pharos CLI with cron jobs?

```bash
# Edit crontab
crontab -e

# Add job
0 */4 * * * PHAROS_API_KEY="your-key" pharos resource list --format json >> /var/log/pharos.log 2>&1
```

### Can I pipe output to other tools?

```bash
# Search and filter
pharos resource list --quiet | grep -i python

# Count resources
pharos resource list --quiet | wc -l

# Process JSON
pharos search "machine learning" --format json | jq '.results[].title'
```

---

## Troubleshooting

### "command not found" after installation

```bash
# Check installation
pip show pharos-cli

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc  # or ~/.zshrc
```

### Authentication keeps failing

```bash
# Verify API key
echo $PHAROS_API_KEY

# Re-authenticate
pharos auth logout
pharos auth login --api-key YOUR_KEY

# Check config
pharos config show
```

### Connection refused errors

```bash
# Check API URL
pharos config show

# Test connectivity
curl https://pharos.onrender.com/health

# Check for proxy
env | grep proxy
```

### Configuration not being applied

```bash
# Validate config
pharos config validate

# Check effective config
pharos config show --verbose

# Reset to defaults
pharos init --force
```

See the [Troubleshooting Guide](troubleshooting.md) for more solutions.

---

## Getting More Help

### Where can I find documentation?

- **This documentation:** [docs/](.)
- **README:** [README.md](../README.md)
- **API Docs:** [pharos.onrender.com/docs](https://pharos.onrender.com/docs)
- **GitHub:** [github.com/pharos-project/pharos-cli](https://github.com/pharos-project/pharos-cli)

### How do I report a bug?

1. Check if the issue is already reported: [GitHub Issues](https://github.com/pharos-project/pharos-cli/issues)
2. Create a new issue with:
   - Error message (full output)
   - Command that failed
   - `pharos --version` output
   - Steps to reproduce

### How do I suggest a feature?

1. Check existing feature requests: [GitHub Discussions](https://github.com/pharos-project/pharos-cli/discussions)
2. Create a new discussion with your suggestion
3. Provide use cases and examples

### Can I contribute to Pharos CLI?

Yes! See [CONTRIBUTING.md](development.md) for:
- Setting up development environment
- Code style and conventions
- Testing requirements
- Pull request process