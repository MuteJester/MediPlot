"""Canvas for anatomical visualizations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

if TYPE_CHECKING:
    import matplotlib.axes as maxes
    import matplotlib.colorbar as mcolorbar
    import matplotlib.figure as mfigure
    import matplotlib.text as mtext

    from mediplot.core.shape import Shape
    from mediplot.core.types import Color


class AnatomicalCanvas:
    """Canvas for rendering anatomical shapes with matplotlib."""

    def __init__(
        self,
        shape: Shape,
        ax: maxes.Axes | None = None,
        figsize: tuple[float, float] | None = None,
        show_outline: bool = True,
    ) -> None:
        """Create a new anatomical canvas.

        Args:
            shape: The Shape to render
            ax: Optional existing matplotlib axes to draw on
            figsize: Optional figure size (width, height) in inches
            show_outline: Whether to draw the shape outline
        """
        self._shape = shape
        self._region_patches: dict[str, mpatches.Patch] = {}
        self._colorbar: mcolorbar.Colorbar | None = None

        if ax is None:
            # Calculate figsize from aspect ratio if not provided
            if figsize is None:
                base_height = 8
                figsize = (base_height * shape.aspect_ratio, base_height)
            self._fig, self._ax = plt.subplots(figsize=figsize)
        else:
            self._ax = ax
            self._fig = ax.get_figure()

        self._ax.set_aspect("equal")
        self._ax.axis("off")

        if show_outline:
            self._draw_outline()

        self._ax.autoscale_view()

    def _draw_outline(self) -> None:
        """Draw the shape outline."""
        outline_patch = self._shape.outline.to_patch(
            facecolor="white",
            edgecolor="black",
            linewidth=2,
            zorder=0,
        )
        self._ax.add_patch(outline_patch)

    def fill_region(
        self,
        region_id: str,
        color: Color,
        alpha: float = 1.0,
        edgecolor: Color = "black",
        linewidth: float = 0.5,
        **kwargs: Any,
    ) -> mpatches.Patch:
        """Fill a single region with a color.

        Args:
            region_id: The region identifier
            color: Fill color
            alpha: Transparency (0-1)
            edgecolor: Edge color
            linewidth: Edge line width
            **kwargs: Additional arguments passed to patch

        Returns:
            The created matplotlib Patch
        """
        region = self._shape.get_region(region_id)

        # Remove existing patch if present
        if region_id in self._region_patches:
            self._region_patches[region_id].remove()

        patch = region.to_patch(
            facecolor=color,
            edgecolor=edgecolor,
            linewidth=linewidth,
            alpha=alpha,
            **kwargs,
        )
        self._ax.add_patch(patch)
        self._region_patches[region_id] = patch
        return patch

    def fill_regions(
        self,
        values: dict[str, float],
        cmap: str | mcolors.Colormap = "coolwarm",
        vmin: float | None = None,
        vmax: float | None = None,
        alpha: float = 1.0,
        show_colorbar: bool = True,
        colorbar_label: str = "",
        **kwargs: Any,
    ) -> dict[str, mpatches.Patch]:
        """Fill multiple regions with values mapped to a colormap.

        Args:
            values: Dictionary mapping region IDs to numeric values
            cmap: Colormap name or Colormap object
            vmin: Minimum value for colormap normalization
            vmax: Maximum value for colormap normalization
            alpha: Transparency (0-1)
            show_colorbar: Whether to display a colorbar
            colorbar_label: Label for the colorbar
            **kwargs: Additional arguments passed to fill_region

        Returns:
            Dictionary mapping region IDs to their patches
        """
        if not values:
            return {}

        if isinstance(cmap, str):
            cmap = plt.get_cmap(cmap)

        vals = list(values.values())
        vmin = vmin if vmin is not None else min(vals)
        vmax = vmax if vmax is not None else max(vals)
        norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

        patches = {}
        for region_id, value in values.items():
            color = cmap(norm(value))
            patches[region_id] = self.fill_region(
                region_id,
                color,
                alpha=alpha,
                **kwargs,
            )

        if show_colorbar and self._fig is not None:
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            self._colorbar = self._fig.colorbar(sm, ax=self._ax, label=colorbar_label)

        return patches

    def highlight_regions(
        self,
        region_ids: list[str],
        color: Color = "red",
        alpha: float = 0.5,
        **kwargs: Any,
    ) -> dict[str, mpatches.Patch]:
        """Highlight specific regions with a single color.

        Args:
            region_ids: List of region identifiers
            color: Highlight color
            alpha: Transparency (0-1)
            **kwargs: Additional arguments passed to fill_region

        Returns:
            Dictionary mapping region IDs to their patches
        """
        patches = {}
        for region_id in region_ids:
            patches[region_id] = self.fill_region(
                region_id,
                color=color,
                alpha=alpha,
                **kwargs,
            )
        return patches

    def add_labels(
        self,
        region_ids: list[str] | None = None,
        fontsize: int = 8,
        color: Color = "black",
        use_display_name: bool = True,
        **kwargs: Any,
    ) -> list[mtext.Text]:
        """Add labels to regions.

        Args:
            region_ids: Specific regions to label (None = all regions)
            fontsize: Font size for labels
            color: Label text color
            use_display_name: Use display_name (True) or id (False)
            **kwargs: Additional arguments passed to ax.text

        Returns:
            List of matplotlib Text objects
        """
        if region_ids is None:
            region_ids = list(self._shape.regions.keys())

        texts = []
        for region_id in region_ids:
            region = self._shape.get_region(region_id)
            label = region.display_name if use_display_name else region_id
            text = self._ax.text(
                region.label_position[0],
                region.label_position[1],
                label,
                ha="center",
                va="center",
                fontsize=fontsize,
                color=color,
                **kwargs,
            )
            texts.append(text)
        return texts

    def clear_regions(self) -> None:
        """Remove all filled regions from the canvas."""
        for patch in self._region_patches.values():
            patch.remove()
        self._region_patches.clear()

    @property
    def figure(self) -> mfigure.Figure | None:
        """Get the matplotlib Figure."""
        return self._fig

    @property
    def axes(self) -> maxes.Axes:
        """Get the matplotlib Axes."""
        return self._ax

    @property
    def shape(self) -> Shape:
        """Get the underlying Shape."""
        return self._shape

    def save(self, path: str, **kwargs: Any) -> None:
        """Save the figure to a file.

        Args:
            path: Output file path
            **kwargs: Arguments passed to figure.savefig
        """
        if self._fig is not None:
            kwargs.setdefault("bbox_inches", "tight")
            kwargs.setdefault("dpi", 150)
            self._fig.savefig(path, **kwargs)

    def show(self) -> None:
        """Display the figure."""
        plt.show()
