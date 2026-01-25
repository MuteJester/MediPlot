"""Patient timeline visualization."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

if TYPE_CHECKING:
    import matplotlib.axes as maxes
    import matplotlib.figure as mfigure


# Category colors for different event types
CATEGORY_COLORS: dict[str, str] = {
    "admission": "#3498DB",  # Blue
    "discharge": "#2ECC71",  # Green
    "procedure": "#E74C3C",  # Red
    "medication": "#9B59B6",  # Purple
    "lab": "#F39C12",  # Orange
    "imaging": "#1ABC9C",  # Teal
    "consultation": "#E67E22",  # Dark orange
    "vital_signs": "#34495E",  # Dark gray
    "diagnosis": "#C0392B",  # Dark red
    "note": "#7F8C8D",  # Gray
    "default": "#95A5A6",  # Light gray
}


@dataclass
class TimelineEvent:
    """A single event on a patient timeline.

    Attributes:
        timestamp: When the event occurred
        title: Event title/name
        category: Event category for color coding
        description: Optional detailed description
        end_time: Optional end time for duration events
        metadata: Additional event data
    """

    timestamp: datetime
    title: str
    category: str = "default"
    description: str = ""
    end_time: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> timedelta | None:
        """Get event duration if end_time is set."""
        if self.end_time is not None:
            return self.end_time - self.timestamp
        return None

    @property
    def color(self) -> str:
        """Get the color for this event's category."""
        return CATEGORY_COLORS.get(self.category.lower(), CATEGORY_COLORS["default"])


