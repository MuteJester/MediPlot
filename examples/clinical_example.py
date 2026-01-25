"""Example: Clinical data visualizations with MediPlot."""

from datetime import datetime, timedelta

import mediplot as mp

# Example 1: Lab panel visualization
print("Creating lab panel visualization...")
panel = mp.LabPanel("bmp")
panel.add_results(
    {
        "glucose": 95,
        "sodium": 138,
        "potassium": 4.2,
        "chloride": 102,
        "co2": 24,
        "bun": 15,
        "creatinine": 1.1,
        "calcium": 9.5,
    }
)
panel.plot(title="Basic Metabolic Panel Results")
panel.save("lab_panel_bmp.png")
print("Saved to lab_panel_bmp.png")

# Show summary
summary = panel.summary()
print(f"\nLab Results Summary:")
print(f"  Normal: {len(summary['normal'])}")
print(f"  Abnormal: {len(summary['abnormal'])}")
print(f"  Critical: {len(summary['critical'])}")

# Example 2: Abnormal lab values
print("\nCreating panel with abnormal values...")
abnormal_panel = mp.LabPanel("bmp")
abnormal_panel.add_results(
    {
        "glucose": 250,  # High
        "sodium": 128,  # Low
        "potassium": 6.2,  # High
        "chloride": 102,
        "co2": 18,  # Low
        "bun": 45,  # High
        "creatinine": 2.8,  # High
        "calcium": 8.0,  # Slightly low
    }
)
abnormal_panel.plot(title="Abnormal BMP Results")
abnormal_panel.save("lab_panel_abnormal.png")
print("Saved to lab_panel_abnormal.png")

# Example 3: Vital signs timeline
print("\nCreating vital signs timeline...")
base_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)

vitals = mp.VitalSigns()

# Add readings over 8 hours
for i in range(9):
    t = base_time + timedelta(hours=i)
    # Simulated data with some variation
    hr = 72 + (i % 3) * 5 - 5
    sys = 120 + (i % 4) * 8 - 10
    dia = 80 + (i % 3) * 5 - 5
    rr = 16 + (i % 2) * 2
    temp = 36.8 + (i % 4) * 0.3
    spo2 = 98 - (i % 3)

    vitals.add_heart_rate(t, hr)
    vitals.add_blood_pressure(t, sys, dia)
    vitals.add_respiratory_rate(t, rr)
    vitals.add_temperature(t, temp)
    vitals.add_spo2(t, spo2)

vitals.plot(title="Patient Vital Signs - 8 Hour Trend")
vitals.save("vital_signs.png")
print("Saved to vital_signs.png")

# Example 4: Patient timeline
print("\nCreating patient timeline...")
timeline = mp.PatientTimeline()

admission_time = datetime(2024, 1, 15, 14, 30)

# Add events
timeline.add_admission(admission_time, unit="Emergency Department")
timeline.add_lab(admission_time + timedelta(hours=1), "CBC", "WBC 12.5")
timeline.add_lab(admission_time + timedelta(hours=1), "BMP", "Cr 1.8")
timeline.add_imaging(admission_time + timedelta(hours=2), "CT Chest", "Pneumonia RLL")
timeline.add_medication(
    admission_time + timedelta(hours=3),
    admission_time + timedelta(days=5),
    "Ceftriaxone",
    dose="1g",
    frequency="Daily",
)
timeline.add_medication(
    admission_time + timedelta(hours=3),
    admission_time + timedelta(days=3),
    "Azithromycin",
    dose="500mg",
    frequency="Daily",
)
timeline.add_procedure(
    admission_time + timedelta(days=1, hours=2),
    "Bronchoscopy",
    duration_minutes=45,
)
timeline.add_event(
    admission_time + timedelta(days=2),
    "Improving clinically",
    "note",
)
timeline.add_discharge(
    admission_time + timedelta(days=5, hours=10),
    disposition="Home",
)

timeline.plot(title="Hospital Course - Community Acquired Pneumonia")
timeline.save("patient_timeline.png")
print("Saved to patient_timeline.png")

print("\nDone!")
