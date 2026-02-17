"""Main CLI application for Pharos CLI.

This module uses lazy imports to optimize startup time.
All command modules are imported only when their commands are invoked.
"""

import typer

from pharos_cli.version import __version__
from pharos_cli.utils.console import get_console, set_color_mode
from pharos_cli.utils.color import ColorMode
from pharos_cli.utils.pager import PagerMode, get_pager_manager
from pharos_cli.utils.lazy_import import LazyModule

# Lazy-loaded command modules - imported only when command is invoked
_command_modules = {
    'auth': LazyModule('pharos_cli.commands.auth'),
    'config': LazyModule('pharos_cli.commands.config'),
    'resource': LazyModule('pharos_cli.commands.resource'),
    'collection': LazyModule('pharos_cli.commands.collection'),
    'search': LazyModule('pharos_cli.commands.search'),
    'graph': LazyModule('pharos_cli.commands.graph'),
    'batch': LazyModule('pharos_cli.commands.batch'),
    'chat': LazyModule('pharos_cli.commands.chat'),
    'recommend': LazyModule('pharos_cli.commands.recommend'),
    'annotation': LazyModule('pharos_cli.commands.annotation'),
    'quality': LazyModule('pharos_cli.commands.quality'),
    'taxonomy': LazyModule('pharos_cli.commands.taxonomy'),
    'code': LazyModule('pharos_cli.commands.code'),
    'rag': LazyModule('pharos_cli.commands.rag'),
    'system': LazyModule('pharos_cli.commands.system'),
    'backup': LazyModule('pharos_cli.commands.backup'),
}

app = typer.Typer(
    name="pharos",
    help="Pharos CLI - Command-line interface for Pharos knowledge management system",
    add_completion=False,
    )


# Global color mode variable
_color_option: ColorMode = ColorMode.AUTO
# Global pager mode variable
_pager_option: PagerMode = PagerMode.AUTO


@app.callback()
def main_callback(
    color: str = typer.Option(
        "auto",
        "--color",
        "-c",
        help="Color output: auto, always, never",
        case_sensitive=False,
    ),
    no_color: bool = typer.Option(
        False,
        "--no-color",
        help="Disable color output (equivalent to --color never)",
    ),
    pager: str = typer.Option(
        "auto",
        "--pager",
        "-p",
        help="Pager mode: auto, always, never",
        case_sensitive=False,
    ),
    no_pager: bool = typer.Option(
        False,
        "--no-pager",
        help="Disable pager output (equivalent to --pager never)",
    ),
) -> None:
    """Pharos CLI - Command-line interface for Pharos knowledge management system."""
    global _color_option, _pager_option
    
    # --no-color takes precedence
    if no_color:
        _color_option = ColorMode.NEVER
    else:
        # Parse color option
        try:
            _color_option = ColorMode(color.lower())
        except ValueError:
            console = get_console()
            console.print(f"[yellow]Warning:[/yellow] Invalid --color value '{color}'. Using 'auto'.")
            _color_option = ColorMode.AUTO
    
    # Apply color mode to console
    set_color_mode(_color_option)
    
    # --no-pager takes precedence
    if no_pager:
        _pager_option = PagerMode.NEVER
    else:
        # Parse pager option
        try:
            _pager_option = PagerMode(pager.lower())
        except ValueError:
            console = get_console()
            console.print(f"[yellow]Warning:[/yellow] Invalid --pager value '{pager}'. Using 'auto'.")
            _pager_option = PagerMode.AUTO
    
    # Apply pager mode to pager manager
    pager_manager = get_pager_manager()
    pager_manager.mode = _pager_option


# Register subcommands using invoke_with_callback approach
# This allows lazy loading of command modules
@app.command("auth")
def auth_cmd(ctx: typer.Context) -> None:
    """Authentication commands."""
    _get_command_app('auth')
    ctx.invoke(_get_command_app('auth'), obj={})

@app.command("config")
def config_cmd(ctx: typer.Context) -> None:
    """Configuration commands."""
    _get_command_app('config')
    ctx.invoke(_get_command_app('config'), obj={})

@app.command("resource")
def resource_cmd(ctx: typer.Context) -> None:
    """Resource management commands."""
    _get_command_app('resource')
    ctx.invoke(_get_command_app('resource'), obj={})

@app.command("collection")
def collection_cmd(ctx: typer.Context) -> None:
    """Collection management commands."""
    _get_command_app('collection')
    ctx.invoke(_get_command_app('collection'), obj={})

@app.command("search")
def search_cmd(ctx: typer.Context) -> None:
    """Search for resources."""
    _get_command_app('search')
    ctx.invoke(_get_command_app('search'), obj={})

@app.command("graph")
def graph_cmd(ctx: typer.Context) -> None:
    """Knowledge graph and citation commands."""
    _get_command_app('graph')
    ctx.invoke(_get_command_app('graph'), obj={})

