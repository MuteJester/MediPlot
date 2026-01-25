#!/usr/bin/env python3
"""Convert VTK 3D models to MediPlot 2D recipe files.

This tool projects 3D anatomical models to 2D views and extracts
simplified polygonal boundaries for use in MediPlot recipes.

Usage:
    python vtk_to_recipe.py /path/to/atlas/folder --view anterior
    python vtk_to_recipe.py /path/to/atlas/folder --view lateral
    python vtk_to_recipe.py /path/to/atlas/folder --preview  # Show 3D first
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import numpy as np


def parse_atlas_structure(atlas_path: Path) -> dict[str, Any]:
    """Parse atlasStructure.json to get structure metadata.

    Returns dict mapping structure IDs to their metadata (name, color, vtk file, groups).
    """
    json_path = atlas_path / "atlasStructure.json"
    if not json_path.exists():
        raise FileNotFoundError(f"No atlasStructure.json found at {json_path}")

    with open(json_path) as f:
        data = json.load(f)

    structures = {}
    data_sources = {}
    groups = {}

    # First pass: collect data sources and groups
    for item in data:
        item_type = item.get("@type", "")
        item_id = item.get("@id", "")

        if item_type == "DataSource":
            source = item.get("source", "")
            data_sources[item_id] = source
        elif item_type == "Group":
            name = item.get("annotation", {}).get("name", "")
            members = item.get("member", [])
            color = item.get("renderOption", {}).get("color", "")
            groups[item_id] = {
                "name": name,
                "members": members,
                "color": color,
            }

    # Second pass: collect structures
    for item in data:
        item_type = item.get("@type", "")
        item_id = item.get("@id", "")

        if item_type == "Structure":
            name = item.get("annotation", {}).get("name", "")
            color = item.get("renderOption", {}).get("color", "")

            # Find the VTK file from sourceSelector
            vtk_file = None
            for selector in item.get("sourceSelector", []):
                if "GeometrySelector" in selector.get("@type", []):
                    ds_id = selector.get("dataSource", "")
                    if ds_id in data_sources:
                        vtk_file = data_sources[ds_id]
                        break

            # Find which groups this structure belongs to
            member_groups = []
            for group_id, group_info in groups.items():
                if item_id in group_info["members"]:
                    member_groups.append(group_info["name"])

            structures[item_id] = {
                "name": name,
                "color": color,
                "vtk_file": vtk_file,
                "groups": member_groups,
            }

    return {
        "structures": structures,
        "groups": groups,
    }


def parse_rgb_color(color_str: str) -> tuple[int, int, int] | None:
    """Parse 'rgb(r,g,b)' string to tuple."""
    match = re.match(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)", color_str)
    if match:
        return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
    return None


def load_vtk_mesh(vtk_path: Path):
    """Load a VTK mesh file using PyVista."""
    import pyvista as pv
    return pv.read(str(vtk_path))


def project_mesh_to_2d(
    mesh,
    view: str = "anterior",
    simplify_tolerance: float = 0.01,
) -> np.ndarray:
    """Project 3D mesh to 2D coordinates.

    Args:
        mesh: PyVista mesh object
        view: 'anterior', 'posterior', 'lateral_left', 'lateral_right', 'superior', 'inferior'
        simplify_tolerance: Tolerance for point simplification

    Returns:
        Array of 2D points representing the projected outline
    """
    points = mesh.points

    if view in ("anterior", "posterior"):
        # Project to XZ plane (looking from Y axis)
        x = points[:, 0]  # left-right
        y = points[:, 2]  # up-down (Z becomes Y in 2D)
        if view == "posterior":
            x = -x  # Flip for posterior view
    elif view in ("lateral_left", "lateral_right"):
        # Project to YZ plane (looking from X axis)
        x = points[:, 1]  # front-back
        y = points[:, 2]  # up-down
        if view == "lateral_right":
            x = -x  # Flip for right lateral
    elif view in ("superior", "inferior"):
        # Project to XY plane (looking from Z axis - top/bottom)
        x = points[:, 0]  # left-right
        y = points[:, 1]  # front-back
        if view == "inferior":
            y = -y  # Flip for inferior (bottom) view
    else:
        raise ValueError(f"Unknown view: {view}")

    return np.column_stack([x, y])


def compute_convex_hull(points_2d: np.ndarray) -> np.ndarray:
    """Compute convex hull of 2D points."""
    from scipy.spatial import ConvexHull

    if len(points_2d) < 3:
        return points_2d

    try:
        hull = ConvexHull(points_2d)
        hull_points = points_2d[hull.vertices]
        return hull_points
    except Exception:
        return points_2d


def compute_alpha_shape(points_2d: np.ndarray, alpha: float = 0.5) -> np.ndarray:
    """Compute alpha shape (concave hull) of 2D points.

    Alpha shape provides better boundary approximation than convex hull
    for complex anatomical shapes.
    """
    from scipy.spatial import Delaunay

    if len(points_2d) < 3:
        return points_2d

    try:
        tri = Delaunay(points_2d)

        # Find edges on the boundary
        edges = set()
        edge_count = {}

        for simplex in tri.simplices:
            for i in range(3):
                edge = tuple(sorted([simplex[i], simplex[(i + 1) % 3]]))
                edge_count[edge] = edge_count.get(edge, 0) + 1

        # Boundary edges appear only once
        boundary_edges = [e for e, c in edge_count.items() if c == 1]

        if not boundary_edges:
            return compute_convex_hull(points_2d)

        # Build ordered boundary
        boundary_points = []
        current_edge = boundary_edges[0]
        boundary_points.append(current_edge[0])
        used_edges = {current_edge}

        while len(boundary_points) < len(boundary_edges):
            current_point = boundary_points[-1]
            found = False
            for edge in boundary_edges:
                if edge in used_edges:
                    continue
                if current_point in edge:
                    next_point = edge[1] if edge[0] == current_point else edge[0]
                    boundary_points.append(next_point)
                    used_edges.add(edge)
                    found = True
                    break
            if not found:
                break

        return points_2d[boundary_points]
    except Exception:
        return compute_convex_hull(points_2d)


def simplify_polygon(points: np.ndarray, tolerance: float = 0.02, max_points: int = 30) -> np.ndarray:
    """Simplify polygon using Ramer-Douglas-Peucker algorithm.

    Iteratively increases tolerance until max_points is reached.
    """
    if len(points) < 3:
        return points

    def rdp(points, epsilon):
        """Recursive Ramer-Douglas-Peucker."""
        if len(points) < 3:
            return points

        # Find point with maximum distance
        start, end = points[0], points[-1]
        line_vec = end - start
        line_len = np.linalg.norm(line_vec)

        if line_len < 1e-10:
            return np.array([start, end])

        line_unit = line_vec / line_len

        max_dist = 0
        max_idx = 0

        for i in range(1, len(points) - 1):
            point_vec = points[i] - start
            proj_len = np.dot(point_vec, line_unit)
            proj_point = start + proj_len * line_unit
            dist = np.linalg.norm(points[i] - proj_point)

            if dist > max_dist:
                max_dist = dist
                max_idx = i

        if max_dist > epsilon:
            left = rdp(points[:max_idx + 1], epsilon)
            right = rdp(points[max_idx:], epsilon)
            return np.vstack([left[:-1], right])
        else:
            return np.array([start, end])

    # Iteratively simplify until we reach max_points
    result = rdp(points, tolerance)
    current_tolerance = tolerance

    while len(result) > max_points and current_tolerance < 1.0:
        current_tolerance *= 1.5
        result = rdp(points, current_tolerance)

    return result


def normalize_coordinates(
    points: np.ndarray,
    global_bounds: tuple[float, float, float, float] | None = None,
) -> np.ndarray:
    """Normalize coordinates to 0-1 range.

    Args:
        points: 2D points array
        global_bounds: Optional (xmin, xmax, ymin, ymax) for consistent scaling

    Returns:
        Normalized points
    """
    if global_bounds:
        xmin, xmax, ymin, ymax = global_bounds
    else:
        xmin, xmax = points[:, 0].min(), points[:, 0].max()
        ymin, ymax = points[:, 1].min(), points[:, 1].max()

    # Add small padding
    x_range = xmax - xmin
    y_range = ymax - ymin

    if x_range < 1e-10:
        x_range = 1.0
    if y_range < 1e-10:
        y_range = 1.0

    # Use max range to maintain aspect ratio
    max_range = max(x_range, y_range)

    # Center and normalize
    x_center = (xmin + xmax) / 2
    y_center = (ymin + ymax) / 2

    normalized = np.zeros_like(points)
    normalized[:, 0] = 0.5 + (points[:, 0] - x_center) / max_range * 0.9
    normalized[:, 1] = 0.5 + (points[:, 1] - y_center) / max_range * 0.9

    return normalized


def compute_global_bounds(meshes: list, view: str) -> tuple[float, float, float, float]:
    """Compute global bounding box for all meshes in a view."""
    all_points = []

    for mesh in meshes:
        points_2d = project_mesh_to_2d(mesh, view)
        all_points.append(points_2d)

    all_points = np.vstack(all_points)

    xmin, xmax = all_points[:, 0].min(), all_points[:, 0].max()
    ymin, ymax = all_points[:, 1].min(), all_points[:, 1].max()

    # Add padding
    x_pad = (xmax - xmin) * 0.05
    y_pad = (ymax - ymin) * 0.05

    return (xmin - x_pad, xmax + x_pad, ymin - y_pad, ymax + y_pad)


def vertices_to_recipe_format(points: np.ndarray) -> list[dict[str, float]]:
    """Convert numpy array to recipe vertex format."""
    return [{"x": round(float(p[0]), 3), "y": round(float(p[1]), 3)} for p in points]


def compute_label_position(points: np.ndarray) -> dict[str, float]:
    """Compute centroid for label placement."""
    centroid = points.mean(axis=0)
    return {"x": round(float(centroid[0]), 3), "y": round(float(centroid[1]), 3)}


def process_atlas_to_recipe(
    atlas_path: Path,
    view: str = "anterior",
    min_vertices: int = 6,
    max_vertices: int = 30,
    simplify_tolerance: float = 0.02,
    filter_groups: list[str] | None = None,
    custom_shape_id: str | None = None,
    custom_display_name: str | None = None,
) -> dict[str, Any]:
    """Process all VTK models in atlas to create a recipe.

    Args:
        atlas_path: Path to atlas folder containing atlasStructure.json and models/
        view: View direction ('anterior', 'posterior', 'lateral_left', 'lateral_right')
        min_vertices: Minimum vertices per region
        max_vertices: Maximum vertices per region (will simplify if more)
        simplify_tolerance: Tolerance for polygon simplification

    Returns:
        Recipe dictionary ready to save as JSON
    """
    print(f"Processing atlas from: {atlas_path}")
    print(f"View: {view}")

    # Parse atlas structure
    atlas_info = parse_atlas_structure(atlas_path)
    structures = atlas_info["structures"]

    print(f"Found {len(structures)} structures")

    # Load all meshes first to compute global bounds
    models_path = atlas_path / "models"
    meshes = {}

    for struct_id, struct_info in structures.items():
        # Filter by groups if specified
        if filter_groups:
            struct_groups = struct_info.get("groups", [])
            if not any(g in filter_groups for g in struct_groups):
                continue

        vtk_file = struct_info.get("vtk_file")
        if not vtk_file:
            continue

        vtk_path = atlas_path / vtk_file
        if not vtk_path.exists():
            print(f"  Warning: VTK file not found: {vtk_path}")
            continue

        try:
            mesh = load_vtk_mesh(vtk_path)
            meshes[struct_id] = mesh
        except Exception as e:
            print(f"  Error loading {vtk_path}: {e}")

    print(f"Loaded {len(meshes)} meshes")

    if not meshes:
        raise ValueError("No meshes could be loaded")

    # Compute global bounds for consistent scaling
    global_bounds = compute_global_bounds(list(meshes.values()), view)
    print(f"Global bounds: {global_bounds}")

    # Process each structure
    regions = {}
    all_outline_points = []

    for struct_id, mesh in meshes.items():
        struct_info = structures[struct_id]
        name = struct_info["name"]

        # Project to 2D
        points_2d = project_mesh_to_2d(mesh, view)

        # Get boundary (alpha shape or convex hull)
        try:
            boundary = compute_alpha_shape(points_2d)
        except Exception:
            boundary = compute_convex_hull(points_2d)

        if len(boundary) < 3:
            print(f"  Skipping {name}: insufficient boundary points")
            continue

        # Always simplify to target max_vertices
        boundary = simplify_polygon(boundary, simplify_tolerance, max_points=max_vertices)

        # Ensure minimum vertices
        if len(boundary) < min_vertices:
            # Use convex hull as fallback for very small shapes
            boundary = compute_convex_hull(points_2d)
            if len(boundary) > max_vertices:
                boundary = simplify_polygon(boundary, simplify_tolerance, max_points=max_vertices)

        # Normalize coordinates
        boundary_norm = normalize_coordinates(boundary, global_bounds)

        # Store for outline computation
        all_outline_points.append(boundary_norm)

        # Create region entry
        region_id = name.replace(" ", "_").lower()

        # Parse color
        color_rgb = parse_rgb_color(struct_info.get("color", ""))

        regions[region_id] = {
            "display_name": name.replace("_", " ").title(),
            "anatomical_name": name.replace("_", " ").title(),
            "path": {
                "type": "polygon",
                "vertices": vertices_to_recipe_format(boundary_norm),
            },
            "label_position": compute_label_position(boundary_norm),
            "z_order": 5,
            "groups": struct_info.get("groups", []),
        }

        if color_rgb:
            regions[region_id]["default_color"] = f"rgb({color_rgb[0]},{color_rgb[1]},{color_rgb[2]})"

        print(f"  Processed: {name} ({len(boundary_norm)} vertices)")

    # Compute overall outline from all points
    if all_outline_points:
        combined_points = np.vstack(all_outline_points)
        outline_hull = compute_convex_hull(combined_points)
        outline_vertices = vertices_to_recipe_format(outline_hull)
    else:
        outline_vertices = []

    # Build recipe
    view_name = view.replace("_", " ").title()

    # Determine shape_id and display_name
    if custom_shape_id:
        shape_id = custom_shape_id
    elif filter_groups:
        group_suffix = "_".join(g.lower() for g in filter_groups)
        shape_id = f"head_neck_{group_suffix}_{view}"
    else:
        shape_id = f"head_neck_{view}"

    if custom_display_name:
        display_name = custom_display_name
    elif filter_groups:
        group_str = ", ".join(filter_groups)
        display_name = f"Head and Neck {group_str} ({view_name} View)"
    else:
        display_name = f"Head and Neck ({view_name} View)"

    recipe = {
        "schema_version": "1.0",
        "shape_id": shape_id,
        "display_name": display_name,
        "description": f"Anatomical structures ({view_name.lower()} view)",
        "metadata": {
            "category": "anatomy",
            "aspect_ratio": 0.8,
            "anatomical_position": view,
        },
        "outline": {
            "type": "polygon",
            "vertices": outline_vertices,
        },
        "regions": regions,
    }

    return recipe


def preview_atlas_3d(atlas_path: Path):
    """Show interactive 3D preview of the atlas."""
    import pyvista as pv

    atlas_info = parse_atlas_structure(atlas_path)
    structures = atlas_info["structures"]

    plotter = pv.Plotter()
    plotter.set_background("white")

    for struct_id, struct_info in structures.items():
        vtk_file = struct_info.get("vtk_file")
        if not vtk_file:
            continue

        vtk_path = atlas_path / vtk_file
        if not vtk_path.exists():
            continue

        try:
            mesh = load_vtk_mesh(vtk_path)
            color_rgb = parse_rgb_color(struct_info.get("color", ""))
            if color_rgb:
                color = [c / 255.0 for c in color_rgb]
            else:
                color = "gray"

            plotter.add_mesh(mesh, color=color, opacity=0.7, label=struct_info["name"])
        except Exception as e:
            print(f"Error loading {vtk_path}: {e}")

    plotter.add_legend()
    plotter.show_axes()
    plotter.show()


def preview_recipe_2d(recipe: dict[str, Any]):
    """Show 2D preview of generated recipe."""
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt
    from matplotlib.path import Path as MplPath

    fig, ax = plt.subplots(figsize=(10, 12))

    colors = plt.cm.tab20.colors

    # Draw outline
    outline = recipe.get("outline", {})
    if outline.get("vertices"):
        verts = [(v["x"], v["y"]) for v in outline["vertices"]]
        verts.append(verts[0])
        codes = [MplPath.MOVETO] + [MplPath.LINETO] * (len(verts) - 2) + [MplPath.CLOSEPOLY]
        path = MplPath(verts, codes)
        patch = mpatches.PathPatch(path, facecolor="white", edgecolor="black", linewidth=2)
        ax.add_patch(patch)

    # Draw regions
    regions = recipe.get("regions", {})
    for i, (region_id, region) in enumerate(regions.items()):
        path_data = region.get("path", {})
        if path_data.get("type") == "polygon":
            verts = [(v["x"], v["y"]) for v in path_data.get("vertices", [])]
            if verts:
                verts.append(verts[0])
                codes = [MplPath.MOVETO] + [MplPath.LINETO] * (len(verts) - 2) + [MplPath.CLOSEPOLY]
                path = MplPath(verts, codes)

                # Use default color if available
                default_color = region.get("default_color")
                if default_color:
                    rgb = parse_rgb_color(default_color)
                    if rgb:
                        facecolor = [c / 255.0 for c in rgb]
                    else:
                        facecolor = colors[i % len(colors)]
                else:
                    facecolor = colors[i % len(colors)]

                patch = mpatches.PathPatch(
                    path, facecolor=facecolor, edgecolor="black",
                    linewidth=0.5, alpha=0.7, zorder=region.get("z_order", 1)
                )
                ax.add_patch(patch)

    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_aspect("equal")
    ax.set_title(f"{recipe.get('display_name', 'Recipe Preview')}\n{len(regions)} regions")
    ax.axis("off")

    plt.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Convert VTK atlas to MediPlot recipe")
    parser.add_argument("atlas_path", type=Path, help="Path to atlas folder")
    parser.add_argument("--view", choices=["anterior", "posterior", "lateral_left", "lateral_right", "superior", "inferior"],
                        default="anterior", help="Projection view (6 directions)")
    parser.add_argument("--output", "-o", type=Path, help="Output JSON file")
    parser.add_argument("--preview-3d", action="store_true", help="Show 3D preview of atlas")
    parser.add_argument("--preview-2d", action="store_true", help="Show 2D preview of recipe")
    parser.add_argument("--simplify", type=float, default=0.02, help="Simplification tolerance")
    parser.add_argument("--max-vertices", type=int, default=20, help="Max vertices per region")
    parser.add_argument("--groups", type=str, nargs="+",
                        help="Filter by group names (e.g., Bones Muscles Arteries)")
    parser.add_argument("--list-groups", action="store_true", help="List available groups and exit")
    parser.add_argument("--shape-id", type=str, help="Custom shape ID for the recipe")
    parser.add_argument("--display-name", type=str, help="Custom display name for the recipe")

    args = parser.parse_args()

    if not args.atlas_path.exists():
        print(f"Error: Atlas path not found: {args.atlas_path}")
        return 1

    if args.list_groups:
        atlas_info = parse_atlas_structure(args.atlas_path)
        print("Available groups:")
        for group_id, group_info in atlas_info["groups"].items():
            member_count = len(group_info["members"])
            print(f"  {group_info['name']}: {member_count} structures")
        return 0

    if args.preview_3d:
        preview_atlas_3d(args.atlas_path)
        return 0

    # Process atlas
    recipe = process_atlas_to_recipe(
        args.atlas_path,
        view=args.view,
        simplify_tolerance=args.simplify,
        max_vertices=args.max_vertices,
        filter_groups=args.groups,
        custom_shape_id=args.shape_id,
        custom_display_name=args.display_name,
    )

    # Save or preview
    if args.output:
        with open(args.output, "w") as f:
            json.dump(recipe, f, indent=2)
        print(f"\nSaved recipe to: {args.output}")
        print(f"  Shape ID: {recipe['shape_id']}")
        print(f"  Regions: {len(recipe['regions'])}")

    if args.preview_2d or not args.output:
        preview_recipe_2d(recipe)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
