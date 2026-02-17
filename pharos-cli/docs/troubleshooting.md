# Troubleshooting Guide

This guide covers common issues and their solutions when using Pharos CLI.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Authentication Issues](#authentication-issues)
- [Configuration Issues](#configuration-issues)
- [Connection Issues](#connection-issues)
- [Command Execution Issues](#command-execution-issues)
- [Output and Display Issues](#output-and-display-issues)
- [Performance Issues](#performance-issues)
- [Getting Help](#getting-help)

---

## Installation Issues

### "pharos: command not found"

**Symptoms:**
- Running `pharos` in terminal returns "command not found"
- The command is not recognized

**Causes:**
1. Installation directory not in PATH
2. Installation failed silently
3. Shell needs to be restarted

**Solutions:**

```bash
# Check if pharos is installed
pip show pharos-cli

# Find installation location
pip show -f pharos-cli | grep location

# Check if it's in PATH
echo $PATH | tr ':' '\n' | xargs -I {} sh -c 'ls {} 2>/dev/null | grep pharos'

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc  # or source ~/.zshrc
```

**For pipx:**
```bash
# Ensure pipx is configured
pipx ensurepath

# Check pipx installation
pipx list
```

### Permission Denied Errors

**Symptoms:**
- "Permission denied" during pip install
- Cannot write to installation directory

**Solutions:**

```bash
# Use --user flag
pip install --user pharos-cli

# Or use pipx (recommended)
pipx install pharos-cli

# For system-wide install (not recommended)
sudo pip install pharos-cli
```

### Python Version Error

**Symptoms:**
- "Python 3.8 or higher required"
- Syntax errors during installation

**Solutions:**

```bash
# Check Python version
python --version
python3 --version

# Install Python 3.11 (macOS)
brew install python@3.11

# Install Python 3.11 (Ubuntu/Debian)
sudo apt install python3.11 python3.11-venv python3.11-dev

# Use specific Python version
python3.11 -m pip install pharos-cli
```

### SSL/TLS Certificate Errors

**Symptoms:**
- "SSL certificate verify failed"
- Cannot download packages

**Solutions:**

```bash
# Update certificates (macOS)
/Applications/Python\ 3.x/Install\ Certificates.command

# Update certificates (Linux)
sudo apt update
sudo apt install ca-certificates
sudo update-ca-certificates

# Temporarily disable verification (not recommended)
pip install --trusted-host pypi.org --trusted-host files.pythonhost.org pharos-cli
```

---

## Authentication Issues

### "Authentication Failed" / Invalid API Key

**Symptoms:**
- "401 Unauthorized" error
- "Invalid API key" message

**Solutions:**

```bash
# Verify API key is correct
echo $PHAROS_API_KEY

# Re-authenticate
pharos auth logout
pharos auth login --api-key YOUR_API_KEY

# Check API key in keyring
pharos auth status

# Verify API URL is correct
pharos config show
```

### Token Expired Errors

**Symptoms:**
- "401 Token expired"
- Need to re-authenticate frequently

**Solutions:**

```bash
# Refresh token manually
pharos auth refresh

# If refresh fails, re-authenticate
pharos auth logout
pharos auth login

# Check token status
pharos auth whoami --verbose
```

### Keyring Errors

**Symptoms:**
- "Keyring not available"
- "Failed to store credentials"
- Credentials not persisted

**Solutions:**

```bash
# Install keyring with all backends
pip install keyring[all]

# Check keyring status
python -c "import keyring; print(keyring.get_keyring())"

# Use environment variable fallback
export PHAROS_API_KEY="your-api-key"

# For Linux without GUI, use pass backend
sudo apt install pass
pip install keyring-pass
export PHAROS_KEYRING_BACKEND=keyring_pass.PassBackend
```

### OAuth2 Browser Issues

**Symptoms:**
- Browser doesn't open
- Callback URL not working
- Authorization code not received

**Solutions:**

```bash
# Use manual mode
pharos auth login --oauth --no-browser

# Or use API key instead
pharos auth login --api-key YOUR_KEY

# Check browser settings
echo $BROWSER
```

---

## Configuration Issues

### Config File Not Found

**Symptoms:**
- "Configuration file not found"
- Default settings used instead

**Solutions:**

```bash
# Initialize configuration
pharos init

# Check config location
pharos config show --path

# Create config manually
mkdir -p ~/.pharos
touch ~/.pharos/config.yaml
```

### Invalid Configuration

**Symptoms:**
- "Invalid configuration"
- "YAML parse error"
- Settings not applied

**Solutions:**

```bash
# Validate configuration
pharos config validate

# Check for YAML syntax errors
python -c "import yaml; yaml.safe_load(open('~/.pharos/config.yaml'))"

# Reset to defaults
pharos init --force
```

### Profile Not Found

**Symptoms:**
- "Profile not found: X"
- Wrong profile used

**Solutions:**

```bash
# List available profiles
pharos config show --section profiles

# Switch to existing profile
pharos --profile default resource list

# Create missing profile
pharos init --profile newprofile
```

### Environment Variables Not Working

**Symptoms:**
- Environment variables ignored
- Settings from config file used instead

**Solutions:**

```bash
# Check if variables are set
echo $PHAROS_API_URL
echo $PHAROS_API_KEY

# Export variables
export PHAROS_API_URL="https://pharos.example.com"
export PHAROS_API_KEY="your-key"

# Verify in current shell
env | grep PHAROS

# Use in single command
PHAROS_API_KEY="key" pharos resource list
```

---

## Connection Issues

### "Connection Refused" / Network Error

**Symptoms:**
- "Connection refused"
- "Network is unreachable"
- Timeout errors

**Solutions:**

```bash
# Test API endpoint
curl -v https://pharos.onrender.com/health

# Check API URL in config
pharos config show

# Test with verbose output
pharos --verbose health

# Check for proxy settings
env | grep -i proxy
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
```

### SSL/TLS Verification Errors

**Symptoms:**
- "SSL certificate verify failed"
- "certificate has expired"

**Solutions:**

```bash
# Check system date (expired certs can be a date issue)
date

# Temporarily disable verification (not recommended for production)
export PHAROS_VERIFY_SSL=0
pharos health

# Update CA certificates
sudo apt update && sudo apt install ca-certificates
```

### Timeout Errors

**Symptoms:**
- "Connection timed out"
- Commands hang then fail

**Solutions:**

```bash
# Increase timeout in config
pharos config set profiles.default.timeout 120

# Or use environment variable
export PHAROS_TIMEOUT=120

# Check network speed
curl -w "\nTime: %{time_total}s\n" https://pharos.onrender.com/health

# Try during off-peak hours
```

### DNS Resolution Errors

**Symptoms:**
- "Name or service not known"
- "Could not resolve host"

**Solutions:**

```bash
# Check DNS resolution
nslookup pharos.onrender.com
dig pharos.onrender.com

# Try IP address directly
curl https://[IP_ADDRESS]/health

# Flush DNS cache
# macOS:
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder

# Linux:
sudo systemd-resolve --flush-caches

# Windows:
ipconfig /flushdns
```

---

## Command Execution Issues

### "Invalid Command" / Unknown Command

**Symptoms:**
- "No such command: X"
- Command not recognized

**Solutions:**

```bash
# List all available commands
pharos --help

# Check command spelling
pharos resource --help

# Update to latest version
pip install --upgrade pharos-cli
```

### Argument/Option Errors

**Symptoms:**
- "Missing argument"
- "Invalid value for X"
- Unexpected behavior

**Solutions:**

```bash
# Check command help
pharos resource add --help

# Verify argument types
pharos resource get 123  # ID should be integer

# Use quotes for complex arguments
pharos search "machine learning with neural networks"

# Check for typos in option names
pharos search --type code  # not --typename
```

### Resource Not Found

**Symptoms:**
- "Resource not found: X"
- Empty results when resource exists

**Solutions:**

```bash
# List resources to find correct ID
pharos resource list

# Search for resource
pharos search "resource title"

# Check resource ID format
pharos resource get 123  # Numeric ID

# Verify you have access
pharos auth whoami
```

### Batch Operation Failures

**Symptoms:**
- Partial failures in batch operations
- "Some items failed"

**Solutions:**

```bash
# Run with verbose output
pharos resource import ./files/ --recursive --verbose

# Check log file
cat pharos_import.log

# Run with continue-on-error
pharos resource import ./files/ --continue-on-error

# Reduce batch size
pharos resource import ./files/ --batch-size 50
```

---

## Output and Display Issues

### No Color Output

**Symptoms:**
- Output is monochrome
- Tables not formatted correctly

**Solutions:**

```bash
# Force color output
pharos resource list --color always

# Check terminal type
echo $TERM

# Enable color in terminal
export TERM=xterm-256color

# Check NO_COLOR variable
echo $NO_COLOR
unset NO_COLOR
```

### Table Formatting Issues

**Symptoms:**
- Tables are broken/misaligned
- Columns wrap incorrectly

**Solutions:**

```bash
# Use JSON output for precise data
pharos resource list --format json

# Adjust terminal width
export COLUMNS=120
pharos resource list

# Use compact table format
pharos resource list --format table --compact
```

### Pager Issues

**Symptoms:**
- Output stuck in pager
- Cannot exit less/more

**Solutions:**

```bash
# Disable pager
pharos resource list --pager never

# Or set environment variable
export PHAROS_PAGER=never

# Exit pager: press 'q'
```

### JSON Output Not Valid

**Symptoms:**
- JSON parse errors
- Incomplete JSON output

**Solutions:**

```bash
# Use quiet mode for IDs only
pharos resource list --quiet

# Check for errors in output
pharos resource list --format json 2>&1 | head -100

# Disable progress bars
export PHAROS_SHOW_PROGRESS=0
```

---

## Performance Issues

### Slow Command Execution

**Symptoms:**
- Commands take >5 seconds
- High CPU usage during commands

**Solutions:**

```bash
# Check network latency
curl -w "\nTime: %{time_total}s\n" https://pharos.onrender.com/health

# Reduce output verbosity
pharos resource list --quiet

# Use pagination
pharos resource list --page 1 --per-page 25

# Check for parallel processing
pharos resource import ./files/ --parallel
```

### High Memory Usage

**Symptoms:**
- Out of memory errors
- Slow system during operations

**Solutions:**

```bash
# Reduce batch size
pharos resource import ./files/ --batch-size 10

# Limit parallel workers
pharos resource import ./files/ --max-workers 2

# Use streaming for large results
pharos search "query" --stream
```

### Slow Startup

**Symptoms:**
- `pharos --help` takes >1 second
- Initial command is slow

**Solutions:**

```bash
# Check Python import time
python -c "import pharos_cli; print('loaded')"

# Use lazy loading (if available)
# Already optimized in recent versions

# Consider shell completion
# Reduces perceived startup time
```

---

## Getting Help

### Diagnostic Information

Collect information for bug reports:

```bash
# Version information
pharos --version
python --version
pip show pharos-cli

# Configuration
pharos config show --verbose

# Debug output
pharos --verbose health

# Environment
env | grep PHAROS
```

### Check Logs

```bash
# Enable debug logging
export PHAROS_LOG_LEVEL=DEBUG
pharos resource list

# Check log file (if logging to file)
cat ~/.pharos/pharos.log
```

### Common Solutions Summary

| Issue | Quick Fix |
|-------|-----------|
| Command not found | `pip install --user pharos-cli` then `source ~/.bashrc` |
| Auth failed | `pharos auth logout && pharos auth login` |
| Connection refused | Check `pharos config show` for correct API URL |
| Slow commands | Use `--quiet` or `--format json` |
| No color | `pharos resource list --color always` |
| Config error | `pharos init --force` |

### Report Issues

If you cannot resolve your issue:

1. **Check existing issues:** [GitHub Issues](https://github.com/pharos-project/pharos-cli/issues)
2. **Create new issue** with:
   - Error message (full output)
   - Command that failed
   - `pharos --version` output
   - Configuration (masked)
   - Steps to reproduce

### Community Support

- **GitHub Discussions:** [Q&A](https://github.com/pharos-project/pharos-cli/discussions)
- **Documentation:** [Full Docs](https://pharos-cli.readthedocs.io)
- **Backend Docs:** [API Reference](https://pharos.onrender.com/docs)