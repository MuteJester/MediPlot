"""Medical-specific colormaps for anatomical visualizations."""

from __future__ import annotations

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

# Medical-specific colormaps
MEDICAL_COLORMAPS: dict[str, mcolors.Colormap] = {
    # Pain scale: green (no pain) to red (severe) to purple (extreme)
    "pain": mcolors.LinearSegmentedColormap.from_list(
        "mediplot_pain",
        ["#2ECC71", "#F1C40F", "#E67E22", "#E74C3C", "#8E44AD"],
    ),
    # Inflammation: white to deep red
    "inflammation": mcolors.LinearSegmentedColormap.from_list(
        "mediplot_inflammation",
        ["#FFFFFF", "#FFCCCC", "#FF6666", "#CC0000", "#800000"],
    ),
    # Perfusion: blue (low) through green to red (high)
    "perfusion": mcolors.LinearSegmentedColormap.from_list(
        "mediplot_perfusion",
        ["#0000FF", "#00FFFF", "#00FF00", "#FFFF00", "#FF0000"],
    ),
    # Temperature: cold blue to fever red
    "temperature": mcolors.LinearSegmentedColormap.from_list(
        "mediplot_temperature",
        ["#0066CC", "#66B2FF", "#FFFFFF", "#FF9999", "#CC0000"],
    ),
    # Oxygenation: cyanotic blue to healthy pink
    "oxygenation": mcolors.LinearSegmentedColormap.from_list(
        "mediplot_oxygenation",
        ["#4169E1", "#6495ED", "#FFB6C1", "#FF69B4", "#FF1493"],
    ),
    # Muscle activity: relaxed to highly active
    "muscle_activity": mcolors.LinearSegmentedColormap.from_list(
        "mediplot_muscle_activity",
        ["#E8F5E9", "#81C784", "#FFF176", "#FF8A65", "#E53935"],
    ),
    # Binary normal/abnormal
    "binary_medical": mcolors.ListedColormap(["#2ECC71", "#E74C3C"]),
    # Severity scale (5 levels)
    "severity": mcolors.ListedColormap(
        [
            "#2ECC71",  # Normal (green)
            "#F1C40F",  # Mild (yellow)
            "#E67E22",  # Moderate (orange)
            "#E74C3C",  # Severe (red)
            "#8E44AD",  # Critical (purple)
        ]
    ),
    # Risk gradient: safe to dangerous
    "risk": mcolors.LinearSegmentedColormap.from_list(
        "mediplot_risk",
        ["#27AE60", "#F39C12", "#E74C3C"],
    ),
    # Healing progression: injured to healed
    "healing": mcolors.LinearSegmentedColormap.from_list(
        "mediplot_healing",
        ["#E74C3C", "#F39C12", "#F1C40F", "#2ECC71"],
    ),
}


_registered = False


def register_medical_colormaps() -> None:
    """Register all medical colormaps with matplotlib.

    After calling this function, colormaps can be used by name
    with the 'mediplot_' prefix (e.g., 'mediplot_pain').
    """
    global _registered
    if _registered:
        return

    import contextlib

    for name, cmap in MEDICAL_COLORMAPS.items():
        full_name = f"mediplot_{name}"
        with contextlib.suppress(ValueError):
            plt.colormaps.register(cmap, name=full_name)

    _registered = True


def get_colormap(name: str) -> mcolors.Colormap:
    """Get a colormap by name.

    Checks medical colormaps first, then falls back to matplotlib.

    Args:
        name: Colormap name (with or without 'mediplot_' prefix)

    Returns:
        Colormap object

    Example:
        >>> cmap = get_colormap("pain")  # Gets mediplot_pain
        >>> cmap = get_colormap("viridis")  # Gets matplotlib viridis
    """
    # Check if it's a medical colormap (with or without prefix)
    clean_name = name.replace("mediplot_", "")
    if clean_name in MEDICAL_COLORMAPS:
        return MEDICAL_COLORMAPS[clean_name]

    # Fall back to matplotlib
    return plt.get_cmap(name)
