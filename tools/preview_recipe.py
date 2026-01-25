#!/usr/bin/env python3
"""Preview and validate MediPlot recipe JSON files.

This tool renders recipe files to visually inspect region boundaries,
label positions, and overall shape appearance.

Usage:
    python preview_recipe.py recipe.json
    python preview_recipe.py recipe.json --save output.png
    python preview_recipe.py recipe.json --fill  # Fill regions with colors
    python preview_recipe.py recipe.json --labels  # Show region labels
    python preview_recipe.py recipe.json --grid  # Show coordinate grid
    python preview_recipe.py recipe.json --interactive  # Click to see region info
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.path import Path as MplPath


def load_recipe(recipe_path: Path) -> dict[str, Any]:
    """Load a recipe JSON file.

    Args:
        recipe_path: Path to JSON file

    Returns:
        Recipe dictionary
    """
    with open(recipe_path) as f:
        return json.load(f)


def vertices_to_mpl_path(vertices: list[dict[str, float]]) -> MplPath:
    """Convert vertex list to matplotlib Path.

    Args:
        vertices: List of {"x": float, "y": float} dicts

    Returns:
        matplotlib Path object
    """
    points = [(v["x"], v["y"]) for v in vertices]
    if points:
        points.append(points[0])  # Close the polygon
        codes = [MplPath.MOVETO] + [MplPath.LINETO] * (len(points) - 2) + [MplPath.CLOSEPOLY]
        return MplPath(points, codes)
    return MplPath([(0, 0)], [MplPath.MOVETO])


def preview_recipe(
    recipe: dict[str, Any],
    fill_regions: bool = True,
    show_labels: bool = True,
    show_grid: bool = False,
    show_outline: bool = True,
    interactive: bool = False,
    figsize: tuple[float, float] | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Create a preview visualization of a recipe.

    Args:
        recipe: Recipe dictionary
        fill_regions: Whether to fill regions with colors
        show_labels: Whether to show region labels
        show_grid: Whether to show coordinate grid
        show_outline: Whether to show the outer outline
        interactive: Whether to enable click interaction
        figsize: Optional figure size

    Returns:
        Tuple of (Figure, Axes)
    """
    # Calculate figure size from aspect ratio
    aspect_ratio = recipe.get("metadata", {}).get("aspect_ratio", 1.0)
    if figsize is None:
        base_height = 10
        figsize = (base_height * aspect_ratio + 2, base_height)  # Extra width for colorbar

    fig, ax = plt.subplots(figsize=figsize)

    # Color palette
    colors = plt.cm.tab20.colors
    region_patches: dict[str, mpatches.PathPatch] = {}

    # Draw outline first (if available)
    outline = recipe.get("outline", {})
    if show_outline and outline.get("type") == "polygon":
        outline_verts = outline.get("vertices", [])
        if outline_verts:
            outline_path = vertices_to_mpl_path(outline_verts)
            outline_patch = mpatches.PathPatch(
                outline_path,
                facecolor="white" if fill_regions else "none",
                edgecolor="black",
                linewidth=2,
                zorder=0,
            )
            ax.add_patch(outline_patch)

    # Draw regions
    regions = recipe.get("regions", {})
    for i, (region_id, region) in enumerate(regions.items()):
        path_data = region.get("path", {})

        if path_data.get("type") == "polygon":
            vertices = path_data.get("vertices", [])
            if vertices:
                mpl_path = vertices_to_mpl_path(vertices)

                facecolor = colors[i % len(colors)] if fill_regions else "none"
                alpha = 0.6 if fill_regions else 1.0

                patch = mpatches.PathPatch(
                    mpl_path,
                    facecolor=facecolor,
                    edgecolor="black",
                    linewidth=1,
                    alpha=alpha,
                    zorder=region.get("z_order", 1),
                )
                ax.add_patch(patch)
                region_patches[region_id] = patch

        elif path_data.get("type") == "ellipse":
            cx = path_data.get("center", {}).get("x", 0.5)
            cy = path_data.get("center", {}).get("y", 0.5)
            rx = path_data.get("rx", 0.1)
            ry = path_data.get("ry", 0.1)

            facecolor = colors[i % len(colors)] if fill_regions else "none"
            alpha = 0.6 if fill_regions else 1.0

            ellipse = mpatches.Ellipse(
                (cx, cy),
                width=rx * 2,
                height=ry * 2,
                facecolor=facecolor,
                edgecolor="black",
                linewidth=1,
                alpha=alpha,
                zorder=region.get("z_order", 1),
            )
            ax.add_patch(ellipse)

        # Draw label
        if show_labels:
            label_pos = region.get("label_position", {})
            lx = label_pos.get("x", 0.5)
            ly = label_pos.get("y", 0.5)
            display_name = region.get("display_name", region_id)

            ax.text(
                lx,
                ly,
                display_name,
                ha="center",
                va="center",
                fontsize=7,
                fontweight="bold",
                bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "alpha": 0.7},
                zorder=100,
            )

            # Draw label position marker
            ax.plot(lx, ly, "r+", markersize=6, zorder=101)

    # Configure axes
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_aspect("equal")

    title = recipe.get("display_name", "Preview")
    subtitle = f"{len(regions)} regions"
    if recipe.get("metadata", {}).get("category"):
        subtitle += f" | Category: {recipe['metadata']['category']}"
    ax.set_title(f"{title}\n{subtitle}", fontsize=12)

    if show_grid:
        ax.grid(True, alpha=0.3, linestyle="--")
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    else:
        ax.axis("off")

    # Interactive click handler
    if interactive:

        def on_click(event):
            if event.inaxes != ax:
                return
            x, y = event.xdata, event.ydata
            print(f"\nClick at ({x:.3f}, {y:.3f})")

            # Check which region was clicked
            for region_id, patch in region_patches.items():
                if patch.get_path().contains_point((x, y)):
                    region = regions[region_id]
                    print(f"  Region: {region_id}")
                    print(f"  Display name: {region.get('display_name', 'N/A')}")
                    print(f"  Groups: {region.get('groups', [])}")
                    print(f"  Z-order: {region.get('z_order', 0)}")
                    break
            else:
                print("  No region at this position")

        fig.canvas.mpl_connect("button_press_event", on_click)
        print("Interactive mode: Click on regions to see info. Close window when done.")

    plt.tight_layout()
    return fig, ax


