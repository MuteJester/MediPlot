"""
MediPlot - Anatomical visualization library for Python.

A matplotlib-based library for creating heatmaps, colormaps, and plots
using anatomical body part shapes and templates.

License: Polyform Noncommercial 1.0.0
For commercial use, contact: thomaskon90@gmail.com

Example:
    >>> import mediplot as mp
    >>> mp.body_map(
    ...     regions=["head", "torso", "left_arm"],
    ...     values=[0.8, 0.5, 0.3],
    ...     cmap="coolwarm",
    ... ).show()
"""

from __future__ import annotations

__version__ = "0.2.0"
__author__ = "Thomas Konstantinovsky"
__email__ = "thomaskon90@gmail.com"
__license__ = "Polyform-Noncommercial-1.0.0"

# Anatomy visualizations
from mediplot.anatomy import (
    BodyMap,
    BrainMap,
    HeartMap,
    LungsMap,
    OrganMap,
    body_map,
)

# Clinical visualizations
from mediplot.clinical import LabPanel, LabResult, VitalSigns

# Colormaps
from mediplot.colormaps import (
    MEDICAL_COLORMAPS,
    get_colormap,
    register_medical_colormaps,
)

# Core components
from mediplot.core import (
    Color,
    PathSegment,
    PathType,
    Point,
    Region,
    Shape,
    ShapePath,
)
from mediplot.core.canvas import AnatomicalCanvas

# Recipe system
from mediplot.recipes import (
    get_shape,
    list_categories,
    list_shapes,
    register_recipe,
    unregister_recipe,
)

# Timeline
from mediplot.timeline import PatientTimeline, TimelineEvent

__all__: list[str] = [
    # Version info
    "__version__",
    # Anatomy
    "BodyMap",
    "BrainMap",
    "HeartMap",
    "LungsMap",
    "OrganMap",
    "body_map",
    # Clinical
    "LabPanel",
    "LabResult",
    "VitalSigns",
    # Timeline
    "PatientTimeline",
    "TimelineEvent",
    # Core
    "AnatomicalCanvas",
    "Color",
    "PathSegment",
    "PathType",
    "Point",
    "Region",
    "Shape",
    "ShapePath",
    # Recipes
    "get_shape",
    "list_categories",
    "list_shapes",
    "register_recipe",
    "unregister_recipe",
    # Colormaps
    "MEDICAL_COLORMAPS",
    "get_colormap",
    "register_medical_colormaps",
]
