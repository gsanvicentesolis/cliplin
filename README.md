# Cliplin CLI

A command-line tool for initializing and managing Cliplin projects with AI-assisted development.

## Installation

### Using uv (Recommended)

```bash
uv tool install cliplin
```

Or for one-time execution:

```bash
uvx cliplin
```

### Development Installation

```bash
uv pip install -e .
```

## Usage

### Initialize a Project

```bash
# Initialize with default settings
cliplin init

# Initialize with Cursor AI tool
cliplin init --ai cursor

# Initialize with Claude Desktop
cliplin init --ai claude-desktop
```

### Validate Project Structure

```bash
cliplin validate
```

### Reindex Context Files

```bash
# Reindex all context files
cliplin reindex

# Reindex a specific file
cliplin reindex docs/features/my-feature.feature

# Reindex files of a specific type
cliplin reindex --type ts4

# Reindex files in a directory
cliplin reindex --directory docs/business

# Dry run (preview changes)
cliplin reindex --dry-run

# Verbose output
cliplin reindex --verbose

# Interactive mode (with confirmation)
cliplin reindex --interactive
```

## Requirements

- Python 3.10 or higher
- uv (Astral UV) for installation

## Project Structure

After initialization, a Cliplin project has the following structure:

```
.
├── docs/
│   ├── adrs/          # Architecture Decision Records
│   ├── business/      # Business documentation
│   ├── features/       # Feature files (Gherkin)
│   ├── ts4/           # Technical specifications
│   └── ui-intent/      # UI Intent specifications
└── .cliplin/
    ├── config.yaml
    └── data/
        └── context/
            └── chroma.sqlite3  # ChromaDB database
```

## License

MIT

