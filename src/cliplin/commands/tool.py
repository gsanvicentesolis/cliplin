"""Tool command for opening SPA tools in a webview."""

from pathlib import Path
from typing import Dict, Optional

import typer
import yaml
from rich.console import Console
from rich.table import Table

from cliplin.utils.tools import get_cliplin_tools_dir, get_cliplin_tools_config_path

console = Console()


def tool_command(
    tool_name: Optional[str] = typer.Argument(
        None,
        help="Name of the tool to open",
    ),
    list_tools: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="List all available tools",
    ),
) -> None:
    """Open a tool in a webview or list available tools."""
    # Get Cliplin tools directory (from package, not project)
    tools_dir = get_cliplin_tools_dir()
    if not tools_dir:
        console.print(
            "[bold red]Error:[/bold red] Cliplin tools directory not found.\n"
            "The tools directory should be part of the Cliplin package installation.\n"
            "If you're developing Cliplin, ensure the tools directory exists in src/cliplin/tools/\n"
        )
        raise typer.Exit(code=1)
    
    # Check if tools configuration file exists
    tools_config_path = get_cliplin_tools_config_path()
    if not tools_config_path:
        console.print(
            "[bold red]Error:[/bold red] Cliplin tools configuration file not found.\n"
            f"Expected file: [cyan]{tools_dir / 'tools.yaml'}[/cyan]\n\n"
            "The tools.yaml file should be part of the Cliplin package.\n"
            "If you're developing Cliplin, ensure tools.yaml exists in src/cliplin/tools/\n"
        )
        raise typer.Exit(code=1)
    
    try:
        # Load tools configuration
        config = load_tools_config(tools_config_path)
        tools = config.get("tools", {})
        
        # List tools if requested or no tool name provided
        if list_tools:
            list_available_tools(tools)
            raise typer.Exit()
        
        if tool_name is None:
            console.print(
                "[bold yellow]No tool name provided.[/bold yellow]\n"
                "Use [cyan]cliplin tool --list[/cyan] to see available tools.\n"
                "Or specify a tool name: [cyan]cliplin tool <tool-name>[/cyan]\n"
            )
            list_available_tools(tools)
            raise typer.Exit(code=1)
        
        # Validate tool exists
        if tool_name not in tools:
            console.print(
                f"[bold red]Error:[/bold red] Tool '{tool_name}' not found.\n"
            )
            list_available_tools(tools)
            raise typer.Exit(code=1)
        
        # Get tool file path
        tool_file = tools[tool_name]
        
        # Resolve file path (relative to tools/ or absolute)
        if Path(tool_file).is_absolute():
            tool_path = Path(tool_file)
        else:
            tool_path = tools_dir / tool_file
        
        # Validate file exists
        if not tool_path.exists():
            console.print(
                f"[bold red]Error:[/bold red] Tool file not found: {tool_path}\n"
                f"Configured path: [cyan]{tool_file}[/cyan]\n"
                f"Resolved path: [cyan]{tool_path}[/cyan]\n"
            )
            raise typer.Exit(code=1)
        
        # Open tool in webview
        console.print(f"[bold]Opening tool:[/bold] [cyan]{tool_name}[/cyan]")
        console.print(f"File: [cyan]{tool_path}[/cyan]")
        
        open_tool_in_webview(tool_path, tool_name)
        
    except yaml.YAMLError as e:
        console.print(
            f"[bold red]Error:[/bold red] Invalid YAML in tools configuration file.\n"
            f"Details: {e}\n"
        )
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


def load_tools_config(config_path: Path) -> Dict:
    """Load tools configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    if not config:
        return {"tools": {}}
    
    return config


def list_available_tools(tools: Dict[str, str]) -> None:
    """Display a list of available tools."""
    if not tools:
        console.print("[yellow]No tools configured in Cliplin.[/yellow]")
        console.print(
            "\nTools are part of the Cliplin package. "
            "If you're developing Cliplin, add tools to [cyan]src/cliplin/tools/tools.yaml[/cyan]\n"
            "with the following structure:\n"
            "```yaml\n"
            "tools:\n"
            "  ui-intent: ui-intent.html\n"
            "  another-tool: subdirectory/tool.html\n"
            "```\n"
        )
        return
    
    table = Table(title="Available Tools")
    table.add_column("Tool Name", style="cyan", no_wrap=True)
    table.add_column("File Path", style="magenta")
    
    for tool_name, tool_file in sorted(tools.items()):
        table.add_row(tool_name, tool_file)
    
    console.print()
    console.print(table)
    console.print()


def open_tool_in_webview(file_path: Path, tool_name: str) -> None:
    """Open a tool file in a webview window."""
    try:
        import webview
    except ImportError:
        console.print(
            "[bold red]Error:[/bold red] webview library not installed.\n"
            "Install it with: [cyan]pip install pywebview[/cyan]\n"
            "Or: [cyan]uv pip install pywebview[/cyan]\n"
        )
        raise typer.Exit(code=1)
    
    # Convert file path to file:// URL
    file_url = file_path.as_uri()
    
    try:
        # Create and show webview window
        window = webview.create_window(
            title=f"Cliplin Tool: {tool_name}",
            url=file_url,
            width=1200,
            height=800,
            resizable=True,
        )
        
        console.print("[green]✓[/green] Webview opened successfully")
        console.print("[dim]Press Ctrl+C to close the webview[/dim]")
        
        # Start webview (this blocks until window is closed)
        webview.start(debug=False)
        
    except Exception as e:
        console.print(
            f"[bold red]Error:[/bold red] Failed to open webview.\n"
            f"Details: {e}\n"
        )
        console.print(
            "Troubleshooting:\n"
            "  - Ensure pywebview is installed correctly\n"
            "  - Check that the file path is valid\n"
            "  - Verify that the file is a valid HTML file\n"
        )
        raise typer.Exit(code=1)

