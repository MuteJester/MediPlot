"""Organ-specific visualization maps."""

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


class OrganMap:
    """High-level API for organ visualizations.

    Creates anatomical organ maps where regions (chambers, lobes, segments)
    can be filled with colors based on numeric values.

    Example:
        >>> heart = OrganMap("heart")
        >>> heart.fill_dict({
        ...     "left_ventricle": 0.8,
        ...     "right_ventricle": 0.6,
        ... }, cmap="perfusion")
        >>> heart.show()
    """

    # Convenience constants for common organs
    HEART = "heart"
    BRAIN = "brain"
    LUNGS = "lungs"

    def __init__(
        self,
        organ: str,
        ax: maxes.Axes | None = None,
        figsize: tuple[float, float] | None = None,
        show_outline: bool = True,
    ) -> None:
        """Create a new organ map.

        Args:
            organ: Organ identifier (use class constants or shape ID)
            ax: Optional matplotlib axes to draw on
            figsize: Optional figure size (width, height)
            show_outline: Whether to draw the organ outline
        """
        self._shape = get_shape(organ)
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
    ) -> OrganMap:
        """Create an OrganMap from a custom Shape object.

        Args:
            shape: Custom Shape object
            ax: Optional matplotlib axes
            figsize: Optional figure size
            show_outline: Whether to draw outline

        Returns:
            New OrganMap instance
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
    ) -> OrganMap:
        """Fill organ regions with values mapped to a colormap.

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
    ) -> OrganMap:
        """Fill organ regions using a dictionary of values.

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
    ) -> OrganMap:
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
    ) -> OrganMap:
        """Add labels to regions.

        Args:
            regions: Specific regions to label (None = all regions)
            fontsize: Font size for labels
            color: Label text color
            **kwargs: Additional text arguments

        Returns:
            Self for method chaining
        """
        region_list = list(regions) if regions is not None else None
        self._canvas.add_labels(region_list, fontsize=fontsize, color=color, **kwargs)
        return self

    def clear(self) -> OrganMap:
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

    def save(self, path: str, **kwargs: Any) -> OrganMap:
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


# Convenience classes for specific organs
class HeartMap(OrganMap):
    """Specialized map for heart visualization.

    Example:
        >>> heart = HeartMap()
        >>> heart.fill_dict({
        ...     "left_ventricle": 0.9,
        ...     "right_ventricle": 0.7,
        ... })
    """

    def __init__(
        self,
        ax: maxes.Axes | None = None,
        figsize: tuple[float, float] | None = None,
    ) -> None:
        super().__init__(OrganMap.HEART, ax=ax, figsize=figsize)


class BrainMap(OrganMap):
    """Specialized map for brain visualization.

    Example:
        >>> brain = BrainMap()
        >>> brain.fill_dict({
        ...     "frontal_lobe": 0.8,
        ...     "temporal_lobe": 0.5,
        ... })
    """

    def __init__(
        self,
        ax: maxes.Axes | None = None,
        figsize: tuple[float, float] | None = None,
    ) -> None:
        super().__init__(OrganMap.BRAIN, ax=ax, figsize=figsize)


class LungsMap(OrganMap):
    """Specialized map for lungs visualization.

    Example:
        >>> lungs = LungsMap()
        >>> lungs.fill_dict({
        ...     "left_upper_lobe": 0.9,
        ...     "right_lower_lobe": 0.6,
        ... })
    """

    def __init__(
        self,
        ax: maxes.Axes | None = None,
        figsize: tuple[float, float] | None = None,
    ) -> None:
        super().__init__(OrganMap.LUNGS, ax=ax, figsize=figsize)
