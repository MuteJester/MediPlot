"""Parser for shape recipe JSON files."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mediplot.core.shape import PathSegment, Region, Shape, ShapePath

if TYPE_CHECKING:
    from mediplot.core.types import Point


def parse_recipe(data: dict[str, Any]) -> Shape:
    """Parse a recipe dictionary into a Shape object.

    Args:
        data: Recipe dictionary loaded from JSON

    Returns:
        Shape object

    Raises:
        ValueError: If schema version is unsupported or data is invalid
    """
    schema_version = data.get("schema_version", "1.0")
    if schema_version != "1.0":
        msg = f"Unsupported schema version: {schema_version}"
        raise ValueError(msg)

    metadata = data.get("metadata", {})

    return Shape(
        id=data["shape_id"],
        display_name=data["display_name"],
        description=data.get("description", ""),
        outline=_parse_path(data["outline"]),
        regions=_parse_regions(data.get("regions", {})),
        metadata=metadata,
        aspect_ratio=metadata.get("aspect_ratio", 1.0),
    )


def _parse_regions(regions_data: dict[str, Any]) -> dict[str, Region]:
    """Parse region definitions from recipe data.

    Args:
        regions_data: Dictionary of region definitions

    Returns:
        Dictionary mapping region IDs to Region objects
    """
    regions = {}
    for region_id, region_data in regions_data.items():
        label_pos = region_data["label_position"]
        label_position: Point = (label_pos["x"], label_pos["y"])

        groups_list = region_data.get("groups", [])

        regions[region_id] = Region(
            id=region_id,
            display_name=region_data["display_name"],
            anatomical_name=region_data.get("anatomical_name"),
            path=_parse_path(region_data["path"]),
            label_position=label_position,
            z_order=region_data.get("z_order", 0),
            groups=frozenset(groups_list),
            metadata=region_data.get("metadata", {}),
        )
    return regions


def _parse_path(path_data: dict[str, Any]) -> ShapePath:
    """Parse a path definition from recipe data.

    Args:
        path_data: Path definition dictionary

    Returns:
        ShapePath object

    Raises:
        ValueError: If path type is unknown
    """
    path_type = path_data["type"]

    if path_type == "polygon":
        return _parse_polygon(path_data)
    elif path_type == "ellipse":
        return _parse_ellipse(path_data)
    elif path_type == "bezier":
        return _parse_bezier(path_data)
    elif path_type == "bezier_closed":
        return _parse_bezier_closed(path_data)
    elif path_type == "arc":
        return _parse_arc(path_data)
    elif path_type == "composite":
        return _parse_composite(path_data)
    else:
        msg = f"Unknown path type: {path_type}"
        raise ValueError(msg)


def _parse_polygon(data: dict[str, Any]) -> ShapePath:
    """Parse a polygon path definition."""
    vertices: list[Point] = [(v["x"], v["y"]) for v in data["vertices"]]
    segment = PathSegment(type="polygon", data={"vertices": vertices})
    return ShapePath(segments=(segment,), closed=True)


def _parse_ellipse(data: dict[str, Any]) -> ShapePath:
    """Parse an ellipse path definition."""
    center: Point = (data["center"]["x"], data["center"]["y"])
    segment = PathSegment(
        type="ellipse",
        data={
            "center": center,
            "rx": data["rx"],
            "ry": data["ry"],
        },
    )
    return ShapePath(segments=(segment,), closed=True)


def _parse_bezier(data: dict[str, Any]) -> ShapePath:
    """Parse a single Bezier curve definition."""
    points: list[Point] = [(p["x"], p["y"]) for p in data["points"]]
    segment = PathSegment(type="bezier", data={"points": points})
    return ShapePath(segments=(segment,), closed=False)


def _parse_bezier_closed(data: dict[str, Any]) -> ShapePath:
    """Parse multiple Bezier curves forming a closed shape."""
    segments = []
    for curve in data["curves"]:
        points: list[Point] = [
            (curve["start"]["x"], curve["start"]["y"]),
            (curve["control1"]["x"], curve["control1"]["y"]),
            (curve["control2"]["x"], curve["control2"]["y"]),
            (curve["end"]["x"], curve["end"]["y"]),
        ]
        segment = PathSegment(type="bezier", data={"points": points})
        segments.append(segment)
    return ShapePath(segments=tuple(segments), closed=True)


def _parse_arc(data: dict[str, Any]) -> ShapePath:
    """Parse an arc path definition."""
    center: Point = (data["center"]["x"], data["center"]["y"])
    segment = PathSegment(
        type="arc",
        data={
            "center": center,
            "radius": data["radius"],
            "start_angle": data["start_angle"],
            "end_angle": data["end_angle"],
        },
    )
    return ShapePath(segments=(segment,), closed=False)


def _parse_composite(data: dict[str, Any]) -> ShapePath:
    """Parse a composite path made of multiple path types."""
    segments = []
    for path_part in data["paths"]:
        sub_path = _parse_path(path_part)
        segments.extend(sub_path.segments)
    return ShapePath(segments=tuple(segments), closed=data.get("closed", True))
