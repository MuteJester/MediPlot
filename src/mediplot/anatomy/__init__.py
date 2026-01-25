"""Anatomical visualization modules for MediPlot."""

from __future__ import annotations

from mediplot.anatomy.body_map import BodyMap, body_map
from mediplot.anatomy.organ_map import (
    BrainMap,
    HeartMap,
    LungsMap,
    OrganMap,
)

__all__ = [
    "BodyMap",
    "BrainMap",
    "HeartMap",
    "LungsMap",
    "OrganMap",
    "body_map",
]
