"""High-level API for body mapping visualizations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt

from mediplot.core.canvas import AnatomicalCanvas
from mediplot.recipes import get_shape

if TYPE_CHECKING:
    from collections.abc import Sequence

    import matplotlib.axes as maxes
    import matplotlib.figure as mfigure

    from mediplot.core.shape import Shape


class BodyMap:
    """High-level API for body mapping visualizations.

    Creates anatomical body maps where regions can be filled with colors
    based on numeric values or highlighted individually.

    Example:
        >>> bm = BodyMap(view="anterior")
        >>> bm.fill(["head", "torso"], [0.8, 0.5], cmap="coolwarm")
        >>> bm.label(["head", "torso"])
        >>> bm.show()
    """

    # Class-level view constants
    ANTERIOR = "human_anterior"
    POSTERIOR = "human_posterior"

    def __init__(
        self,
        view: str = ANTERIOR,
        ax: maxes.Axes | None = None,
        figsize: tuple[float, float] | None = None,
        show_outline: bool = True,
    ) -> None:
        """Create a new body map.

        Args:
            view: Which body view to use (use class constants or shape ID)
            ax: Optional matplotlib axes to draw on
            figsize: Optional figure size (width, height)
            show_outline: Whether to draw the body outline
        """
        self._shape = get_shape(view)
        self._canvas = AnatomicalCanvas(
            self._shape,
            ax=ax,
            figsize=figsize,
            show_outline=show_outline,
        )

    @classmethod
    def from_shape(
        cls,
        shape: Shape,
        ax: maxes.Axes | None = None,
        figsize: tuple[float, float] | None = None,
        show_outline: bool = True,
    ) -> BodyMap:
        """Create a BodyMap from a custom Shape object.

        Args:
            shape: Custom Shape object
            ax: Optional matplotlib axes
            figsize: Optional figure size
            show_outline: Whether to draw outline

        Returns:
            New BodyMap instance
        """
        instance = cls.__new__(cls)
        instance._shape = shape
        instance._canvas = AnatomicalCanvas(
            shape,
            ax=ax,
            figsize=figsize,
            show_outline=show_outline,
        )
        return instance

    def fill(
        self,
        regions: Sequence[str],
        values: Sequence[float],
        cmap: str = "coolwarm",
        vmin: float | None = None,
        vmax: float | None = None,
        alpha: float = 1.0,
        show_colorbar: bool = True,
        colorbar_label: str = "",
        **kwargs: Any,
    ) -> BodyMap:
        """Fill body regions with values mapped to a colormap.

        Args:
            regions: List of region names to fill
            values: List of values (same length as regions)
            cmap: Colormap name
            vmin: Minimum value for normalization
            vmax: Maximum value for normalization
            alpha: Transparency (0-1)
            show_colorbar: Whether to show colorbar
            colorbar_label: Label for the colorbar
            **kwargs: Additional arguments passed to canvas

        Returns:
            Self for method chaining

        Raises:
            ValueError: If regions and values have different lengths
        """
        if len(regions) != len(values):
            msg = f"Length mismatch: {len(regions)} regions, {len(values)} values"
            raise ValueError(msg)

        value_dict = dict(zip(regions, values, strict=False))
        self._canvas.fill_regions(
            value_dict,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            alpha=alpha,
            show_colorbar=show_colorbar,
            colorbar_label=colorbar_label,
            **kwargs,
        )
        return self

    def fill_dict(
        self,
        values: dict[str, float],
        cmap: str = "coolwarm",
        **kwargs: Any,
    ) -> BodyMap:
        """Fill body regions using a dictionary of values.

        Args:
            values: Dictionary mapping region names to values
            cmap: Colormap name
            **kwargs: Additional arguments passed to fill_regions

        Returns:
            Self for method chaining
        """
        self._canvas.fill_regions(values, cmap=cmap, **kwargs)
        return self

    def highlight(
        self,
        regions: Sequence[str],
        color: str = "red",
        alpha: float = 0.5,
        **kwargs: Any,
    ) -> BodyMap:
        """Highlight specific regions with a single color.

        Args:
            regions: List of region names to highlight
            color: Highlight color
            alpha: Transparency (0-1)
            **kwargs: Additional arguments

        Returns:
            Self for method chaining
        """
        self._canvas.highlight_regions(list(regions), color=color, alpha=alpha, **kwargs)
        return self

    def label(
        self,
        regions: Sequence[str] | None = None,
        fontsize: int = 8,
        color: str = "black",
        **kwargs: Any,
    ) -> BodyMap:
        """Add labels to regions.

        Args:
            regions: Specific regions to label (None = all filled regions)
            fontsize: Font size for labels
            color: Label text color
            **kwargs: Additional text arguments

        Returns:
            Self for method chaining
        """
        region_list = list(regions) if regions is not None else None
        self._canvas.add_labels(region_list, fontsize=fontsize, color=color, **kwargs)
        return self

    def clear(self) -> BodyMap:
        """Clear all filled regions.

        Returns:
            Self for method chaining
        """
        self._canvas.clear_regions()
        return self

    def list_regions(self) -> list[str]:
        """List all available region names.

        Returns:
            Sorted list of region identifiers
        """
        return self._shape.list_regions()

    def list_groups(self) -> list[str]:
        """List all available region groups.

        Returns:
            Sorted list of group names
        """
        return self._shape.list_groups()

    def get_regions_by_group(self, group: str) -> list[str]:
        """Get all region IDs belonging to a group.

        Args:
            group: The group name

        Returns:
            List of region IDs in the group
        """
        return [r.id for r in self._shape.get_regions_by_group(group)]

    @property
    def figure(self) -> mfigure.Figure | None:
        """Get the matplotlib Figure."""
        return self._canvas.figure

    @property
    def ax(self) -> maxes.Axes:
        """Get the matplotlib Axes."""
        return self._canvas.axes

    @property
    def shape(self) -> Shape:
        """Get the underlying Shape object."""
        return self._shape

    def save(self, path: str, **kwargs: Any) -> BodyMap:
        """Save the figure to a file.

        Args:
            path: Output file path
            **kwargs: Arguments passed to savefig

        Returns:
            Self for method chaining
        """
        self._canvas.save(path, **kwargs)
        return self

    def show(self) -> None:
        """Display the figure."""
        plt.show()


def body_map(
    regions: Sequence[str],
    values: Sequence[float],
    view: str = BodyMap.ANTERIOR,
    cmap: str = "coolwarm",
    show_labels: bool = False,
    figsize: tuple[float, float] | None = None,
    **kwargs: Any,
) -> BodyMap:
    """Create a filled body map in one call.

    Convenience function for quickly creating body map visualizations.

    Args:
        regions: List of region names
        values: List of values
        view: Body view to use
        cmap: Colormap name
        show_labels: Whether to show region labels
        figsize: Figure size
        **kwargs: Additional arguments for fill()

    Returns:
        Configured BodyMap instance

    Example:
        >>> import mediplot as mp
        >>> mp.body_map(
        ...     regions=["head", "torso", "left_arm"],
        ...     values=[0.8, 0.5, 0.3],
        ...     cmap="viridis",
        ... ).show()
    """
    bm = BodyMap(view=view, figsize=figsize)
    bm.fill(regions, values, cmap=cmap, **kwargs)
    if show_labels:
        bm.label(list(regions))
    return bm
