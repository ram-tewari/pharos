#!/bin/bash
# Shell completion installation script for Pharos CLI
# Supports bash, zsh, and fish shells

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Pharos CLI Shell Completion Installer${NC}"
echo "======================================="
echo ""

# Function to print status messages
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Detect shell
detect_shell() {
    if [ -n "$BASH_VERSION" ]; then
        echo "bash"
    elif [ -n "$ZSH_VERSION" ]; then
        echo "zsh"
    elif [ -n "$FISH_VERSION" ]; then
        echo "fish"
    else
        echo "unknown"
    fi
}

# Check if pharos is installed
check_pharos_installed() {
    if command -v pharos &> /dev/null; then
        return 0
    elif [ -f "$HOME/.local/bin/pharos" ]; then
        return 0
    elif [ -f "$HOME/.local/share/pipx/venvs/pharos-cli/bin/pharos" ]; then
        return 0
    else
        return 1
    fi
}

# Get pharos command path
get_pharos_command() {
    if command -v pharos &> /dev/null; then
        echo "pharos"
    elif [ -f "$HOME/.local/bin/pharos" ]; then
        echo "$HOME/.local/bin/pharos"
    elif [ -f "$HOME/.local/share/pipx/venvs/pharos-cli/bin/pharos" ]; then
        echo "$HOME/.local/share/pipx/venvs/pharos-cli/bin/pharos"
    else
        echo ""
    fi
}

# Install bash completion
install_bash_completion() {
    echo ""
    echo -e "${BLUE}Installing Bash completion...${NC}"
    
    local pharos_cmd=$(get_pharos_command)
    
    if [ -z "$pharos_cmd" ]; then
        print_error "pharos command not found. Please install pharos-cli first."
        return 1
    fi
    
    # Generate completion script
    local completion_script=$($_PHAROS_COMPLETE=bash_source $pharos_cmd 2>/dev/null)
    
    if [ -z "$completion_script" ]; then
        print_error "Failed to generate completion script"
        return 1
    fi
    
    # Determine where to install
    local completion_file="$HOME/.bash_completion.d/pharos"
    
    # Create directory if it doesn't exist
    mkdir -p "$HOME/.bash_completion.d"
    
    # Write completion script
    echo "$completion_script" > "$completion_file"
    chmod 644 "$completion_file"
    
    print_status "Bash completion installed to $completion_file"
    
    # Add to bashrc if needed
    local bashrc="$HOME/.bashrc"
    local source_line="[ -f \"$completion_file\" ] && source \"$completion_file\""
    
    if [ -f "$bashrc" ]; then
        if ! grep -qF "bash_completion.d/pharos" "$bashrc" 2>/dev/null; then
            echo "" >> "$bashrc"
            echo "# Pharos CLI completion" >> "$bashrc"
            echo "$source_line" >> "$bashrc"
            print_status "Added completion source to $bashrc"
        fi
    else
        # Create .bashrc if it doesn't exist
        echo "# ~/.bashrc" > "$bashrc"
        echo "" >> "$bashrc"
        echo "# Pharos CLI completion" >> "$bashrc"
        echo "$source_line" >> "$bashrc"
        print_status "Created $bashrc with completion source"
    fi
    
    echo ""
    print_status "Bash completion installed successfully!"
    echo "  Restart your terminal or run: source $bashrc"
}

