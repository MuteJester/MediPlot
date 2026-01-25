"""Shape registry for discovering and loading shape recipes."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

from mediplot.recipes.parser import parse_recipe

if TYPE_CHECKING:
    from collections.abc import Iterator

    from mediplot.core.shape import Shape

# Directory containing built-in recipe data files
_BUILTIN_RECIPES_DIR = Path(__file__).parent / "data"

# Custom recipes registered at runtime
_custom_recipes: dict[str, Path | Shape] = {}


def register_recipe(shape_id: str, source: Path | Shape) -> None:
    """Register a custom shape recipe.

    Args:
        shape_id: Unique identifier for the shape
        source: Either a Path to a JSON file or a Shape object

    Example:
        >>> from pathlib import Path
        >>> register_recipe("my_organ", Path("custom_organ.json"))
    """
    _custom_recipes[shape_id] = source
    # Clear cache to pick up new recipe
    get_shape.cache_clear()


def unregister_recipe(shape_id: str) -> bool:
    """Remove a custom recipe from the registry.

    Args:
        shape_id: The shape identifier to remove

    Returns:
        True if the recipe was removed, False if it wasn't registered
    """
    if shape_id in _custom_recipes:
        del _custom_recipes[shape_id]
        get_shape.cache_clear()
        return True
    return False


@lru_cache(maxsize=64)
def get_shape(shape_id: str) -> Shape:
    """Get a shape by its identifier.

    Searches custom recipes first, then built-in recipes.

    Args:
        shape_id: The shape identifier

    Returns:
        Shape object

    Raises:
        KeyError: If shape not found

    Example:
        >>> shape = get_shape("human_body_anterior")
        >>> print(shape.list_regions())
    """
    # Check custom recipes first
    if shape_id in _custom_recipes:
        source = _custom_recipes[shape_id]
        if isinstance(source, Path):
            return _load_shape_from_file(source)
        return source

    # Search built-in recipes
    for recipe_file in _iter_builtin_recipes():
        if recipe_file.stem == shape_id:
            return _load_shape_from_file(recipe_file)

    available = list_shapes()
    msg = f"Shape '{shape_id}' not found. Available: {', '.join(available[:10])}"
    if len(available) > 10:
        msg += f" ... and {len(available) - 10} more"
    raise KeyError(msg)


def _load_shape_from_file(path: Path) -> Shape:
    """Load a shape from a JSON recipe file.

    Args:
        path: Path to the JSON file

    Returns:
        Shape object
    """
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return parse_recipe(data)


def _iter_builtin_recipes() -> Iterator[Path]:
    """Iterate over all built-in recipe files.

    Yields:
        Path objects for each JSON recipe file
    """
    if not _BUILTIN_RECIPES_DIR.exists():
        return

    for json_file in _BUILTIN_RECIPES_DIR.rglob("*.json"):
        # Skip schema files
        if "schema" in json_file.parts:
            continue
        yield json_file


def list_shapes(category: str | None = None) -> list[str]:
    """List available shape identifiers.

    Args:
        category: Optional category filter (e.g., "body", "organs")

    Returns:
        Sorted list of shape IDs

    Example:
        >>> list_shapes()
        ['heart', 'human_body_anterior', 'human_body_posterior', ...]
        >>> list_shapes("body")
        ['human_body_anterior', 'human_body_posterior']
    """
    shapes: set[str] = set()

    # Add custom shapes
    shapes.update(_custom_recipes.keys())

    # Add built-in shapes
    for recipe_file in _iter_builtin_recipes():
        if category is None or category in recipe_file.parts:
            shapes.add(recipe_file.stem)

    return sorted(shapes)


def list_categories() -> list[str]:
    """List available shape categories.

    Returns:
        Sorted list of category names

    Example:
        >>> list_categories()
        ['body', 'dermatomes', 'organs']
    """
    categories: set[str] = set()

    for recipe_file in _iter_builtin_recipes():
        # Get immediate parent of the file (the category folder)
        parent = recipe_file.parent.name
        if parent != "data":
            categories.add(parent)

    return sorted(categories)
