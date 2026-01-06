"""ChromaDB utilities for Cliplin."""

import os
from pathlib import Path
from typing import List, Optional

import chromadb
from chromadb.config import Settings
from rich.console import Console

console = Console()

# Collection mappings
COLLECTION_MAPPINGS = {
    "business-and-architecture": {
        "directories": ["docs/adrs", "docs/business"],
        "file_pattern": "*.md",
        "type": "adr",
    },
    "features": {
        "directories": ["docs/features"],
        "file_pattern": "*.feature",
        "type": "feature",
    },
    "tech-specs": {
        "directories": ["docs/ts4"],
        "file_pattern": "*.ts4",
        "type": "ts4",
    },
    "uisi": {
        "directories": ["docs/ui-intent"],
        "file_pattern": "*.yaml",
        "type": "ui-intent",
    },
}

REQUIRED_COLLECTIONS = list(COLLECTION_MAPPINGS.keys())


def get_chromadb_path(project_root: Path) -> Path:
    """Get the ChromaDB database path for a project."""
    return project_root / ".cliplin" / "data" / "context" / "chroma.sqlite3"


def get_chromadb_client(project_root: Path) -> chromadb.Client:
    """Get or create a ChromaDB client for a project."""
    db_path = get_chromadb_path(project_root)
    db_dir = db_path.parent
    
    # Ensure directory exists and is writable
    try:
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Verify directory was created and is accessible
        if not db_dir.exists():
            raise OSError(f"Failed to create ChromaDB directory: {db_dir}")
        
        # Verify write permissions by attempting to create a test file
        test_file = db_dir / ".cliplin_test_write"
        try:
            test_file.touch()
            test_file.unlink()
        except (OSError, PermissionError) as e:
            raise PermissionError(
                f"No write permission for ChromaDB directory: {db_dir}. "
                f"Error: {e}"
            ) from e
        
        # Use absolute path to avoid issues with relative paths
        db_dir_absolute = db_dir.resolve()
        
    except (OSError, PermissionError) as e:
        error_msg = (
            f"Failed to initialize ChromaDB directory at {db_dir}.\n"
            f"Error: {e}\n"
            f"Please ensure you have write permissions for the project directory."
        )
        console.print(f"[bold red]Error:[/bold red] {error_msg}")
        raise
    
    # Create ChromaDB client with absolute path
    try:
        return chromadb.PersistentClient(
            path=str(db_dir_absolute),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )
    except Exception as e:
        error_msg = (
            f"Failed to create ChromaDB client.\n"
            f"Database path: {db_dir_absolute}\n"
            f"Error: {e}\n"
            f"This may be due to:\n"
            f"  - Insufficient permissions\n"
            f"  - Path too long (Windows limitation)\n"
            f"  - Corrupted existing database\n"
            f"Try removing {db_dir_absolute} and running init again."
        )
        console.print(f"[bold red]Error:[/bold red] {error_msg}")
        raise


def initialize_collections(client: chromadb.Client) -> None:
    """Initialize all required ChromaDB collections."""
    for collection_name in REQUIRED_COLLECTIONS:
        try:
            client.get_or_create_collection(
                name=collection_name,
                metadata={"description": f"Collection for {collection_name}"},
            )
            console.print(f"  [green]✓[/green] Collection '{collection_name}' initialized")
        except Exception as e:
            error_msg = (
                f"Failed to create collection '{collection_name}': {e}\n"
                f"This may indicate a problem with the ChromaDB database.\n"
                f"Try removing the .cliplin/data/context directory and running init again."
            )
            console.print(f"  [red]✗[/red] {error_msg}")
            raise RuntimeError(f"Failed to initialize ChromaDB collection '{collection_name}'") from e


def verify_collections(client: chromadb.Client) -> List[str]:
    """Verify that all required collections exist."""
    existing_collections = [col.name for col in client.list_collections()]
    missing = [col for col in REQUIRED_COLLECTIONS if col not in existing_collections]
    return missing


def get_collection_for_file(file_path: Path, project_root: Path) -> Optional[str]:
    """Determine the ChromaDB collection for a given file path."""
    relative_path = file_path.relative_to(project_root)
    
    for collection_name, mapping in COLLECTION_MAPPINGS.items():
        for directory in mapping["directories"]:
            if str(relative_path).startswith(directory):
                # Check file pattern
                if file_path.match(mapping["file_pattern"]):
                    return collection_name
    
    return None


def get_file_type(file_path: Path, project_root: Path) -> Optional[str]:
    """Get the file type based on path and collection mapping."""
    relative_path = file_path.relative_to(project_root)
    
    for collection_name, mapping in COLLECTION_MAPPINGS.items():
        for directory in mapping["directories"]:
            if str(relative_path).startswith(directory):
                if file_path.match(mapping["file_pattern"]):
                    return mapping["type"]
    
    return None

