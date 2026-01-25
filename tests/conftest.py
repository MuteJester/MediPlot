"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture
def sample_body_areas() -> list[str]:
    """Return a sample list of body areas for testing."""
    return ["head", "torso", "left_arm", "right_arm"]


@pytest.fixture
def sample_values() -> list[float]:
    """Return sample values corresponding to body areas."""
    return [0.8, 0.5, 0.3, 0.9]
