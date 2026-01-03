"""Init command for initializing Cliplin projects."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from cliplin.utils.chromadb import get_chromadb_client, initialize_collections
from cliplin.utils.templates import (
    AI_TOOL_CONFIGS,
    create_ai_tool_config,
    create_config_file,
    create_framework_adr,
    create_readme_file,
    create_ts4_format_adr,
    create_ui_intent_format_adr,
)

console = Console()

# Required directory structure
REQUIRED_DIRS = [
    "docs/adrs",
    "docs/business",
    "docs/features",
    "docs/ts4",
    "docs/ui-intent",
    ".cliplin/data/context",
]


def init_command(
    ai: Optional[str] = typer.Option(
        None,
        "--ai",
        help="AI tool ID (cursor, claude-desktop, etc.)",
    ),
) -> None:
    """Initialize a new Cliplin project in the current directory."""
    project_root = Path.cwd()
    
    # Check if already initialized
    if is_cliplin_initialized(project_root):
        console.print(
            "[yellow]⚠[/yellow]  Cliplin appears to be already initialized in this directory."
        )
        if not typer.confirm("Do you want to continue anyway?"):
            console.print("[yellow]Aborted.[/yellow]")
            raise typer.Exit()
    
    console.print(Panel.fit("[bold cyan]Initializing Cliplin Project[/bold cyan]"))
    
    # Validate Python version
    if sys.version_info < (3, 10):
        console.print(
            "[bold red]Error:[/bold red] Python 3.10 or higher is required. "
            f"Current version: {sys.version.split()[0]}"
        )
        raise typer.Exit(code=1)
    
    try:
        # Create directory structure
        console.print("\n[bold]Creating directory structure...[/bold]")
        create_directory_structure(project_root)
        
        # Create configuration files
        console.print("\n[bold]Creating configuration files...[/bold]")
        create_config_file(project_root, ai_tool=ai)
        create_readme_file(project_root)
        
        # Create framework context ADRs
        console.print("\n[bold]Creating framework context documentation...[/bold]")
        create_framework_adr(project_root)
        create_ts4_format_adr(project_root)
        create_ui_intent_format_adr(project_root)
        
        # Create AI tool configuration if specified
        if ai:
            if ai not in AI_TOOL_CONFIGS:
                console.print(
                    f"[bold red]Error:[/bold red] Unknown AI tool: {ai}\n"
                    f"Available tools: {', '.join(AI_TOOL_CONFIGS.keys())}"
                )
                raise typer.Exit(code=1)
            
            console.print(f"\n[bold]Configuring for AI tool: {ai}...[/bold]")
            create_ai_tool_config(project_root, ai)
        
        # Initialize ChromaDB
        console.print("\n[bold]Initializing ChromaDB...[/bold]")
        client = get_chromadb_client(project_root)
        initialize_collections(client)
        
        # Validate project structure
        console.print("\n[bold]Validating project structure...[/bold]")
        validate_project_structure(project_root)
        
        # Success message
        success_text = (
            "[bold green]✓ Cliplin project initialized successfully![/bold green]\n\n"
            f"Project root: [cyan]{project_root}[/cyan]\n"
        )
        if ai:
            success_text += f"AI tool: [cyan]{ai}[/cyan]\n"
        success_text += (
            "\nNext steps:\n"
            "  - Run 'cliplin reindex' to index framework context ADRs\n"
            "  - Add your feature files to docs/features/\n"
            "  - Add your TS4 specs to docs/ts4/\n"
            "  - Run 'cliplin reindex' again to index your new context files"
        )
        console.print()
        console.print(Panel.fit(success_text, border_style="green"))
        
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


def is_cliplin_initialized(project_root: Path) -> bool:
    """Check if Cliplin is already initialized in the project."""
    cliplin_dir = project_root / ".cliplin"
    return cliplin_dir.exists() and (cliplin_dir / "data" / "context").exists()


def create_directory_structure(project_root: Path) -> None:
    """Create the required Cliplin directory structure."""
    for dir_path in REQUIRED_DIRS:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        console.print(f"  [green]✓[/green] Created {dir_path}/")


def validate_project_structure(project_root: Path) -> None:
    """Validate that all required directories exist."""
    missing = []
    for dir_path in REQUIRED_DIRS:
        if not (project_root / dir_path).exists():
            missing.append(dir_path)
    
    if missing:
        console.print(f"  [red]✗[/red] Missing directories: {', '.join(missing)}")
        raise ValueError("Project structure validation failed")
    
    console.print("  [green]✓[/green] All required directories exist")

