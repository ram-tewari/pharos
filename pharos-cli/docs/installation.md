# Installation Guide

This guide covers all methods of installing the Pharos CLI, from simple package manager installation to building from source.

## Prerequisites

Before installing Pharos CLI, ensure you have:

- **Python 3.8 or higher** - Check with `python --version` or `python3 --version`
- **pip** - Python package manager (usually included with Python)
- **Git** - Required for source installations (optional for pip/pipx)

### Verifying Python Installation

```bash
# Check Python version
python --version
# Should output: Python 3.8.x or higher

# Check pip is available
pip --version
# Should show pip version and Python version
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/) or use your system's package manager:

**macOS:**
```bash
brew install python@3.11
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**Windows:**
Download from [python.org](https://www.python.org/downloads/windows/) or use the Microsoft Store.

---

## Installation Methods

### Method 1: pip (Recommended for Most Users)

The simplest way to install Pharos CLI is via pip:

```bash
pip install pharos-cli
```

**Upgrade to the latest version:**
```bash
pip install --upgrade pharos-cli
```

**Install a specific version:**
```bash
pip install pharos-cli==0.1.0
```

**Verify installation:**
```bash
pharos --version
# Should output: pharos-cli 0.1.0
```

### Method 2: pipx (Isolated Installation)

[pipx](https://pypa.github.io/pipx/) installs Python applications in isolated environments, preventing conflicts with other packages.

**Install pipx (if not already installed):**

**macOS:**
```bash
brew install pipx
pipx ensurepath
```

**Ubuntu/Debian:**
```bash
sudo apt install pipx
pipx ensurepath
```

**Windows:**
```bash
pip install --user pipx
pipx ensurepath
```

**Install Pharos CLI with pipx:**
```bash
pipx install pharos-cli
```

**Upgrade pipx installation:**
```bash
pipx upgrade pharos-cli
```

**Reinstall with fresh environment:**
```bash
pipx reinstall pharos-cli
```

**Benefits of pipx:**
- Isolated from system Python packages
- No sudo/admin privileges required
- Clean uninstallation
- Automatic PATH management

### Method 3: pip from GitHub

Install directly from the GitHub repository:

```bash
# Latest development version
pip install git+https://github.com/pharos-project/pharos-cli.git

# Specific branch
pip install git+https://github.com/pharos-project/pharos-cli.git@main

# Specific tag/version
pip install git+https://github.com/pharos-project/pharos-cli.git@v0.1.0
```

### Method 4: Source Installation

For development or to access unreleased features:

```bash
# Clone the repository
git clone https://github.com/pharos-project/pharos-cli
cd pharos-cli

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# Install in editable mode (for development)
pip install -e ".[dev]"

# Or install without dev dependencies
pip install .
```

**Verify editable installation:**
```bash
pharos --version
```

**Update from source:**
```bash
git pull origin main
pip install -e .
```

---

## Platform-Specific Instructions

### macOS

**Using Homebrew:**
```bash
# If you have a Homebrew formula (when available)
brew install pharos-cli
```

**Using pip/pipx:**
```bash
pipx install pharos-cli
```

**Note:** On macOS, you may need to install Xcode command-line tools:
```bash
xcode-select --install
```

### Linux (Ubuntu/Debian)

```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# Install with pipx (recommended)
pipx install pharos-cli

# Or with pip
pip install pharos-cli
```

### Linux (Fedora/RHEL)

```bash
# Install dependencies
sudo dnf install python3 python3-pip git

# Install with pipx
pipx install pharos-cli
```

### Windows

**Using PowerShell:**
```powershell
# Ensure Python is in PATH
python --version

# Install via pip
pip install pharos-cli

# Or using pipx
pipx install pharos-cli
```

**Note:** On Windows, the config file location is `%APPDATA%\pharos\config.yaml`.

---

## Verifying Your Installation

After installation, verify everything works:

```bash
# Check version
pharos --version

# Show help
pharos --help

# Initialize configuration
pharos init

# Check health (after authentication)
pharos health
```

Expected output for `--version`:
```
Pharos CLI v0.1.0
Python: 3.11.x
Platform: macOS-14.0-arm64
```

Expected output for `--help`:
```
 Usage: pharos [OPTIONS] COMMAND [ARGS]...

 Command-line interface for Pharos knowledge management system.

 Options:
 --version  Show the version and exit.
 --help     Show this message and exit.

 Commands:
 auth       Authentication commands
 backup     Database backup and restore
 batch      Batch operations
 cache      Cache management
 chat       Interactive chat mode
 code       Code analysis commands
 collection Collection management
 graph      Knowledge graph commands
 health     System health check
 quality    Quality assessment commands
 recommend  Recommendation commands
 resource   Resource management
 search     Search knowledge base
 taxonomy   Taxonomy and classification
```

---

## Troubleshooting Installation Issues

### "pharos: command not found"

**Cause:** The installation directory is not in your PATH.

**Solutions:**

1. **For pip installations:**
   ```bash
   # Find where pip installed pharos
   pip show pharos-cli
   # Look at "Location" field
   
   # Add to PATH (add to ~/.bashrc or ~/.zshrc)
   export PATH="$HOME/.local/bin:$PATH"
   source ~/.bashrc  # or ~/.zshrc
   ```

2. **For pipx installations:**
   ```bash
   # pipx should auto-configure PATH, but verify:
   pipx ensurepath
   source ~/.bashrc  # or ~/.zshrc
   ```

3. **For Windows:**
   ```powershell
   # Add to User PATH
   [Environment]::SetEnvironmentVariable(
       "Path",
       $env:Path + ";$env:USERPROFILE\AppData\Roaming\Python\Python311\Scripts",
       "User"
   )
   ```

### Permission Errors

**Cause:** Installing without proper permissions.

**Solutions:**

1. **Use pipx (recommended):**
   ```bash
   pipx install pharos-cli
   ```

2. **Use user installation:**
   ```bash
   pip install --user pharos-cli
   ```

3. **For system-wide install (not recommended):**
   ```bash
   sudo pip install pharos-cli
   ```

### Python Version Error

**Cause:** Python version is too old.

**Solution:** Install Python 3.8 or higher:
```bash
# macOS with Homebrew
brew install python@3.11

# Ubuntu/Debian
sudo apt install python3.11

# Check version
python3.11 --version
```

### SSL/TLS Certificate Errors

**Cause:** Outdated certificates or proxy issues.

**Solutions:**

1. **Update certificates:**
   ```bash
   # macOS
   /Applications/Python\ 3.x/Install\ Certificates.command
   
   # Ubuntu/Debian
   sudo apt install ca-certificates
   sudo update-ca-certificates
   ```

2. **Disable SSL verification (not recommended for production):**
   ```bash
   PHAROS_VERIFY_SSL=0 pharos health
   ```

---

## Uninstalling

### Using pip

```bash
pip uninstall pharos-cli
```

### Using pipx

```bash
pipx uninstall pharos-cli
```

### Manual Cleanup

Remove configuration files:

```bash
# Linux/macOS
rm -rf ~/.pharos/
rm -rf ~/.config/pharos/

# Windows
Remove-Item -Recurse -Force $env:APPDATA\pharos
```

---

## Next Steps

After successful installation:

1. **[Initialize Configuration](configuration.md)** - Set up your first configuration
2. **[Authentication](authentication.md)** - Log in to your Pharos account
3. **[Quick Start Guide](../README.md#quick-start)** - Get started with basic commands

---

## Getting Help

If you encounter issues not covered here:

- **[Troubleshooting Guide](troubleshooting.md)** - Common issues and solutions
- **[FAQ](faq.md)** - Frequently asked questions
- **[GitHub Issues](https://github.com/pharos-project/pharos-cli/issues)** - Report bugs
- **[GitHub Discussions](https://github.com/pharos-project/pharos-cli/discussions)** - Ask questions