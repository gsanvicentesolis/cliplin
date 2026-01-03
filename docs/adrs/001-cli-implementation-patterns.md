# ADR-001: CLI Implementation Patterns and Learnings

## Status
Accepted

## Context
During the implementation of the Cliplin CLI tool, several patterns and best practices emerged that should be documented for future CLI development and maintenance.

## Decision

### 1. Command Organization Pattern
**Pattern**: Separate each command into its own module under `commands/` directory.

**Rationale**:
- Maintains clear separation of concerns
- Makes commands easy to test independently
- Allows for better code organization as CLI grows
- Each command can have its own dependencies and utilities

**Implementation**:
```
src/cliplin/
  commands/
    __init__.py
    init.py
    validate.py
    reindex.py
```

### 2. Rich Library Usage Pattern
**Pattern**: Never concatenate Rich objects (Panel, Table, etc.) with strings using `+` operator.

**Rationale**:
- Rich objects cannot be concatenated with strings directly
- Causes runtime errors: "can only concatenate str (not 'Panel') to str"
- Rich objects should be printed separately or their content should be built as strings first

**Correct Pattern**:
```python
# ❌ Wrong
console.print("\n" + Panel.fit(text))

# ✅ Correct
console.print()
console.print(Panel.fit(text))

# ✅ Also correct - build string first
text = "line 1\n" + "line 2\n"
console.print(Panel.fit(text))
```

### 3. Template Directory Discovery Pattern
**Pattern**: Search for template directory in multiple locations with fallback order.

**Rationale**:
- Templates may be in package directory (when installed)
- Templates may be in project root (during development)
- Templates may be in user home directory (for global templates)
- Provides flexibility for different deployment scenarios

**Implementation Order**:
1. Package directory: `package_dir/template`
2. Project root: `project_root/template`
3. Current working directory: `cwd/template`
4. User home: `~/.cliplin/template`

### 4. ChromaDB Collection Management Pattern
**Pattern**: Centralize collection mappings and provide utility functions for file-to-collection resolution.

**Rationale**:
- Ensures consistency across commands
- Makes it easy to add new collection types
- Provides single source of truth for mappings
- Simplifies maintenance when mappings change

**Implementation**:
- Define `COLLECTION_MAPPINGS` dictionary with directory patterns
- Provide `get_collection_for_file()` utility function
- Provide `get_file_type()` utility function
- Centralize in `utils/chromadb.py`

### 5. Early Validation Pattern
**Pattern**: Validate Python version and prerequisites at CLI entry point, not in individual commands.

**Rationale**:
- Fails fast with clear error messages
- Prevents partial initialization
- Provides consistent error handling
- Better user experience

**Implementation**:
- Validate in `cli.py` main callback
- Exit early with clear error message
- Don't proceed with command execution if prerequisites fail

### 6. Development Testing Pattern
**Pattern**: Use editable install (`uv pip install -e .`) for local development and testing.

**Rationale**:
- Changes to code are immediately available
- No need to reinstall after each change
- Faster development cycle
- Can test in isolated directories

**Testing Workflow**:
```bash
# Install in development mode
uv pip install -e .

# Activate venv
source .venv/bin/activate

# Test commands
cliplin --help
cliplin init --ai cursor

# After code changes, reinstall
uv pip install -e . --force-reinstall
```

### 7. Error Handling Pattern
**Pattern**: Use Typer's Exit with appropriate exit codes and Rich for user-friendly error messages.

**Rationale**:
- Consistent error reporting
- Proper exit codes for scripting
- Rich formatting makes errors more readable
- Typer handles exit gracefully

**Implementation**:
```python
try:
    # operation
except Exception as e:
    console.print(f"[bold red]Error:[/bold red] {e}")
    raise typer.Exit(code=1)
```

### 8. Command Structure Pattern
**Pattern**: Each command should:
1. Validate prerequisites
2. Perform operation with progress feedback
3. Display summary/success message
4. Handle errors gracefully

**Rationale**:
- Consistent user experience
- Clear feedback during long operations
- Easy to debug when things go wrong
- Predictable behavior

## Consequences

### Positive
- Code is more maintainable and testable
- Clear patterns for future CLI development
- Better error handling and user experience
- Flexible template discovery
- Consistent collection management

### Negative
- Slightly more verbose code (separate print statements)
- Need to remember Rich library limitations
- Multiple template locations to maintain

## Notes
These patterns were discovered during the initial CLI implementation and should be followed in future CLI development to maintain consistency and avoid common pitfalls.

