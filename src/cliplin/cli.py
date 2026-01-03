"""Main CLI entry point for Cliplin."""

import sys
from typing import Optional

import typer
from rich.console import Console

from cliplin import __version__
from cliplin.commands.init import init_command
from cliplin.commands.validate import validate_command
from cliplin.commands.reindex import reindex_command

app = typer.Typer(
    name="cliplin",
    help="Cliplin CLI - Initialize and manage Cliplin projects for AI-assisted development",
    add_completion=False,
)

console = Console()


def version_callback(value: bool) -> None:
    """Display version information."""
    if value:
        console.print(f"[bold green]cliplin[/bold green] version [cyan]{__version__}[/cyan]")
        console.print(f"Python version: [cyan]{sys.version.split()[0]}[/cyan]")
        try:
            import subprocess
            result = subprocess.run(
                ["uv", "--version"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                console.print(f"uv version: [cyan]{result.stdout.strip()}[/cyan]")
        except Exception:
            pass
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        help="Show version information",
    ),
) -> None:
    """Cliplin CLI - Initialize and manage Cliplin projects."""
    # Validate Python version
    if sys.version_info < (3, 10):
        console.print(
            "[bold red]Error:[/bold red] Python 3.10 or higher is required. "
            f"Current version: {sys.version.split()[0]}"
        )
        raise typer.Exit(code=1)


# Register commands
app.command(name="init")(init_command)
app.command(name="validate")(validate_command)
app.command(name="reindex")(reindex_command)


def main() -> None:
    """CLI entry point."""
    app()

