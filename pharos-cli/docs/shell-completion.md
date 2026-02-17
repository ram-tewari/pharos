# Shell Completion for Pharos CLI

This document describes how to enable shell completion for the Pharos CLI on different shells.

## Overview

Pharos CLI supports shell completion for:
- **Bash** - Linux/macOS
- **Zsh** - macOS/Linux
- **Fish** - Linux/macOS

## Quick Installation

### Bash

```bash
# Add completion to your current session
pharos completion bash >> ~/.bashrc

# Or install system-wide
sudo pharos completion bash > /etc/bash_completion.d/pharos
```

### Zsh

```bash
# Add completion to your current session
pharos completion zsh >> ~/.zshrc

# Or install to completion directory
mkdir -p ~/.zsh/completion
pharos completion zsh > ~/.zsh/completion/_pharos
```

### Fish

```bash
# Install completion
mkdir -p ~/.config/fish/completions
pharos completion fish > ~/.config/fish/completions/pharos.fish
```

## Using the Installation Script

Pharos CLI includes an installation script that automatically detects your shell and installs the appropriate completion:

```bash
# Install for all shells
./scripts/install_completion.sh

# Install for specific shell only
./scripts/install_completion.sh bash
./scripts/install_completion.sh zsh
./scripts/install_completion.sh fish
```

## Manual Installation

### Bash

1. Generate the completion script:
   ```bash
   pharos completion bash > ~/.bash_completion.d/pharos
   ```

2. Source it in your shell configuration:
   ```bash
   # Add to ~/.bashrc
   source ~/.bash_completion.d/pharos
   ```

3. Restart your terminal or run:
   ```bash
   source ~/.bashrc
   ```

### Zsh

1. Generate the completion script:
   ```bash
   pharos completion zsh > ~/.zsh/completion/_pharos
   ```

2. Make sure compinit is loaded in your `.zshrc`:
   ```zsh
   # Add to ~/.zshrc
   autoload -U compinit
   compinit
   fpath=(~/.zsh/completion $fpath)
   ```

3. Restart your terminal or run:
   ```zsh
   autoload -U compinit && compinit
   ```

### Fish

1. Generate the completion script:
   ```bash
   pharos completion fish > ~/.config/fish/completions/pharos.fish
   ```

2. Restart your terminal - Fish automatically loads completions from this directory.

## Verification

After installation, verify that completion works:

```bash
# Test completion is loaded
pharos <TAB><TAB>

# Should show available commands:
# auth    collection  graph     resource  version
# backup  config      help      search    ...
```

## Troubleshooting

### Completion not working

1. **Restart your terminal** - Some shells need to be restarted after installation.

2. **Check if completion is loaded**:
   ```bash
   # Bash
   type _pharos_completion

   # Zsh
   which _pharos

   # Fish
   complete -p pharos
   ```

3. **Verify shell configuration**:
   ```bash
   # Check if completion file is sourced
   grep -r "pharos" ~/.bashrc ~/.zshrc 2>/dev/null
   ```

### Permission denied errors

If you get permission errors when installing system-wide:

```bash
# Use user-level installation instead
pharos completion bash >> ~/.bashrc
```

### macOS-specific issues

On macOS, you may need to use Homebrew's bash:

```bash
# Install Homebrew bash
brew install bash

# Set as default shell
sudo bash -c 'echo /usr/local/bin/bash >> /etc/shells'
chsh -s /usr/local/bin/bash
```

## How It Works

Pharos CLI uses Typer's built-in shell completion system. When you run `pharos completion <shell>`, it generates a completion script specific to your shell that:

1. **Bash**: Defines a `_pharos_completion` function and registers it with `complete`
2. **Zsh**: Creates a completion function and registers it with `compdef`
3. **Fish**: Uses Fish's `complete` command to register completions

The completion scripts are generated dynamically based on the CLI's command structure, so they automatically stay up-to-date as new commands are added.

## Custom Completion

If you need custom completion for your specific use case, you can generate the base completion script and modify it:

```bash
# Generate base completion
pharos completion bash > my-completion.bash

# Modify as needed
# Then source it:
source my-completion.bash
```

## Related Commands

- `pharos --help` - Show help with all available commands
- `pharos <command> --help` - Show help for a specific command
- `pharos version` - Show version information