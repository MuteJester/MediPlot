"""Lab value visualization tools."""

from __future__ import annotations

import contextlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

from mediplot.clinical.reference_ranges import (
    ReferenceRange,
    get_panel_tests,
    get_reference_range,
)

if TYPE_CHECKING:
    from datetime import datetime

    import matplotlib.axes as maxes
    import matplotlib.figure as mfigure


@dataclass
class LabResult:
    """A single lab result.

    Attributes:
        test: Test identifier
        value: Numeric result value
        unit: Unit of measurement (optional, uses reference if not provided)
        timestamp: When the test was performed
        reference: Reference range (auto-populated if not provided)
    """

    test: str
    value: float
    unit: str | None = None
    timestamp: datetime | None = None
    reference: ReferenceRange | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Auto-populate reference range if not provided."""
        if self.reference is None:
            try:
                self.reference = get_reference_range(self.test)
                if self.unit is None:
                    self.unit = self.reference.unit
            except KeyError:
                pass

    @property
    def status(self) -> str:
        """Get status (normal, low, high, critical)."""
        if self.reference is None:
            return "unknown"
        return self.reference.status(self.value)

    @property
    def is_normal(self) -> bool:
        """Check if value is within normal range."""
        if self.reference is None:
            return True
        return self.reference.is_normal(self.value)

    @property
    def is_critical(self) -> bool:
        """Check if value is in critical range."""
        if self.reference is None:
            return False
        return self.reference.is_critical(self.value)


class LabPanel:
    """Visualization for a panel of lab results.

    Example:
        >>> panel = LabPanel("bmp")
        >>> panel.add_result("glucose", 95)
        >>> panel.add_result("sodium", 142)
        >>> panel.add_result("potassium", 4.2)
        >>> panel.plot()
        >>> plt.show()
    """

    def __init__(
        self,
        panel_name: str | None = None,
        figsize: tuple[float, float] | None = None,
    ) -> None:
        """Create a new lab panel visualization.

        Args:
            panel_name: Optional preset panel name (e.g., "cbc", "bmp", "cmp")
            figsize: Optional figure size
        """
        self._panel_name = panel_name
        self._figsize = figsize or (10, 6)
        self._results: list[LabResult] = []
        self._fig: mfigure.Figure | None = None
        self._ax: maxes.Axes | None = None

        # If panel name provided, get expected tests
        self._expected_tests: list[str] = []
        if panel_name:
            with contextlib.suppress(KeyError):
                self._expected_tests = get_panel_tests(panel_name)

    def add_result(
        self,
        test: str,
        value: float,
        unit: str | None = None,
        timestamp: datetime | None = None,
    ) -> LabPanel:
        """Add a lab result to the panel.

        Args:
            test: Test identifier
            value: Numeric result
            unit: Unit of measurement
            timestamp: When test was performed

        Returns:
            Self for method chaining
        """
        result = LabResult(test=test, value=value, unit=unit, timestamp=timestamp)
        self._results.append(result)
        return self

    def add_results(self, results: dict[str, float]) -> LabPanel:
        """Add multiple results at once.

        Args:
            results: Dictionary mapping test names to values

        Returns:
            Self for method chaining
        """
        for test, value in results.items():
            self.add_result(test, value)
        return self

    def plot(
        self,
        highlight_abnormal: bool = True,
        show_reference: bool = True,
        title: str | None = None,
        ax: maxes.Axes | None = None,
    ) -> LabPanel:
        """Create the lab panel visualization.

        Args:
            highlight_abnormal: Highlight abnormal values
            show_reference: Show reference range bars
            title: Plot title
            ax: Optional axes to plot on

        Returns:
            Self for method chaining
        """
        if not self._results:
            return self

        if ax is None:
            self._fig, self._ax = plt.subplots(figsize=self._figsize)
        else:
            self._ax = ax
            self._fig = ax.get_figure()

        # Sort results by test order (if panel) or alphabetically
        if self._expected_tests:
            results = sorted(
                self._results,
                key=lambda r: (
                    self._expected_tests.index(r.test.lower())
                    if r.test.lower() in self._expected_tests
                    else len(self._expected_tests)
                ),
            )
        else:
            results = sorted(self._results, key=lambda r: r.test)

        n_results = len(results)
        np.arange(n_results)

        # Calculate normalized positions for plotting
        for i, result in enumerate(results):
            ref = result.reference
            if ref is None:
                continue

            y = n_results - 1 - i  # Reverse order (top to bottom)

            # Draw reference range bar
            if show_reference:
                # Determine the plot range
                range_span = ref.high - ref.low
                ref.low - range_span * 0.5
                ref.high + range_span * 0.5

                # Normal range (green)
                self._ax.barh(
                    y,
                    ref.high - ref.low,
                    left=ref.low,
                    height=0.6,
                    color="#90EE90",
                    alpha=0.5,
                    edgecolor="none",
                )

                # Add range labels
                self._ax.axvline(ref.low, color="green", alpha=0.3, linewidth=0.5)
                self._ax.axvline(ref.high, color="green", alpha=0.3, linewidth=0.5)

            # Plot the actual value
            color = "black"
            marker = "o"
            markersize = 10

            if highlight_abnormal:
                if result.is_critical:
                    color = "purple"
                    marker = "X"
                    markersize = 14
                elif not result.is_normal:
                    color = "red" if result.value > ref.high else "blue"
                    marker = "^" if result.value > ref.high else "v"
                    markersize = 12

            self._ax.plot(
                result.value,
                y,
                marker=marker,
                markersize=markersize,
                color=color,
                markeredgecolor="black",
                markeredgewidth=1,
                zorder=10,
            )

            # Value label
            offset = range_span * 0.1 if ref else 0
            self._ax.annotate(
                f"{result.value:.1f}",
                (result.value + offset, y),
                fontsize=9,
                va="center",
            )

        # Y-axis labels
        labels = [f"{r.reference.name if r.reference else r.test}\n({r.unit or ''})" for r in results]
        self._ax.set_yticks(np.arange(n_results))
        self._ax.set_yticklabels(labels[::-1])  # Reverse to match plot order

        # Formatting
        self._ax.set_xlabel("Value")
        if title:
            self._ax.set_title(title)
        elif self._panel_name:
            self._ax.set_title(f"{self._panel_name.upper()} Panel Results")

        self._ax.spines["top"].set_visible(False)
        self._ax.spines["right"].set_visible(False)

        # Legend
        if highlight_abnormal:
            legend_elements = [
                mpatches.Patch(facecolor="#90EE90", alpha=0.5, label="Normal Range"),
                plt.Line2D(
                    [0],
                    [0],
                    marker="o",
                    color="w",
                    markerfacecolor="black",
                    markersize=8,
                    label="Normal",
                ),
                plt.Line2D(
                    [0],
                    [0],
                    marker="^",
                    color="w",
                    markerfacecolor="red",
                    markersize=8,
                    label="High",
                ),
                plt.Line2D(
                    [0],
                    [0],
                    marker="v",
                    color="w",
                    markerfacecolor="blue",
                    markersize=8,
                    label="Low",
                ),
                plt.Line2D(
                    [0],
                    [0],
                    marker="X",
                    color="w",
                    markerfacecolor="purple",
                    markersize=8,
                    label="Critical",
                ),
            ]
            self._ax.legend(
                handles=legend_elements,
                loc="lower right",
                fontsize=8,
            )

        plt.tight_layout()
        return self

    @property
    def figure(self) -> mfigure.Figure | None:
        """Get the matplotlib Figure."""
        return self._fig

    @property
    def ax(self) -> maxes.Axes | None:
        """Get the matplotlib Axes."""
        return self._ax

    @property
    def results(self) -> list[LabResult]:
        """Get all lab results."""
        return self._results.copy()

    def save(self, path: str, **kwargs: Any) -> LabPanel:
        """Save the figure to a file.

        Args:
            path: Output file path
            **kwargs: Arguments passed to savefig

        Returns:
            Self for method chaining
        """
        if self._fig is not None:
            kwargs.setdefault("bbox_inches", "tight")
            kwargs.setdefault("dpi", 150)
            self._fig.savefig(path, **kwargs)
        return self

    def show(self) -> None:
        """Display the figure."""
        plt.show()

    def summary(self) -> dict[str, list[LabResult]]:
        """Get summary of results by status.

        Returns:
            Dictionary with 'normal', 'abnormal', and 'critical' lists
        """
        summary: dict[str, list[LabResult]] = {
            "normal": [],
            "abnormal": [],
            "critical": [],
        }
        for result in self._results:
            if result.is_critical:
                summary["critical"].append(result)
            elif not result.is_normal:
                summary["abnormal"].append(result)
            else:
                summary["normal"].append(result)
        return summary
