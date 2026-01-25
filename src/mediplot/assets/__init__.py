"""
Asset loading utilities for MediPlot.

This module provides functions to reliably load bundled assets
(images, templates) regardless of how the package is installed.
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from importlib.abc import Traversable

# Reference to this package's assets directory
_ASSETS_DIR: Traversable = files(__package__)


def get_asset_path(filename: str) -> Path:
    """
    Get the path to a bundled asset file.

    Args:
        filename: Name of the asset file (e.g., 'body_silhouette.png')

    Returns:
        Path to the asset file.

    Raises:
        FileNotFoundError: If the asset doesn't exist.
    """
    asset = _ASSETS_DIR.joinpath(filename)

    # For installed packages, we may need to extract to a temp location
    # importlib.resources handles this automatically
    if hasattr(asset, '__fspath__'):
        path = Path(asset)  # type: ignore[arg-type]
    else:
        # Fallback for older Python or edge cases
        import importlib.resources as resources
        with resources.as_file(asset) as path:
            return path

    if not path.exists():
        raise FileNotFoundError(f"Asset not found: {filename}")

    return path


def list_assets() -> list[str]:
    """
    List all available asset files.

    Returns:
        List of asset filenames.
    """
    return [
        item.name
        for item in _ASSETS_DIR.iterdir()
        if not item.name.startswith("_") and not item.name.endswith(".py")
    ]
