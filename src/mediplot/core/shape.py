"""Shape and region definitions for anatomical visualizations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import matplotlib.patches as mpatches
import matplotlib.path as mpath
import numpy as np

if TYPE_CHECKING:
    from mediplot.core.types import Color, PathType, Point


def _bezier_to_vertices(points: list[Point]) -> tuple[list[int], list[Point]]:
    """Convert cubic Bezier control points to matplotlib path codes and vertices.

    Args:
        points: List of 4 points [start, control1, control2, end]

    Returns:
        Tuple of (codes, vertices) for matplotlib Path
    """
    if len(points) != 4:
        msg = f"Cubic Bezier requires 4 points, got {len(points)}"
        raise ValueError(msg)

    return (
        [mpath.Path.MOVETO, mpath.Path.CURVE4, mpath.Path.CURVE4, mpath.Path.CURVE4],
        list(points),
    )


def _polygon_to_vertices(vertices: list[Point]) -> tuple[list[int], list[Point]]:
    """Convert polygon vertices to matplotlib path codes and vertices.

    Args:
        vertices: List of polygon vertices

    Returns:
        Tuple of (codes, vertices) for matplotlib Path
    """
    if len(vertices) < 3:
        msg = f"Polygon requires at least 3 vertices, got {len(vertices)}"
        raise ValueError(msg)

    codes = [mpath.Path.MOVETO] + [mpath.Path.LINETO] * (len(vertices) - 1)
    return codes, list(vertices)


def _ellipse_to_vertices(
    center: Point,
    rx: float,
    ry: float,
    num_points: int = 64,
) -> tuple[list[int], list[Point]]:
    """Convert ellipse parameters to matplotlib path codes and vertices.

    Args:
        center: Center point (x, y)
        rx: Radius in x direction
        ry: Radius in y direction
        num_points: Number of points to approximate the ellipse

    Returns:
        Tuple of (codes, vertices) for matplotlib Path
    """
    theta = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    x = center[0] + rx * np.cos(theta)
    y = center[1] + ry * np.sin(theta)
    vertices = list(zip(x, y, strict=False))
    codes = [mpath.Path.MOVETO] + [mpath.Path.LINETO] * (num_points - 1)
    return codes, vertices


def _arc_to_vertices(
    center: Point,
    radius: float,
    start_angle: float,
    end_angle: float,
    num_points: int = 32,
) -> tuple[list[int], list[Point]]:
    """Convert arc parameters to matplotlib path codes and vertices.

    Args:
        center: Center point (x, y)
        radius: Arc radius
        start_angle: Start angle in degrees
        end_angle: End angle in degrees
        num_points: Number of points to approximate the arc

    Returns:
        Tuple of (codes, vertices) for matplotlib Path
    """
    theta = np.linspace(
        np.radians(start_angle),
        np.radians(end_angle),
        num_points,
    )
    x = center[0] + radius * np.cos(theta)
    y = center[1] + radius * np.sin(theta)
    vertices = list(zip(x, y, strict=False))
    codes = [mpath.Path.MOVETO] + [mpath.Path.LINETO] * (num_points - 1)
    return codes, vertices


@dataclass(frozen=True, slots=True)
class PathSegment:
    """A single path segment (line, curve, arc, etc.)."""

    type: PathType
    data: dict[str, Any]

    def to_mpl_codes_vertices(self) -> tuple[list[int], list[Point]]:
        """Convert this segment to matplotlib path codes and vertices.

        Returns:
            Tuple of (codes, vertices) for constructing matplotlib Path
        """
        if self.type == "polygon":
            return _polygon_to_vertices(self.data["vertices"])
        elif self.type == "bezier":
            return _bezier_to_vertices(self.data["points"])
        elif self.type == "ellipse":
            return _ellipse_to_vertices(
                self.data["center"],
                self.data["rx"],
                self.data["ry"],
            )
        elif self.type == "arc":
            return _arc_to_vertices(
                self.data["center"],
                self.data["radius"],
                self.data["start_angle"],
                self.data["end_angle"],
            )
        else:
            msg = f"Unsupported path type: {self.type}"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class ShapePath:
    """A complete path made of one or more segments."""

    segments: tuple[PathSegment, ...]
    closed: bool = True

    def to_matplotlib_path(self) -> mpath.Path:
        """Convert to a matplotlib Path object.

        Returns:
            matplotlib.path.Path object
        """
        all_vertices: list[Point] = []
        all_codes: list[int] = []

        for i, segment in enumerate(self.segments):
            codes, vertices = segment.to_mpl_codes_vertices()

            # For subsequent segments, skip MOVETO if we're continuing a path
            if i > 0 and codes and codes[0] == mpath.Path.MOVETO:
                codes = [mpath.Path.LINETO] + codes[1:]

            all_codes.extend(codes)
            all_vertices.extend(vertices)

        if self.closed and all_vertices:
            all_codes.append(mpath.Path.CLOSEPOLY)
            all_vertices.append(all_vertices[0])

        return mpath.Path(all_vertices, all_codes)

    def to_patch(self, **kwargs: Any) -> mpatches.PathPatch:
        """Convert to a matplotlib PathPatch.

        Args:
            **kwargs: Arguments passed to PathPatch constructor

        Returns:
            matplotlib.patches.PathPatch object
        """
        return mpatches.PathPatch(self.to_matplotlib_path(), **kwargs)


@dataclass(frozen=True, slots=True)
class Region:
    """A named region within a shape."""

    id: str
    display_name: str
    path: ShapePath
    label_position: Point
    anatomical_name: str | None = None
    z_order: int = 0
    groups: frozenset[str] = field(default_factory=frozenset)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_patch(
        self,
        facecolor: Color = "none",
        edgecolor: Color = "black",
        linewidth: float = 1.0,
        alpha: float = 1.0,
        **kwargs: Any,
    ) -> mpatches.PathPatch:
        """Create a matplotlib patch for this region.

        Args:
            facecolor: Fill color
            edgecolor: Edge/outline color
            linewidth: Width of the outline
            alpha: Transparency (0-1)
            **kwargs: Additional arguments passed to PathPatch

        Returns:
            matplotlib.patches.PathPatch object
        """
        return self.path.to_patch(
            facecolor=facecolor,
            edgecolor=edgecolor,
            linewidth=linewidth,
            alpha=alpha,
            zorder=self.z_order,
            **kwargs,
        )


@dataclass(frozen=True, slots=True)
class Shape:
    """A complete anatomical shape with named regions."""

    id: str
    display_name: str
    description: str
    outline: ShapePath
    regions: dict[str, Region]
    metadata: dict[str, Any]
    aspect_ratio: float

    def get_region(self, region_id: str) -> Region:
        """Get a region by ID.

        Args:
            region_id: The region identifier

        Returns:
            The Region object

        Raises:
            KeyError: If region not found
        """
        if region_id not in self.regions:
            available = ", ".join(sorted(self.regions.keys()))
            msg = f"Region '{region_id}' not found. Available: {available}"
            raise KeyError(msg)
        return self.regions[region_id]

    def get_regions_by_group(self, group: str) -> list[Region]:
        """Get all regions belonging to a group.

        Args:
            group: The group name to filter by

        Returns:
            List of regions in the specified group
        """
        return [r for r in self.regions.values() if group in r.groups]

    def list_regions(self) -> list[str]:
        """List all available region IDs.

        Returns:
            Sorted list of region identifiers
        """
        return sorted(self.regions.keys())

    def list_groups(self) -> list[str]:
        """List all available groups.

        Returns:
            Sorted list of unique group names
        """
        groups: set[str] = set()
        for region in self.regions.values():
            groups.update(region.groups)
        return sorted(groups)
