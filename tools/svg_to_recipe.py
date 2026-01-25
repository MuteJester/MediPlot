#!/usr/bin/env python3
"""Convert SVG files to MediPlot recipe JSON format.

This tool parses SVG files and converts paths to our JSON recipe format.
It handles basic SVG path commands (M, L, C, Q, Z) and normalizes coordinates.

Usage:
    python svg_to_recipe.py input.svg output.json --shape-id my_shape
    python svg_to_recipe.py input.svg output.json --preview  # Show preview before saving
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PathCommand:
    """A single SVG path command."""

    command: str  # M, L, C, Q, Z, etc.
    points: list[tuple[float, float]]
    relative: bool = False


@dataclass
class SVGPath:
    """Parsed SVG path with metadata."""

    id: str
    commands: list[PathCommand]
    fill: str | None = None
    stroke: str | None = None
    label: str | None = None
    groups: list[str] = field(default_factory=list)


def parse_svg_path_d(d: str) -> list[PathCommand]:
    """Parse SVG path 'd' attribute into commands.

    Args:
        d: The path data string (e.g., "M 0 0 L 10 10 Z")

    Returns:
        List of PathCommand objects
    """
    # Tokenize the path data
    # Split on commands while keeping the command letter
    tokens = re.findall(r"([MmLlHhVvCcSsQqTtAaZz])|([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)", d)

    commands = []
    current_cmd = None
    current_points: list[float] = []

    for token in tokens:
        cmd_letter, number = token
        if cmd_letter:
            # Save previous command if exists
            if current_cmd is not None:
                commands.append(_make_command(current_cmd, current_points))
            current_cmd = cmd_letter
            current_points = []
        elif number:
            current_points.append(float(number))

    # Save last command
    if current_cmd is not None:
        commands.append(_make_command(current_cmd, current_points))

    return commands


def _make_command(cmd: str, points: list[float]) -> PathCommand:
    """Create a PathCommand from command letter and point values."""
    relative = cmd.islower()
    cmd_upper = cmd.upper()

    # Convert flat list to point tuples based on command type
    point_tuples: list[tuple[float, float]] = []

    if cmd_upper == "Z":
        # Close path - no points
        pass
    elif cmd_upper == "H":
        # Horizontal line - only x values
        point_tuples = [(x, 0.0) for x in points]
    elif cmd_upper == "V":
        # Vertical line - only y values
        point_tuples = [(0.0, y) for y in points]
    elif cmd_upper in ("M", "L", "T"):
        # Move, Line, Smooth quadratic - pairs of x,y
        for i in range(0, len(points) - 1, 2):
            point_tuples.append((points[i], points[i + 1]))
    elif cmd_upper in ("Q", "S"):
        # Quadratic Bezier, Smooth cubic - pairs of x,y
        for i in range(0, len(points) - 1, 2):
            point_tuples.append((points[i], points[i + 1]))
    elif cmd_upper == "C":
        # Cubic Bezier - 6 values (3 points) per curve
        for i in range(0, len(points) - 1, 2):
            point_tuples.append((points[i], points[i + 1]))
    elif cmd_upper == "A":
        # Arc - complex, we'll approximate
        # rx ry x-axis-rotation large-arc-flag sweep-flag x y
        for i in range(0, len(points) - 6, 7):
            # Just grab the endpoint for simplification
            point_tuples.append((points[i + 5], points[i + 6]))

    return PathCommand(command=cmd_upper, points=point_tuples, relative=relative)


def parse_svg_file(svg_path: Path) -> tuple[list[SVGPath], tuple[float, float, float, float]]:
    """Parse an SVG file and extract paths.

    Args:
        svg_path: Path to SVG file

    Returns:
        Tuple of (list of SVGPath objects, viewBox as (x, y, width, height))
    """
    tree = ET.parse(svg_path)
    root = tree.getroot()

    # Handle namespace
    ns = {"svg": "http://www.w3.org/2000/svg"}
    if root.tag.startswith("{"):
        ns_uri = root.tag[1 : root.tag.index("}")]
        ns = {"svg": ns_uri}

    # Get viewBox for coordinate normalization
    viewbox_str = root.get("viewBox", "0 0 100 100")
    viewbox = tuple(map(float, viewbox_str.split()))
    if len(viewbox) != 4:
        viewbox = (0, 0, 100, 100)

    # Also check width/height if no viewBox
    if viewbox == (0, 0, 100, 100):
        width = root.get("width", "100")
        height = root.get("height", "100")
        # Remove units like 'px', 'pt', etc.
        width = float(re.sub(r"[^\d.]", "", width) or "100")
        height = float(re.sub(r"[^\d.]", "", height) or "100")
        viewbox = (0, 0, width, height)

    paths: list[SVGPath] = []

    # Find all path elements (with and without namespace)
    for path_elem in root.iter():
        tag = path_elem.tag
        if isinstance(tag, str):
            tag = tag.split("}")[-1]  # Remove namespace prefix

        if tag == "path":
            d = path_elem.get("d", "")
            if not d:
                continue

            path_id = path_elem.get("id", f"path_{len(paths)}")
            fill = path_elem.get("fill")
            stroke = path_elem.get("stroke")

            # Try to get label from various attributes
            label = (
                path_elem.get("inkscape:label")
                or path_elem.get("label")
                or path_elem.get("title")
                or path_id
            )

            # Parse groups from parent elements
            groups = []
            parent = path_elem
            while parent is not None:
                parent_id = parent.get("id", "")
                if parent_id and parent_id != path_id:
                    groups.append(parent_id)
                # This is a simplified parent traversal
                break

            commands = parse_svg_path_d(d)
            paths.append(
                SVGPath(
                    id=path_id,
                    commands=commands,
                    fill=fill,
                    stroke=stroke,
                    label=label,
                    groups=groups,
                )
            )

    return paths, viewbox


def commands_to_vertices(
    commands: list[PathCommand],
    viewbox: tuple[float, float, float, float],
    flip_y: bool = True,
) -> list[tuple[float, float]]:
    """Convert path commands to normalized vertices.

    Args:
        commands: List of PathCommand objects
        viewbox: SVG viewBox (x, y, width, height)
        flip_y: Whether to flip Y axis (SVG is top-down, we want bottom-up)

    Returns:
        List of normalized (x, y) vertices
    """
    vb_x, vb_y, vb_w, vb_h = viewbox
    vertices: list[tuple[float, float]] = []
    current_x, current_y = 0.0, 0.0
    start_x, start_y = 0.0, 0.0

    for cmd in commands:
        if cmd.command == "Z":
            # Close path - return to start
            if vertices and (start_x, start_y) != vertices[-1]:
                vertices.append((start_x, start_y))
            continue

        for px, py in cmd.points:
            if cmd.relative:
                if cmd.command == "H":
                    px = current_x + px
                    py = current_y
                elif cmd.command == "V":
                    px = current_x
                    py = current_y + py
                else:
                    px = current_x + px
                    py = current_y + py
            else:
                if cmd.command == "H":
                    py = current_y
                elif cmd.command == "V":
                    px = current_x

            current_x, current_y = px, py

            if cmd.command == "M" and not vertices:
                start_x, start_y = px, py

            # Normalize to 0-1 range
            norm_x = (px - vb_x) / vb_w
            norm_y = (py - vb_y) / vb_h

            if flip_y:
                norm_y = 1.0 - norm_y

            # Clamp to valid range
            norm_x = max(0.0, min(1.0, norm_x))
            norm_y = max(0.0, min(1.0, norm_y))

            vertices.append((round(norm_x, 4), round(norm_y, 4)))

    return vertices


def paths_to_recipe(
    paths: list[SVGPath],
    viewbox: tuple[float, float, float, float],
    shape_id: str,
    display_name: str,
    description: str = "",
    category: str = "custom",
    flip_y: bool = True,
) -> dict[str, Any]:
    """Convert parsed SVG paths to recipe JSON format.

    Args:
        paths: List of SVGPath objects
        viewbox: SVG viewBox for normalization
        shape_id: Unique identifier for the shape
        display_name: Human-readable name
        description: Shape description
        category: Shape category
        flip_y: Whether to flip Y coordinates

    Returns:
        Recipe dictionary ready for JSON serialization
    """
    # Calculate aspect ratio from viewbox
    _, _, vb_w, vb_h = viewbox
    aspect_ratio = round(vb_w / vb_h, 2)

    # Build regions from paths
    regions: dict[str, Any] = {}
    all_vertices: list[tuple[float, float]] = []

    for path in paths:
        vertices = commands_to_vertices(path.commands, viewbox, flip_y)
        if len(vertices) < 3:
            continue

        all_vertices.extend(vertices)

        # Calculate label position (centroid)
        cx = sum(v[0] for v in vertices) / len(vertices)
        cy = sum(v[1] for v in vertices) / len(vertices)

        region_id = path.id.lower().replace("-", "_").replace(" ", "_")
        display_label = path.label or path.id.replace("_", " ").replace("-", " ").title()

        regions[region_id] = {
            "display_name": display_label,
            "path": {
                "type": "polygon",
                "vertices": [{"x": v[0], "y": v[1]} for v in vertices],
            },
            "label_position": {"x": round(cx, 4), "y": round(cy, 4)},
            "z_order": len(regions),
            "groups": path.groups,
        }

    # Build outline from all vertices (convex hull approximation)
    # For simplicity, use the first path as outline or combine all
    outline_vertices = all_vertices if all_vertices else [(0, 0), (1, 0), (1, 1), (0, 1)]

    recipe = {
        "schema_version": "1.0",
        "shape_id": shape_id,
        "display_name": display_name,
        "description": description,
        "metadata": {
            "category": category,
            "aspect_ratio": aspect_ratio,
            "source": "svg_conversion",
        },
        "outline": {
            "type": "polygon",
            "vertices": [{"x": v[0], "y": v[1]} for v in outline_vertices[:100]],  # Limit points
        },
        "regions": regions,
    }

    return recipe


def preview_recipe(recipe: dict[str, Any]) -> None:
    """Show a matplotlib preview of the recipe.

    Args:
        recipe: Recipe dictionary
    """
    try:
        import matplotlib.patches as mpatches
        import matplotlib.pyplot as plt
        from matplotlib.path import Path
    except ImportError:
        print("matplotlib not available for preview")
        return

    fig, ax = plt.subplots(figsize=(8, 10))

    # Draw regions
    colors = plt.cm.tab20.colors
    for i, (region_id, region) in enumerate(recipe.get("regions", {}).items()):
        path_data = region["path"]
        if path_data["type"] == "polygon":
            vertices = [(v["x"], v["y"]) for v in path_data["vertices"]]
            if vertices:
                vertices.append(vertices[0])  # Close the polygon
                codes = [Path.MOVETO] + [Path.LINETO] * (len(vertices) - 2) + [Path.CLOSEPOLY]
                path = Path(vertices, codes)
                patch = mpatches.PathPatch(
                    path,
                    facecolor=colors[i % len(colors)],
                    edgecolor="black",
                    linewidth=1,
                    alpha=0.6,
                )
                ax.add_patch(patch)

                # Add label
                label_pos = region.get("label_position", {})
                lx = label_pos.get("x", 0.5)
                ly = label_pos.get("y", 0.5)
                ax.text(lx, ly, region_id, ha="center", va="center", fontsize=7)

    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_aspect("equal")
    ax.set_title(f"{recipe.get('display_name', 'Preview')}\n{len(recipe.get('regions', {}))} regions")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert SVG files to MediPlot recipe JSON format"
    )
    parser.add_argument("input", type=Path, help="Input SVG file")
    parser.add_argument("output", type=Path, help="Output JSON file")
    parser.add_argument("--shape-id", required=True, help="Unique shape identifier")
    parser.add_argument("--display-name", help="Human-readable name (default: from shape-id)")
    parser.add_argument("--description", default="", help="Shape description")
    parser.add_argument("--category", default="custom", help="Shape category")
    parser.add_argument("--no-flip-y", action="store_true", help="Don't flip Y axis")
    parser.add_argument("--preview", action="store_true", help="Show preview before saving")

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}")
        return 1

    display_name = args.display_name or args.shape_id.replace("_", " ").title()

    print(f"Parsing SVG: {args.input}")
    paths, viewbox = parse_svg_file(args.input)
    print(f"Found {len(paths)} paths, viewBox: {viewbox}")

    print("Converting to recipe format...")
    recipe = paths_to_recipe(
        paths,
        viewbox,
        shape_id=args.shape_id,
        display_name=display_name,
        description=args.description,
        category=args.category,
        flip_y=not args.no_flip_y,
    )
    print(f"Created {len(recipe['regions'])} regions")

    if args.preview:
        print("Showing preview...")
        preview_recipe(recipe)

    print(f"Writing to: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(recipe, f, indent=2)

    print("Done!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
