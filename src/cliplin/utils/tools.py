"""Utilities for locating Cliplin tools directory."""

import sys
from pathlib import Path
from typing import Optional

# Try to use importlib.resources (Python 3.9+)
try:
    from importlib.resources import files, as_file
    HAS_RESOURCES = True
except ImportError:
    # Fallback for older Python versions
    HAS_RESOURCES = False


def get_cliplin_tools_dir() -> Optional[Path]:
    """
    Get the path to the Cliplin tools directory.
    
    Searches in the following order:
    1. Package directory (when installed): cliplin/tools/
    2. Development directory: src/cliplin/tools/
    3. Current package location: <package_location>/tools/
    
    Returns:
        Path to tools directory, or None if not found
    """
    # Try importlib.resources first (Python 3.9+)
    if HAS_RESOURCES:
        try:
            # This works when the package is installed
            package = files("cliplin")
            tools_path = package / "tools"
            if tools_path.is_dir():
                # Convert to actual filesystem path
                with as_file(tools_path) as path:
                    return Path(path)
        except (ModuleNotFoundError, TypeError):
            pass
    
    # Fallback: try to find based on __file__ location
    try:
        import cliplin
        if hasattr(cliplin, "__file__") and cliplin.__file__:
            package_dir = Path(cliplin.__file__).parent
            tools_dir = package_dir / "tools"
            if tools_dir.exists():
                return tools_dir
    except (ImportError, AttributeError):
        pass
    
    # Try development location: src/cliplin/tools/
    # Get the current file's location and work backwards
    current_file = Path(__file__)
    # This file is in src/cliplin/utils/, so go up to src/cliplin/
    cliplin_dir = current_file.parent.parent
    tools_dir = cliplin_dir / "tools"
    if tools_dir.exists():
        return tools_dir
    
    # Try to find in sys.path
    for path_str in sys.path:
        path = Path(path_str)
        if path.exists():
            # Check if it's a site-packages or similar (installed package)
            tools_dir = path / "cliplin" / "tools"
            if tools_dir.exists():
                return tools_dir
    
    return None


def get_cliplin_tools_config_path() -> Optional[Path]:
    """
    Get the path to the Cliplin tools configuration file.
    
    Returns:
        Path to tools.yaml, or None if not found
    """
    tools_dir = get_cliplin_tools_dir()
    if tools_dir:
        config_path = tools_dir / "tools.yaml"
        if config_path.exists():
            return config_path
    
    return None

