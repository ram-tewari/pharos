# Configuration Guide

This guide explains how to configure Pharos CLI for different environments, manage multiple profiles, and use environment variables for CI/CD pipelines.

## Configuration Overview

Pharos CLI uses a YAML configuration file to store settings. The configuration is loaded in the following order (later sources override earlier ones):

1. **System-wide config** - `/etc/pharos/config.yaml` (Linux) or equivalent
2. **User config** - `~/.pharos/config.yaml` or `~/.config/pharos/config.yaml`
3. **Project config** - `./.pharos.yaml` (current directory)
4. **Environment variables** - Override any config file settings
5. **CLI flags** - Override all other settings

## Initial Configuration

### Interactive Setup

Run the initialization wizard to create your first configuration:

```bash
pharos init
```

The wizard will:

1. **Create config directory** - `~/.pharos/` (Linux/macOS) or `%APPDATA%\pharos` (Windows)
2. **Prompt for API URL** - Enter your Pharos backend URL
3. **Prompt for authentication** - Choose API key or OAuth2
4. **Create default profile** - Sets up the `default` profile
5. **Test connection** - Verifies connectivity to the API

### Manual Configuration

Create the config file manually:

```bash
mkdir -p ~/.pharos
touch ~/.pharos/config.yaml
```

## Config File Structure

### Basic Configuration

```yaml
# ~/.pharos/config.yaml

# Active profile (must match a profile name below)
active_profile: default

# Profile configurations
profiles:
  default:
    api_url: http://localhost:8000
    api_key: null  # Stored securely in keyring
    timeout: 30
    verify_ssl: true

# Output preferences
output:
  format: table  # table, json, tree, csv, quiet
  color: auto    # auto, always, never
  pager: auto    # auto, always, never

# Behavior settings
behavior:
  confirm_destructive: true
  show_progress: true
  parallel_batch: true
  max_workers: 4
```

### Multiple Profiles

```yaml
active_profile: development

profiles:
  # Local development
  development:
    api_url: http://localhost:8000
    api_key: null
    timeout: 30
    verify_ssl: false

  # Staging environment
  staging:
    api_url: https://staging.pharos.example.com
    api_key: null
    timeout: 60
    verify_ssl: true

  # Production environment
  production:
    api_url: https://pharos.onrender.com
    api_key: null
    timeout: 60
    verify_ssl: true

# Output settings (shared across profiles)
output:
  format: table
  color: auto
  pager: auto

behavior:
  confirm_destructive: true
  show_progress: true
```

## Profile Management

### Creating a New Profile

**Using `pharos init`:**
```bash
pharos init --profile myprofile
```

**Manual addition to config.yaml:**
```yaml
active_profile: default

profiles:
  default:
    api_url: http://localhost:8000
    api_key: null
    timeout: 30
    verify_ssl: true

  myprofile:
    api_url: https://my-pharos-instance.com
    api_key: null
    timeout: 60
    verify_ssl: true
```

### Switching Profiles

**Using CLI flag:**
```bash
pharos --profile production resource list
```

**Using environment variable:**
```bash
PHAROS_PROFILE=production pharos resource list
```

**Changing active profile:**
```bash
# Edit config.yaml and change active_profile
pharos config set active_profile production
```

### Viewing Current Configuration

```bash
# Show full configuration (masked API key)
pharos config show

# Show specific section
pharos config show --section profiles

# Show active profile
pharos config show --section active_profile
```

Output example:
```
Active Profile: default

Profiles:
  default:
    api_url: http://localhost:8000
    api_key: ************
    timeout: 30
    verify_ssl: true

Output:
  format: table
  color: auto
  pager: auto

Behavior:
  confirm_destructive: true
  show_progress: true
  parallel_batch: true
  max_workers: 4
```

## Environment Variables

Override config file settings using environment variables:

### Core Settings

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `PHAROS_API_URL` | API endpoint URL | From config |
| `PHAROS_API_KEY` | API authentication key | From config/keyring |
| `PHAROS_PROFILE` | Active profile name | `default` |
| `PHAROS_TIMEOUT` | Request timeout in seconds | 30 |

### Output Settings

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `PHAROS_OUTPUT_FORMAT` | Output format (table, json, tree, csv, quiet) | `table` |
| `PHAROS_COLOR` | Color output (auto, always, never) | `auto` |
| `PHAROS_PAGER` | Use pager for long output (auto, always, never) | `auto` |
| `PHAROS_NO_COLOR` | Disable colors (any value) | Not set |