def print_recipe_info(recipe: dict[str, Any]) -> None:
    """Print recipe information to console.

    Args:
        recipe: Recipe dictionary
    """
    print(f"\n{'='*60}")
    print(f"Shape ID: {recipe.get('shape_id', 'N/A')}")
    print(f"Display Name: {recipe.get('display_name', 'N/A')}")
    print(f"Description: {recipe.get('description', 'N/A')}")
    print(f"\nMetadata:")
    for key, value in recipe.get("metadata", {}).items():
        print(f"  {key}: {value}")

    regions = recipe.get("regions", {})
    print(f"\nRegions ({len(regions)}):")
    for region_id, region in regions.items():
        display = region.get("display_name", region_id)
        groups = region.get("groups", [])
        z_order = region.get("z_order", 0)
        path_type = region.get("path", {}).get("type", "unknown")
        print(f"  {region_id}: {display}")
        print(f"    Type: {path_type}, Z-order: {z_order}, Groups: {groups}")

    # Collect all groups
    all_groups: set[str] = set()
    for region in regions.values():
        all_groups.update(region.get("groups", []))
    if all_groups:
        print(f"\nAll groups: {sorted(all_groups)}")

    print(f"{'='*60}\n")


def validate_recipe(recipe: dict[str, Any]) -> list[str]:
    """Validate a recipe and return list of issues.

    Args:
        recipe: Recipe dictionary

    Returns:
        List of issue descriptions (empty if valid)
    """
    issues = []

    # Check required fields
    if not recipe.get("shape_id"):
        issues.append("Missing 'shape_id'")
    if not recipe.get("display_name"):
        issues.append("Missing 'display_name'")
    if not recipe.get("outline"):
        issues.append("Missing 'outline'")
    if not recipe.get("regions"):
        issues.append("Missing 'regions' or empty")

    # Validate regions
    for region_id, region in recipe.get("regions", {}).items():
        if not region.get("display_name"):
            issues.append(f"Region '{region_id}' missing 'display_name'")
        if not region.get("path"):
            issues.append(f"Region '{region_id}' missing 'path'")
        if not region.get("label_position"):
            issues.append(f"Region '{region_id}' missing 'label_position'")

        # Check path validity
        path = region.get("path", {})
        if path.get("type") == "polygon":
            vertices = path.get("vertices", [])
            if len(vertices) < 3:
                issues.append(f"Region '{region_id}' polygon has < 3 vertices")

            # Check coordinate bounds
            for v in vertices:
                x, y = v.get("x", 0), v.get("y", 0)
                if not (0 <= x <= 1 and 0 <= y <= 1):
                    issues.append(f"Region '{region_id}' has out-of-bounds vertex ({x}, {y})")
                    break

    return issues


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Preview and validate MediPlot recipe files")
    parser.add_argument("recipe", type=Path, help="Recipe JSON file to preview")
    parser.add_argument("--save", type=Path, help="Save preview to image file")
    parser.add_argument("--no-fill", action="store_true", help="Don't fill regions with colors")
    parser.add_argument("--no-labels", action="store_true", help="Don't show region labels")
    parser.add_argument("--grid", action="store_true", help="Show coordinate grid")
    parser.add_argument("--no-outline", action="store_true", help="Don't show outer outline")
    parser.add_argument("--interactive", "-i", action="store_true", help="Enable click interaction")
    parser.add_argument("--info", action="store_true", help="Print recipe info to console")
    parser.add_argument("--validate", action="store_true", help="Validate recipe and report issues")
    parser.add_argument("--dpi", type=int, default=150, help="DPI for saved image")

    args = parser.parse_args()

    if not args.recipe.exists():
        print(f"Error: Recipe file not found: {args.recipe}")
        return 1

    print(f"Loading recipe: {args.recipe}")
    recipe = load_recipe(args.recipe)

    if args.info:
        print_recipe_info(recipe)

    if args.validate:
        issues = validate_recipe(recipe)
        if issues:
            print("Validation issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("Validation passed!")

    # Create preview
    fig, ax = preview_recipe(
        recipe,
        fill_regions=not args.no_fill,
        show_labels=not args.no_labels,
        show_grid=args.grid,
        show_outline=not args.no_outline,
        interactive=args.interactive,
    )

    if args.save:
        print(f"Saving to: {args.save}")
        fig.savefig(args.save, dpi=args.dpi, bbox_inches="tight")
        print("Saved!")

    if not args.save or args.interactive:
        plt.show()

    return 0


if __name__ == "__main__":
    sys.exit(main())
