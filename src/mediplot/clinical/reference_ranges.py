"""Reference ranges for common clinical lab values."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReferenceRange:
    """Reference range for a lab value.

    Attributes:
        name: Display name for the test
        unit: Unit of measurement
        low: Lower limit of normal
        high: Upper limit of normal
        critical_low: Critical low value (if applicable)
        critical_high: Critical high value (if applicable)
    """

    name: str
    unit: str
    low: float
    high: float
    critical_low: float | None = None
    critical_high: float | None = None

    def is_normal(self, value: float) -> bool:
        """Check if a value is within normal range."""
        return self.low <= value <= self.high

    def is_critical(self, value: float) -> bool:
        """Check if a value is in the critical range."""
        if self.critical_low is not None and value < self.critical_low:
            return True
        return bool(self.critical_high is not None and value > self.critical_high)

    def status(self, value: float) -> str:
        """Get status string for a value."""
        if self.is_critical(value):
            return "critical"
        if value < self.low:
            return "low"
        if value > self.high:
            return "high"
        return "normal"


# Common lab reference ranges (adult values)
REFERENCE_RANGES: dict[str, ReferenceRange] = {
    # Complete Blood Count (CBC)
    "wbc": ReferenceRange("WBC", "x10^9/L", 4.5, 11.0, 2.0, 30.0),
    "rbc": ReferenceRange("RBC", "x10^12/L", 4.5, 5.5),
    "hemoglobin": ReferenceRange("Hemoglobin", "g/dL", 12.0, 17.5, 7.0, 20.0),
    "hematocrit": ReferenceRange("Hematocrit", "%", 36.0, 50.0),
    "platelets": ReferenceRange("Platelets", "x10^9/L", 150.0, 400.0, 50.0, 1000.0),
    "mcv": ReferenceRange("MCV", "fL", 80.0, 100.0),
    "mch": ReferenceRange("MCH", "pg", 27.0, 33.0),
    "mchc": ReferenceRange("MCHC", "g/dL", 32.0, 36.0),
    # Basic Metabolic Panel (BMP)
    "glucose": ReferenceRange("Glucose", "mg/dL", 70.0, 100.0, 40.0, 500.0),
    "bun": ReferenceRange("BUN", "mg/dL", 7.0, 20.0),
    "creatinine": ReferenceRange("Creatinine", "mg/dL", 0.7, 1.3),
    "sodium": ReferenceRange("Sodium", "mEq/L", 136.0, 145.0, 120.0, 160.0),
    "potassium": ReferenceRange("Potassium", "mEq/L", 3.5, 5.0, 2.5, 6.5),
    "chloride": ReferenceRange("Chloride", "mEq/L", 98.0, 106.0),
    "co2": ReferenceRange("CO2", "mEq/L", 23.0, 29.0),
    "calcium": ReferenceRange("Calcium", "mg/dL", 8.5, 10.5, 6.0, 13.0),
    # Liver Function Tests (LFT)
    "alt": ReferenceRange("ALT", "U/L", 7.0, 56.0),
    "ast": ReferenceRange("AST", "U/L", 10.0, 40.0),
    "alp": ReferenceRange("ALP", "U/L", 44.0, 147.0),
    "bilirubin_total": ReferenceRange("Total Bilirubin", "mg/dL", 0.1, 1.2),
    "bilirubin_direct": ReferenceRange("Direct Bilirubin", "mg/dL", 0.0, 0.3),
    "albumin": ReferenceRange("Albumin", "g/dL", 3.5, 5.0),
    "total_protein": ReferenceRange("Total Protein", "g/dL", 6.0, 8.3),
    # Lipid Panel
    "cholesterol_total": ReferenceRange("Total Cholesterol", "mg/dL", 0.0, 200.0),
    "ldl": ReferenceRange("LDL", "mg/dL", 0.0, 100.0),
    "hdl": ReferenceRange("HDL", "mg/dL", 40.0, 200.0),
    "triglycerides": ReferenceRange("Triglycerides", "mg/dL", 0.0, 150.0),
    # Thyroid
    "tsh": ReferenceRange("TSH", "mIU/L", 0.4, 4.0),
    "t4_free": ReferenceRange("Free T4", "ng/dL", 0.8, 1.8),
    "t3_free": ReferenceRange("Free T3", "pg/mL", 2.3, 4.2),
    # Coagulation
    "pt": ReferenceRange("PT", "seconds", 11.0, 13.5),
    "inr": ReferenceRange("INR", "", 0.8, 1.2),
    "ptt": ReferenceRange("PTT", "seconds", 25.0, 35.0),
    # Cardiac
    "troponin": ReferenceRange("Troponin I", "ng/mL", 0.0, 0.04, None, 0.4),
    "bnp": ReferenceRange("BNP", "pg/mL", 0.0, 100.0),
    # Inflammatory
    "crp": ReferenceRange("CRP", "mg/L", 0.0, 3.0),
    "esr": ReferenceRange("ESR", "mm/hr", 0.0, 20.0),
    # Renal
    "gfr": ReferenceRange("eGFR", "mL/min/1.73m2", 90.0, 120.0),
}


# Lab panel groupings
LAB_PANELS: dict[str, list[str]] = {
    "cbc": ["wbc", "rbc", "hemoglobin", "hematocrit", "platelets", "mcv", "mch", "mchc"],
    "bmp": ["glucose", "bun", "creatinine", "sodium", "potassium", "chloride", "co2", "calcium"],
    "cmp": [
        "glucose",
        "bun",
        "creatinine",
        "sodium",
        "potassium",
        "chloride",
        "co2",
        "calcium",
        "alt",
        "ast",
        "alp",
        "bilirubin_total",
        "albumin",
        "total_protein",
    ],
    "lft": ["alt", "ast", "alp", "bilirubin_total", "bilirubin_direct", "albumin", "total_protein"],
    "lipid": ["cholesterol_total", "ldl", "hdl", "triglycerides"],
    "thyroid": ["tsh", "t4_free", "t3_free"],
    "coag": ["pt", "inr", "ptt"],
    "cardiac": ["troponin", "bnp"],
}


def get_reference_range(test_name: str) -> ReferenceRange:
    """Get reference range for a test.

    Args:
        test_name: Test identifier (lowercase)

    Returns:
        ReferenceRange object

    Raises:
        KeyError: If test not found
    """
    test_lower = test_name.lower().replace(" ", "_")
    if test_lower not in REFERENCE_RANGES:
        available = ", ".join(sorted(REFERENCE_RANGES.keys())[:10])
        msg = f"Unknown test: {test_name}. Available: {available}..."
        raise KeyError(msg)
    return REFERENCE_RANGES[test_lower]


def get_panel_tests(panel_name: str) -> list[str]:
    """Get tests in a panel.

    Args:
        panel_name: Panel identifier

    Returns:
        List of test identifiers
    """
    panel_lower = panel_name.lower()
    if panel_lower not in LAB_PANELS:
        available = ", ".join(sorted(LAB_PANELS.keys()))
        msg = f"Unknown panel: {panel_name}. Available: {available}"
        raise KeyError(msg)
    return LAB_PANELS[panel_lower]