@app.command("batch")
def batch_cmd(ctx: typer.Context) -> None:
    """Batch operations for resources and collections."""
    _get_command_app('batch')
    ctx.invoke(_get_command_app('batch'), obj={})

@app.command("chat")
def chat_cmd(ctx: typer.Context) -> None:
    """Interactive chat with your knowledge base."""
    _get_command_app('chat')
    ctx.invoke(_get_command_app('chat'), obj={})

@app.command("recommend")
def recommend_cmd(ctx: typer.Context) -> None:
    """Get recommendations for resources."""
    _get_command_app('recommend')
    ctx.invoke(_get_command_app('recommend'), obj={})

@app.command("annotate")
def annotate_cmd(ctx: typer.Context) -> None:
    """Annotation management commands."""
    _get_command_app('annotate')
    ctx.invoke(_get_command_app('annotate'), obj={})

@app.command("quality")
def quality_cmd(ctx: typer.Context) -> None:
    """Quality assessment commands."""
    _get_command_app('quality')
    ctx.invoke(_get_command_app('quality'), obj={})

@app.command("taxonomy")
def taxonomy_cmd(ctx: typer.Context) -> None:
    """Taxonomy and classification commands."""
    _get_command_app('taxonomy')
    ctx.invoke(_get_command_app('taxonomy'), obj={})

@app.command("code")
def code_cmd(ctx: typer.Context) -> None:
    """Code analysis and intelligence commands."""
    _get_command_app('code')
    ctx.invoke(_get_command_app('code'), obj={})

@app.command("ask")
def rag_cmd(ctx: typer.Context) -> None:
    """Ask questions and get answers from your knowledge base."""
    _get_command_app('rag')
    ctx.invoke(_get_command_app('rag'), obj={})

@app.command("system")
def system_cmd(ctx: typer.Context) -> None:
    """System management commands."""
    _get_command_app('system')
    ctx.invoke(_get_command_app('system'), obj={})

@app.command("backup")
def backup_cmd(ctx: typer.Context) -> None:
    """Backup and restore commands."""
    _get_command_app('backup')
    ctx.invoke(_get_command_app('backup'), obj={})
@app.command()
def version() -> None:
    """Show version information."""
    console = get_console()
    console.print(f"[bold]Pharos CLI[/bold] version [cyan]{__version__}[/cyan]")


@app.command("completion")
def completion(
    shell: str = typer.Argument(
        None,
        help="Shell type: bash, zsh, or fish",
    ),
) -> None:
    """Generate shell completion script."""
    from typer.completion import get_completion_script

    if shell:
        try:
            # Validate shell type
            valid_shells = ["bash", "zsh", "fish", "powershell"]
            if shell.lower() not in valid_shells:
                console = get_console()
                console.print(f"[red]Error:[/red] Invalid shell '{shell}'. Valid options: {', '.join(valid_shells)}")
                raise typer.Exit(1)
            
            # Generate completion script
            prog_name = "pharos"
            complete_var = f"_{prog_name.upper()}_COMPLETE"
            completion_script = get_completion_script(
                prog_name=prog_name,
                complete_var=complete_var,
                shell=shell.lower()
            )
            
            # Print the completion script
            console = get_console()
            console.print(completion_script)
            
        except Exception as e:
            console = get_console()
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
    else:
        console = get_console()
        console.print("Please specify a shell: bash, zsh, or fish")
        console.print("Example: pharos completion bash")
        console.print("")
        console.print("To install completion, run:")
        console.print("  Bash: pharos completion bash >> ~/.bashrc")
        console.print("  Zsh:  pharos completion zsh >> ~/.zshrc")
        console.print("  Fish: pharos completion fish > ~/.config/fish/completions/pharos.fish")
        raise typer.Exit(0)


@app.command()
def info() -> None:
    """Show terminal and color information."""
    from pharos_cli.utils.color import get_terminal_info
    from pharos_cli.utils.pager import get_pager_manager
    
    console = get_console()
    info = get_terminal_info()
    pager_info = get_pager_manager().get_pager_info()
    
    console.print("[bold]Terminal Information[/bold]")
    console.print(f"  Is TTY: {info['is_tty']}")
    console.print(f"  Is CI Environment: {info['is_ci']}")
    console.print(f"  Supports Color: {info['supports_color']}")
    console.print(f"  TERM: {info['term']}")
    console.print(f"  NO_COLOR set: {info['no_color']}")
    console.print(f"  Current color mode: {_color_option.value}")
    console.print("")
    console.print("[bold]Pager Information[/bold]")
    console.print(f"  Pager Available: {pager_info['pager_available']}")
    console.print(f"  Pager Executable: {pager_info['pager_executable'] or 'None'}")
    console.print(f"  Should Use Pager: {pager_info['should_use_pager']}")
    console.print(f"  Current pager mode: {_pager_option.value}")


if __name__ == "__main__":
    app()