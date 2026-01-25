"""Vital signs visualization tools."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

if TYPE_CHECKING:
    from datetime import datetime

    import matplotlib.axes as maxes
    import matplotlib.figure as mfigure


@dataclass
class VitalReading:
    """A single vital sign reading.

    Attributes:
        timestamp: When the reading was taken
        value: The vital sign value
        unit: Unit of measurement
    """

    timestamp: datetime
    value: float
    unit: str = ""


# Normal ranges for vital signs
VITAL_RANGES: dict[str, dict[str, float]] = {
    "heart_rate": {"low": 60, "high": 100, "critical_low": 40, "critical_high": 150, "unit": "bpm"},
    "systolic_bp": {"low": 90, "high": 140, "critical_low": 70, "critical_high": 180, "unit": "mmHg"},
    "diastolic_bp": {"low": 60, "high": 90, "critical_low": 40, "critical_high": 120, "unit": "mmHg"},
    "respiratory_rate": {"low": 12, "high": 20, "critical_low": 8, "critical_high": 30, "unit": "/min"},
    "temperature": {"low": 36.1, "high": 37.2, "critical_low": 35.0, "critical_high": 39.0, "unit": "°C"},
    "spo2": {"low": 95, "high": 100, "critical_low": 90, "critical_high": 100, "unit": "%"},
    "map": {"low": 70, "high": 105, "critical_low": 60, "critical_high": 110, "unit": "mmHg"},
}


class VitalSigns:
    """Visualization for vital signs over time.

    Example:
        >>> vitals = VitalSigns()
        >>> vitals.add_heart_rate(datetime.now(), 72)
        >>> vitals.add_blood_pressure(datetime.now(), 120, 80)
        >>> vitals.add_spo2(datetime.now(), 98)
        >>> vitals.plot()
        >>> plt.show()
    """

    def __init__(self, figsize: tuple[float, float] | None = None) -> None:
        """Create a new vital signs visualization.

        Args:
            figsize: Optional figure size
        """
        self._figsize = figsize or (12, 8)
        self._data: dict[str, list[VitalReading]] = {
            "heart_rate": [],
            "systolic_bp": [],
            "diastolic_bp": [],
            "respiratory_rate": [],
            "temperature": [],
            "spo2": [],
        }
        self._fig: mfigure.Figure | None = None
        self._axes: dict[str, maxes.Axes] = {}

    def add_heart_rate(self, timestamp: datetime, value: float) -> VitalSigns:
        """Add a heart rate reading.

        Args:
            timestamp: When reading was taken
            value: Heart rate in bpm

        Returns:
            Self for method chaining
        """
        self._data["heart_rate"].append(VitalReading(timestamp, value, "bpm"))
        return self

    def add_blood_pressure(
        self,
        timestamp: datetime,
        systolic: float,
        diastolic: float,
    ) -> VitalSigns:
        """Add a blood pressure reading.

        Args:
            timestamp: When reading was taken
            systolic: Systolic pressure in mmHg
            diastolic: Diastolic pressure in mmHg

        Returns:
            Self for method chaining
        """
        self._data["systolic_bp"].append(VitalReading(timestamp, systolic, "mmHg"))
        self._data["diastolic_bp"].append(VitalReading(timestamp, diastolic, "mmHg"))
        return self

    def add_respiratory_rate(self, timestamp: datetime, value: float) -> VitalSigns:
        """Add a respiratory rate reading.

        Args:
            timestamp: When reading was taken
            value: Respiratory rate per minute

        Returns:
            Self for method chaining
        """
        self._data["respiratory_rate"].append(VitalReading(timestamp, value, "/min"))
        return self

    def add_temperature(self, timestamp: datetime, value: float) -> VitalSigns:
        """Add a temperature reading.

        Args:
            timestamp: When reading was taken
            value: Temperature in Celsius

        Returns:
            Self for method chaining
        """
        self._data["temperature"].append(VitalReading(timestamp, value, "°C"))
        return self

    def add_spo2(self, timestamp: datetime, value: float) -> VitalSigns:
        """Add an SpO2 reading.

        Args:
            timestamp: When reading was taken
            value: SpO2 percentage

        Returns:
            Self for method chaining
        """
        self._data["spo2"].append(VitalReading(timestamp, value, "%"))
        return self

    def add_reading(
        self,
        vital_type: str,
        timestamp: datetime,
        value: float,
    ) -> VitalSigns:
        """Add a vital sign reading.

        Args:
            vital_type: Type of vital sign
            timestamp: When reading was taken
            value: The reading value

        Returns:
            Self for method chaining
        """
        if vital_type not in self._data:
            msg = f"Unknown vital type: {vital_type}. Available: {list(self._data.keys())}"
            raise ValueError(msg)
        unit = VITAL_RANGES.get(vital_type, {}).get("unit", "")
        self._data[vital_type].append(VitalReading(timestamp, value, unit))
        return self

    def plot(
        self,
        vitals: list[str] | None = None,
        show_normal_range: bool = True,
        show_critical_range: bool = True,
        title: str = "Vital Signs",
    ) -> VitalSigns:
        """Create the vital signs visualization.

        Args:
            vitals: List of vital types to plot (None = all with data)
            show_normal_range: Show normal range shading
            show_critical_range: Show critical thresholds
            title: Plot title

        Returns:
            Self for method chaining
        """
        # Determine which vitals to plot
        if vitals is None:
            vitals = [k for k, v in self._data.items() if v]

        # Handle blood pressure specially (combine systolic/diastolic)
        if "blood_pressure" in vitals:
            vitals.remove("blood_pressure")
            if "systolic_bp" not in vitals and self._data["systolic_bp"]:
                vitals.append("systolic_bp")
            if "diastolic_bp" not in vitals and self._data["diastolic_bp"]:
                vitals.append("diastolic_bp")

        if not vitals:
            return self

        # Create subplots
        n_plots = len(vitals)
        self._fig, axes = plt.subplots(
            n_plots,
            1,
            figsize=(self._figsize[0], self._figsize[1] * n_plots / 3),
            sharex=True,
        )

        if n_plots == 1:
            axes = [axes]

        for i, vital_type in enumerate(vitals):
            ax = axes[i]
            self._axes[vital_type] = ax
            readings = self._data[vital_type]

            if not readings:
                continue

            # Extract data
            times = [r.timestamp for r in readings]
            values = [r.value for r in readings]
            unit = readings[0].unit

            # Get range info
            range_info = VITAL_RANGES.get(vital_type, {})
            low = range_info.get("low")
            high = range_info.get("high")
            crit_low = range_info.get("critical_low")
            crit_high = range_info.get("critical_high")

            # Plot normal range
            if show_normal_range and low is not None and high is not None:
                ax.axhspan(low, high, color="green", alpha=0.1, label="Normal")

            # Plot critical thresholds
            if show_critical_range:
                if crit_low is not None:
                    ax.axhline(crit_low, color="red", linestyle="--", alpha=0.5, linewidth=1)
                if crit_high is not None:
                    ax.axhline(crit_high, color="red", linestyle="--", alpha=0.5, linewidth=1)

            # Plot the data
            ax.plot(times, values, "o-", color="navy", markersize=6, linewidth=1.5)

            # Highlight abnormal values
            for t, v in zip(times, values, strict=False):
                is_critical = (crit_low is not None and v < crit_low) or (
                    crit_high is not None and v > crit_high
                )
                is_abnormal = (
                    (low is not None and v < low) or (high is not None and v > high)
                ) and not is_critical

                if is_critical:
                    ax.plot(t, v, "o", color="red", markersize=10, zorder=5)
                elif is_abnormal:
                    ax.plot(t, v, "o", color="orange", markersize=8, zorder=5)

            # Format
            display_name = vital_type.replace("_", " ").title()
            if vital_type == "systolic_bp":
                display_name = "Systolic BP"
            elif vital_type == "diastolic_bp":
                display_name = "Diastolic BP"
            elif vital_type == "spo2":
                display_name = "SpO2"

            ax.set_ylabel(f"{display_name}\n({unit})")
            ax.grid(True, alpha=0.3)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

        # Format x-axis
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%m/%d"))
        axes[-1].set_xlabel("Time")

        # Title
        self._fig.suptitle(title, fontsize=14, fontweight="bold")
        plt.tight_layout()

        return self

    def plot_combined_bp(
        self,
        ax: maxes.Axes | None = None,
        show_normal_range: bool = True,
    ) -> VitalSigns:
        """Plot blood pressure with systolic and diastolic together.

        Args:
            ax: Optional axes to plot on
            show_normal_range: Show normal range shading

        Returns:
            Self for method chaining
        """
        if not self._data["systolic_bp"] or not self._data["diastolic_bp"]:
            return self

        if ax is None:
            self._fig, ax = plt.subplots(figsize=(10, 5))

        sys_times = [r.timestamp for r in self._data["systolic_bp"]]
        sys_values = [r.value for r in self._data["systolic_bp"]]
        dia_times = [r.timestamp for r in self._data["diastolic_bp"]]
        dia_values = [r.value for r in self._data["diastolic_bp"]]

        # Normal ranges
        if show_normal_range:
            ax.axhspan(90, 140, color="green", alpha=0.1, label="Normal Systolic")
            ax.axhspan(60, 90, color="blue", alpha=0.1, label="Normal Diastolic")

        # Plot with fill between
        ax.plot(sys_times, sys_values, "o-", color="red", label="Systolic", markersize=6)
        ax.plot(dia_times, dia_values, "o-", color="blue", label="Diastolic", markersize=6)

        # Fill between if timestamps match
        if sys_times == dia_times:
            ax.fill_between(sys_times, sys_values, dia_values, alpha=0.2, color="purple")

        ax.set_ylabel("Blood Pressure (mmHg)")
        ax.set_xlabel("Time")
        ax.legend(loc="upper right")
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%m/%d"))

        return self

    @property
    def figure(self) -> mfigure.Figure | None:
        """Get the matplotlib Figure."""
        return self._fig

    @property
    def data(self) -> dict[str, list[VitalReading]]:
        """Get all vital sign data."""
        return {k: v.copy() for k, v in self._data.items()}

    def save(self, path: str, **kwargs: Any) -> VitalSigns:
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