### Behavior Settings

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `PHAROS_CONFIRM_DESTRUCTIVE` | Confirm before delete operations | `true` |
| `PHAROS_SHOW_PROGRESS` | Show progress bars | `true` |
| `PHAROS_PARALLEL_BATCH` | Use parallel processing for batch ops | `true` |
| `PHAROS_MAX_WORKERS` | Max parallel workers | 4 |

### Example Usage

```bash
# CI/CD pipeline usage
export PHAROS_API_URL="https://pharos.onrender.com"
export PHAROS_API_KEY="$PHAROS_API_KEY"
export PHAROS_OUTPUT_FORMAT="json"
export PHAROS_NO_COLOR="1"

# Run commands
pharos resource list
pharos search "security" --format json > results.json
```

## Project-Level Configuration

Create a `.pharos.yaml` file in your project root for project-specific settings:

```yaml
# .pharos.yaml (project root)

# Project-specific API settings
api_url: https://pharos.mycompany.com
api_key: null  # Use keyring or env var

# Project-specific output settings
output:
  format: json

# Default filters for project
defaults:
  resource_type: code
  min_quality: 0.7
```

This allows different projects to have different configurations while sharing the same CLI installation.

## Credential Storage

API keys are stored securely using your system's keyring:

```bash
# Store API key (done automatically during login)
pharos auth login --api-key YOUR_KEY

# Verify keyring storage
pharos config show
# API key will be masked as ************

# Remove stored credentials
pharos auth logout
```

### Keyring Backend

Pharos CLI uses the `keyring` library to store credentials. The appropriate backend is selected automatically:

- **macOS:** Keychain
- **Windows:** Credential Manager
- **Linux:** Secret Service (GNOME Keyring, KWallet) or pass

### Troubleshooting Keyring

If keyring is not available:

```bash
# Install keyring with all backends
pip install keyring[all]

# Or use a specific backend
pip install keyring-backends

# Fallback: Use environment variable
export PHAROS_API_KEY="your-key-here"
```

## Advanced Configuration

### Timeout Settings

```yaml
profiles:
  default:
    api_url: http://localhost:8000
    timeout: 30  # 30 seconds
    connect_timeout: 10  # Connection timeout
    read_timeout: 60  # Read timeout for large responses
    write_timeout: 60  # Write timeout for large uploads
```

### SSL/TLS Settings

```yaml
profiles:
  default:
    api_url: https://pharos.example.com
    verify_ssl: true
    # For custom CA certificates:
    # ssl_cert_path: /path/to/ca-bundle.crt
```

### Proxy Settings

```yaml
profiles:
  default:
    api_url: https://pharos.example.com
    proxy:
      http: http://proxy.example.com:8080
      https: https://proxy.example.com:8080
```

Set via environment variables:
```bash
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="https://proxy.example.com:8080"
```

### Batch Processing Settings

```yaml
behavior:
  confirm_destructive: true
  show_progress: true
  parallel_batch: true
  max_workers: 4  # Adjust based on your system
  batch_size: 100  # Items per batch
  retry_attempts: 3
  retry_delay: 1  # Seconds between retries
```

## Configuration Validation

Validate your configuration file:

```bash
# Check config syntax
pharos config validate

# Test API connectivity
pharos health

# Test with verbose output
pharos --verbose resource list
```

## Resetting Configuration

Reset to default configuration:

```bash
# Backup current config
cp ~/.pharos/config.yaml ~/.pharos/config.yaml.backup

# Reset to defaults
pharos init --force

# Or manually remove and recreate
rm ~/.pharos/config.yaml
pharos init
```

## Configuration File Locations

| Platform | Location |
|----------|----------|
| Linux | `~/.pharos/config.yaml` or `~/.config/pharos/config.yaml` |
| macOS | `~/.pharos/config.yaml` or `~/Library/Application Support/pharos/config.yaml` |
| Windows | `%APPDATA%\pharos\config.yaml` |
| Project | `./.pharos.yaml` |

Check the effective config location:
```bash
pharos config show --path
```

## Next Steps

- **[Authentication Guide](authentication.md)** - Set up API access
- **[Command Reference](commands.md)** - Explore all available commands
- **[Examples](examples.md)** - Common workflows and scripts

## Getting Help

- **[Troubleshooting](troubleshooting.md)** - Common configuration issues
- **[FAQ](faq.md)** - Frequently asked questions
- **[GitHub Issues](https://github.com/pharos-project/pharos-cli/issues)** - Report problems