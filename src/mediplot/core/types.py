"""Type definitions for MediPlot."""

from __future__ import annotations

from typing import Literal, TypeAlias

# A 2D point as (x, y) tuple
Point: TypeAlias = tuple[float, float]

# Color can be a named color string, RGB tuple, or RGBA tuple
Color: TypeAlias = str | tuple[float, float, float] | tuple[float, float, float, float]

# Supported path types for shape definitions
PathType: TypeAlias = Literal[
    "polygon",
    "bezier",
    "bezier_closed",
    "ellipse",
    "arc",
    "composite",
]