class PatientTimeline:
    """Patient journey timeline visualization.

    Creates timeline visualizations showing events, medications,
    procedures, and other clinical activities over time.

    Example:
        >>> timeline = PatientTimeline()
        >>> timeline.add_event(datetime(2024, 1, 1, 8, 0), "Admission", "admission")
        >>> timeline.add_medication(
        ...     datetime(2024, 1, 1, 10, 0),
        ...     datetime(2024, 1, 5, 10, 0),
        ...     "Amoxicillin 500mg TID"
        ... )
        >>> timeline.add_procedure(datetime(2024, 1, 2, 14, 0), "CT Scan")
        >>> timeline.plot()
        >>> plt.show()
    """

    def __init__(self, figsize: tuple[float, float] | None = None) -> None:
        """Create a new patient timeline.

        Args:
            figsize: Optional figure size
        """
        self._figsize = figsize or (14, 8)
        self._events: list[TimelineEvent] = []
        self._fig: mfigure.Figure | None = None
        self._ax: maxes.Axes | None = None

    def add_event(
        self,
        timestamp: datetime,
        title: str,
        category: str = "default",
        description: str = "",
        end_time: datetime | None = None,
        **metadata: Any,
    ) -> PatientTimeline:
        """Add an event to the timeline.

        Args:
            timestamp: When the event occurred
            title: Event title
            category: Event category
            description: Optional description
            end_time: Optional end time for duration events
            **metadata: Additional event data

        Returns:
            Self for method chaining
        """
        event = TimelineEvent(
            timestamp=timestamp,
            title=title,
            category=category,
            description=description,
            end_time=end_time,
            metadata=dict(metadata),
        )
        self._events.append(event)
        return self

    def add_admission(
        self,
        timestamp: datetime,
        unit: str = "",
        description: str = "",
    ) -> PatientTimeline:
        """Add an admission event.

        Args:
            timestamp: Admission time
            unit: Hospital unit
            description: Additional details

        Returns:
            Self for method chaining
        """
        title = f"Admission{' to ' + unit if unit else ''}"
        return self.add_event(timestamp, title, "admission", description, unit=unit)

    def add_discharge(
        self,
        timestamp: datetime,
        disposition: str = "",
        description: str = "",
    ) -> PatientTimeline:
        """Add a discharge event.

        Args:
            timestamp: Discharge time
            disposition: Discharge disposition
            description: Additional details

        Returns:
            Self for method chaining
        """
        title = f"Discharge{' - ' + disposition if disposition else ''}"
        return self.add_event(timestamp, title, "discharge", description, disposition=disposition)

    def add_procedure(
        self,
        timestamp: datetime,
        name: str,
        description: str = "",
        duration_minutes: int | None = None,
    ) -> PatientTimeline:
        """Add a procedure event.

        Args:
            timestamp: Procedure time
            name: Procedure name
            description: Additional details
            duration_minutes: Procedure duration in minutes

        Returns:
            Self for method chaining
        """
        end_time = None
        if duration_minutes:
            end_time = timestamp + timedelta(minutes=duration_minutes)
        return self.add_event(timestamp, name, "procedure", description, end_time)

    def add_medication(
        self,
        start_time: datetime,
        end_time: datetime | None,
        name: str,
        dose: str = "",
        frequency: str = "",
    ) -> PatientTimeline:
        """Add a medication event.

        Args:
            start_time: When medication started
            end_time: When medication ended (None if ongoing)
            name: Medication name
            dose: Dosage
            frequency: Frequency (e.g., "TID", "BID")

        Returns:
            Self for method chaining
        """
        title = name
        if dose:
            title += f" {dose}"
        if frequency:
            title += f" {frequency}"
        return self.add_event(
            start_time,
            title,
            "medication",
            end_time=end_time,
            dose=dose,
            frequency=frequency,
        )

    def add_lab(
        self,
        timestamp: datetime,
        name: str,
        result: str = "",
    ) -> PatientTimeline:
        """Add a lab result event.

        Args:
            timestamp: When lab was drawn/resulted
            name: Lab name
            result: Result value

        Returns:
            Self for method chaining
        """
        title = f"{name}: {result}" if result else name
        return self.add_event(timestamp, title, "lab", result=result)

    def add_imaging(
        self,
        timestamp: datetime,
        name: str,
        findings: str = "",
    ) -> PatientTimeline:
        """Add an imaging study event.

        Args:
            timestamp: When study was performed
            name: Study name
            findings: Key findings

        Returns:
            Self for method chaining
        """
        return self.add_event(timestamp, name, "imaging", findings, findings=findings)

    def plot(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        categories: list[str] | None = None,
        show_legend: bool = True,
        title: str = "Patient Timeline",
    ) -> PatientTimeline:
        """Create the timeline visualization.

        Args:
            start_date: Start of date range (None = auto)
            end_date: End of date range (None = auto)
            categories: Categories to include (None = all)
            show_legend: Whether to show legend
            title: Plot title

        Returns:
            Self for method chaining
        """
        if not self._events:
            return self

        # Filter events
        events = self._events
        if categories:
            events = [e for e in events if e.category.lower() in [c.lower() for c in categories]]

        if start_date:
            events = [e for e in events if e.timestamp >= start_date]
        if end_date:
            events = [e for e in events if e.timestamp <= end_date]

        if not events:
            return self

        # Sort by timestamp
        events = sorted(events, key=lambda e: e.timestamp)

        # Determine time range
        if start_date is None:
            start_date = events[0].timestamp - timedelta(hours=6)
        if end_date is None:
            # Include end times if any
            max_time = max(
                e.end_time if e.end_time else e.timestamp for e in events
            )
            end_date = max_time + timedelta(hours=6)

        # Create figure
        self._fig, self._ax = plt.subplots(figsize=self._figsize)

        # Group events by category for y-positioning
        category_order = [
            "admission",
            "discharge",
            "procedure",
            "imaging",
            "medication",
            "lab",
            "consultation",
            "vital_signs",
            "diagnosis",
            "note",
            "default",
        ]
        used_categories = sorted(
            set(e.category.lower() for e in events),
            key=lambda c: category_order.index(c) if c in category_order else len(category_order),
        )

        category_y = {cat: i for i, cat in enumerate(used_categories)}
        n_categories = len(used_categories)

        # Plot events
        for event in events:
            y = category_y[event.category.lower()]
            color = event.color

            if event.end_time:
                # Duration event - draw as bar
                (event.end_time - event.timestamp).total_seconds() / 3600  # hours
                self._ax.barh(
                    y,
                    event.end_time - event.timestamp,
                    left=event.timestamp,
                    height=0.6,
                    color=color,
                    alpha=0.7,
                    edgecolor="black",
                    linewidth=0.5,
                )
                # Label at start
                self._ax.annotate(
                    event.title,
                    (event.timestamp, y),
                    xytext=(5, 0),
                    textcoords="offset points",
                    fontsize=8,
                    va="center",
                )
            else:
                # Point event - draw as marker
                self._ax.plot(
                    event.timestamp,
                    y,
                    "o",
                    color=color,
                    markersize=12,
                    markeredgecolor="black",
                    markeredgewidth=1,
                )
                # Label
                self._ax.annotate(
                    event.title,
                    (event.timestamp, y),
                    xytext=(8, 0),
                    textcoords="offset points",
                    fontsize=8,
                    va="center",
                    ha="left",
                )

        # Format y-axis
        self._ax.set_yticks(range(n_categories))
        self._ax.set_yticklabels([cat.replace("_", " ").title() for cat in used_categories])
        self._ax.set_ylim(-0.5, n_categories - 0.5)

        # Format x-axis
        self._ax.set_xlim(start_date, end_date)
        self._ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d\n%H:%M"))
        self._ax.xaxis.set_major_locator(mdates.AutoDateLocator())

        # Grid
        self._ax.grid(True, axis="x", alpha=0.3)
        self._ax.set_axisbelow(True)

        # Formatting
        self._ax.set_xlabel("Date / Time")
        self._ax.set_title(title, fontsize=14, fontweight="bold")
        self._ax.spines["top"].set_visible(False)
        self._ax.spines["right"].set_visible(False)

        # Legend
        if show_legend:
            legend_elements = [
                mpatches.Patch(
                    facecolor=CATEGORY_COLORS.get(cat, CATEGORY_COLORS["default"]),
                    edgecolor="black",
                    label=cat.replace("_", " ").title(),
                )
                for cat in used_categories
            ]
            self._ax.legend(
                handles=legend_elements,
                loc="upper left",
                bbox_to_anchor=(1.02, 1),
                fontsize=9,
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
    def events(self) -> list[TimelineEvent]:
        """Get all timeline events."""
        return self._events.copy()

    def filter_by_category(self, category: str) -> list[TimelineEvent]:
        """Get events filtered by category.

        Args:
            category: Category to filter by

        Returns:
            List of matching events
        """
        return [e for e in self._events if e.category.lower() == category.lower()]

    def filter_by_date_range(
        self,
        start: datetime,
        end: datetime,
    ) -> list[TimelineEvent]:
        """Get events within a date range.

        Args:
            start: Start of range
            end: End of range

        Returns:
            List of events in range
        """
        return [e for e in self._events if start <= e.timestamp <= end]

    def save(self, path: str, **kwargs: Any) -> PatientTimeline:
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
