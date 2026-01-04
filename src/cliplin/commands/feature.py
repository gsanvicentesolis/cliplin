"""Feature apply command for generating implementation prompts."""

from pathlib import Path

import typer
from rich.console import Console

from cliplin.utils.chromadb import get_chromadb_path

console = Console()


def feature_apply_command(
    feature_filepath: str = typer.Argument(
        ...,
        help="Path to the feature file (relative to project root)",
    ),
) -> None:
    """Generate an implementation prompt for a feature file."""
    project_root = Path.cwd()
    
    # Validate feature file path
    feature_path = project_root / feature_filepath
    
    if not feature_path.exists():
        console.print(
            f"[bold red]Error:[/bold red] Feature file not found: {feature_filepath}\n"
            "Please check that the file path is correct."
        )
        raise typer.Exit(code=1)
    
    # Validate file is in docs/features/ directory
    relative_path = feature_path.relative_to(project_root)
    if not str(relative_path).startswith("docs/features/"):
        console.print(
            f"[bold red]Error:[/bold red] File is not in the docs/features/ directory: {feature_filepath}\n"
            "Feature files must be located in docs/features/"
        )
        raise typer.Exit(code=1)
    
    # Validate file extension
    if not feature_path.suffix == ".feature":
        console.print(
            f"[bold red]Error:[/bold red] File is not a valid feature file: {feature_filepath}\n"
            "Feature files must have a .feature extension"
        )
        raise typer.Exit(code=1)
    
    # Check if ChromaDB is initialized
    db_path = get_chromadb_path(project_root)
    if not db_path.exists():
        console.print(
            "[bold red]Error:[/bold red] ChromaDB is not initialized.\n"
            "Run 'cliplin init' to initialize the project first."
        )
        raise typer.Exit(code=1)
    
    try:
        # Read feature file content
        feature_content = feature_path.read_text(encoding="utf-8")
        
        # Generate structured prompt
        prompt = generate_implementation_prompt(
            feature_filepath=relative_path,
            feature_content=feature_content,
        )
        
        # Output prompt to stdout
        console.print(prompt)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


def generate_implementation_prompt(
    feature_filepath: Path,
    feature_content: str,
) -> str:
    """Generate a structured implementation prompt."""
    
    prompt_parts = []
    
    # Header
    prompt_parts.append("# Implementation Prompt")
    prompt_parts.append("")
    prompt_parts.append(f"## Feature: {feature_filepath}")
    prompt_parts.append("")
    
    # Feature Content Section
    prompt_parts.append("## Feature Content")
    prompt_parts.append("")
    prompt_parts.append("```gherkin")
    prompt_parts.append(feature_content)
    prompt_parts.append("```")
    prompt_parts.append("")
    
    # Implementation Instructions Section
    prompt_parts.append("## Implementation Instructions")
    prompt_parts.append("")
    prompt_parts.append("Please implement this feature following the Cliplin framework:")
    prompt_parts.append("")
    prompt_parts.append("1. **Load context**: Query ChromaDB collections to retrieve relevant context (ADRs, TS4 specs, related features, UI Intent)")
    prompt_parts.append("2. **Analyze the feature**: Review all scenarios and understand the business requirements")
    prompt_parts.append("3. **Review context**: Consider the business context, technical constraints, and related features")
    prompt_parts.append("4. **Design architecture**: Identify domain entities, use cases, and boundaries")
    prompt_parts.append("5. **Implement business logic**: Follow the technical specifications and constraints")
    prompt_parts.append("6. **Write tests**: Create unit tests and BDD tests for all scenarios")
    prompt_parts.append("7. **Validate**: Ensure all tests pass and the feature is complete")
    prompt_parts.append("")
    prompt_parts.append("Follow the Cliplin framework rules for feature implementation as defined in the project context.")
    prompt_parts.append("")
    
    return "\n".join(prompt_parts)

