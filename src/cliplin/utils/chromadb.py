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
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    return chromadb.PersistentClient(
        path=str(db_path.parent),
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True,
        ),
    )


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
            console.print(f"  [red]✗[/red] Failed to create collection '{collection_name}': {e}")
            raise


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