# Install zsh completion
install_zsh_completion() {
    echo ""
    echo -e "${BLUE}Installing Zsh completion...${NC}"
    
    local pharos_cmd=$(get_pharos_command)
    
    if [ -z "$pharos_cmd" ]; then
        print_error "pharos command not found. Please install pharos-cli first."
        return 1
    fi
    
    # Generate completion script
    local completion_script=$($_PHAROS_COMPLETE=zsh_source $pharos_cmd 2>/dev/null)
    
    if [ -z "$completion_script" ]; then
        print_error "Failed to generate completion script"
        return 1
    fi
    
    # Determine where to install
    local completion_dir="$HOME/.zsh/completion"
    local completion_file="$completion_dir/_pharos"
    
    # Create directory if it doesn't exist
    mkdir -p "$completion_dir"
    
    # Write completion script
    echo "$completion_script" > "$completion_file"
    chmod 644 "$completion_file"
    
    print_status "Zsh completion installed to $completion_file"
    
    # Check if compinit is configured
    local zshrc="$HOME/.zshrc"
    
    if [ -f "$zshrc" ]; then
        if ! grep -q "compinit" "$zshrc" 2>/dev/null; then
            print_warning "compinit not found in $zshrc"
            echo "  Add 'autoload -U compinit && compinit' to your .zshrc"
        fi
        
        # Add fpath if needed
        if ! grep -q "zsh/completion" "$zshrc" 2>/dev/null; then
            echo "" >> "$zshrc"
            echo "# Pharos CLI completion" >> "$zshrc"
            echo "fpath=(\$HOME/.zsh/completion \$fpath)" >> "$zshrc"
            echo "autoload -U compinit && compinit" >> "$zshrc"
            print_status "Added completion setup to $zshrc"
        fi
    else
        # Create .zshrc if it doesn't exist
        echo "# ~/.zshrc" > "$zshrc"
        echo "" >> "$zshrc"
        echo "# Pharos CLI completion" >> "$zshrc"
        echo "fpath=(\$HOME/.zsh/completion \$fpath)" >> "$zshrc"
        echo "autoload -U compinit && compinit" >> "$zshrc"
        print_status "Created $zshrc with completion setup"
    fi
    
    echo ""
    print_status "Zsh completion installed successfully!"
    echo "  Restart your terminal or run: autoload -U compinit && compinit"
}

# Install fish completion
install_fish_completion() {
    echo ""
    echo -e "${BLUE}Installing Fish completion...${NC}"
    
    local pharos_cmd=$(get_pharos_command)
    
    if [ -z "$pharos_cmd" ]; then
        print_error "pharos command not found. Please install pharos-cli first."
        return 1
    fi
    
    # Generate completion script
    local completion_script=$($_PHAROS_COMPLETE=fish_source $pharos_cmd 2>/dev/null)
    
    if [ -z "$completion_script" ]; then
        print_error "Failed to generate completion script"
        return 1
    fi
    
    # Determine where to install
    local completion_dir="$HOME/.config/fish/completions"
    local completion_file="$completion_dir/pharos.fish"
    
    # Create directory if it doesn't exist
    mkdir -p "$completion_dir"
    
    # Write completion script
    echo "$completion_script" > "$completion_file"
    chmod 644 "$completion_file"
    
    print_status "Fish completion installed to $completion_file"
    echo ""
    print_status "Fish completion installed successfully!"
    echo "  Restart your terminal or run: source $completion_file"
}

# Print usage
usage() {
    echo "Usage: $0 [bash|zsh|fish|all]"
    echo ""
    echo "Options:"
    echo "  bash    Install Bash completion"
    echo "  zsh     Install Zsh completion"
    echo "  fish    Install Fish completion"
    echo "  all     Install completion for all shells (default)"
    echo "  --help  Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Install all shells"
    echo "  $0 bash         # Install Bash only"
    echo "  $0 zsh          # Install Zsh only"
    echo "  $0 fish         # Install Fish only"
}

# Main
main() {
    local shell="${1:-all}"
    
    # Check for help flag
    if [ "$shell" = "--help" ] || [ "$shell" = "-h" ]; then
        usage
        exit 0
    fi
    
    echo "Detecting shell..."
    local detected_shell=$(detect_shell)
    echo "Detected shell: $detected_shell"
    echo ""
    
    # Check if pharos is installed
    if ! check_pharos_installed; then
        print_warning "pharos command not found in PATH"
        echo "  Make sure pharos-cli is installed:"
        echo "    pip install pharos-cli"
        echo "  Or add it to your PATH:"
        echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
        echo ""
    fi
    
    case "$shell" in
        bash)
            install_bash_completion
            ;;
        zsh)
            install_zsh_completion
            ;;
        fish)
            install_fish_completion
            ;;
        all)
            install_bash_completion
            echo ""
            install_zsh_completion
            echo ""
            install_fish_completion
            ;;
        *)
            print_error "Unknown shell: $shell"
            usage
            exit 1
            ;;
    esac
    
    echo ""
    echo "======================================="
    echo -e "${GREEN}Installation complete!${NC}"
    echo "======================================="
    echo ""
    echo "If completion doesn't work immediately:"
    echo "  - Restart your terminal"
    echo "  - Or source your shell configuration:"
    echo "    Bash: source ~/.bashrc"
    echo "    Zsh:  source ~/.zshrc"
    echo "    Fish: source ~/.config/fish/completions/pharos.fish"
}

main "$@"