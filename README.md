# MediPlot

A matplotlib-based Python library for anatomical visualizations and medical data mapping.

Create beautiful visualizations using detailed anatomical shapes and templates for medical data, research, and educational purposes.

![Multi-anatomy Example](docs/images/multi_organ_example.png)

## Features

- **216 Anatomical Shapes**: Comprehensive atlas-based shapes for brain, head/neck, liver, and abdomen
- **6 View Angles**: Each anatomical structure available in anterior, posterior, lateral (left/right), superior, and inferior views
- **Detailed Regions**: Anatomically accurate regions with proper naming (gyri, sulci, muscles, vessels, etc.)
- **Medical Colormaps**: Purpose-built colormaps for clinical data visualization
- **Clinical Charts**: Lab panels, vital signs, and patient timelines
- Built on matplotlib for seamless integration with existing workflows
- Fully typed for excellent IDE support
- Python 3.11+ support

## Installation

```bash
pip install mediplot
```

For development:

```bash
pip install mediplot[dev]
```

## Quick Start

### Brain Atlas - Frontal Lobes

```python
import mediplot as mp

brain = mp.OrganMap("brain_frontal_anterior")
brain.fill_dict(
    {
        "left_frontal_pole": 0.9,
        "right_frontal_pole": 0.85,
        "left_superior_frontal_gyrus": 0.7,
        "right_superior_frontal_gyrus": 0.75,
        "left_precentral_gyrus": 0.6,
        "right_precentral_gyrus": 0.65,
    },
    cmap="viridis",
    colorbar_label="Activation Level",
)
brain.save("brain_frontal.png")
```

![Brain Atlas Example](docs/images/brain_atlas_example.png)

### Head & Neck Skeleton

```python
import mediplot as mp

skeleton = mp.OrganMap("head_neck_skeleton_anterior")
skeleton.fill_dict(
    {
        "skull": 0.8,
        "mandible": 0.7,
        "atlas": 0.6,
        "axis": 0.6,
        "cervical3": 0.5,
        "cervical4": 0.5,
        "hyoid": 0.3,
        "sternum": 0.2,
    },
    cmap="bone",
    colorbar_label="Bone Density",
)
skeleton.save("skeleton.png")
```

![Head Neck Skeleton Example](docs/images/head_neck_skeleton_example.png)

### Head & Neck Muscles

```python
import mediplot as mp

muscles = mp.OrganMap("head_neck_muscles_anterior")
muscles.fill_dict(
    {
        "left_temporalis_muscle": 0.8,
        "right_temporalis_muscle": 0.75,
        "left_masseter_muscle": 0.7,
        "right_masseter_muscle": 0.65,
        "left_sternocleidomastoideus_muscle": 0.6,
        "right_sternocleidomastoideus_muscle": 0.55,
    },
    cmap="Reds",
    colorbar_label="Muscle Tension",
)
muscles.save("muscles.png")
```

![Head Neck Muscles Example](docs/images/head_neck_muscles_example.png)

### Liver Segments

```python
import mediplot as mp

liver = mp.OrganMap("liver_segments_anterior")
liver.fill_dict(
    {
        "liver_segment_i": 0.3,
        "liver_segment_ii": 0.5,
        "liver_segment_iii": 0.6,
        "liver_segment_v": 0.8,
        "liver_segment_vi": 0.75,
        "liver_segment_vii": 0.9,
        "liver_segment_viii": 0.85,
    },
    cmap="YlOrRd",
    colorbar_label="Function Score",
)
liver.save("liver.png")
```

![Liver Segments Example](docs/images/liver_segments_example.png)

### Abdomen GI Tract

```python
import mediplot as mp

abdomen = mp.OrganMap("abdomen_gi_tract_anterior")
abdomen.fill_dict(
    {
        "liver": 0.8,
        "stomach_and_duodenum": 0.6,
        "pancreas": 0.5,
        "gallbladder": 0.7,
        "colon_and_ileum": 0.4,
    },
    cmap="RdYlGn",
    colorbar_label="Health Index",
)
abdomen.save("abdomen.png")
```

![Abdomen Example](docs/images/abdomen_example.png)

## Side-by-Side Comparisons

```python
import matplotlib.pyplot as plt
import mediplot as mp

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# Brain Frontal Lobes
brain = mp.OrganMap("brain_frontal_anterior", ax=axes[0])
brain.fill_dict({"left_frontal_pole": 0.9, "right_frontal_pole": 0.85}, show_colorbar=False)
axes[0].set_title("Brain Frontal Lobes")

# Liver Segments
liver = mp.OrganMap("liver_segments_anterior", ax=axes[1])
liver.fill_dict({"liver_segment_ii": 0.9, "liver_segment_vii": 0.5}, show_colorbar=False)
axes[1].set_title("Liver Segments")

# Abdomen
abdomen = mp.OrganMap("abdomen_gi_tract_anterior", ax=axes[2])
abdomen.fill_dict({"liver": 0.8, "stomach_and_duodenum": 0.6}, show_colorbar=False)
axes[2].set_title("Abdomen GI Tract")

plt.tight_layout()
plt.savefig("comparison.png")
```

## Clinical Visualizations

### Lab Panel

```python
import mediplot as mp

panel = mp.LabPanel("Complete Blood Count")
panel.add_result(mp.LabResult("WBC", 7.5, "K/uL", 4.5, 11.0))
panel.add_result(mp.LabResult("RBC", 4.8, "M/uL", 4.0, 5.5))
panel.add_result(mp.LabResult("Hemoglobin", 14.2, "g/dL", 12.0, 16.0))
panel.plot()
```

### Patient Timeline

```python
import mediplot as mp
from datetime import datetime

timeline = mp.PatientTimeline("Patient Journey")
timeline.add_event(mp.TimelineEvent(datetime(2024, 1, 15), "Admission", "admission"))
timeline.add_event(mp.TimelineEvent(datetime(2024, 1, 16), "Surgery", "procedure"))
timeline.add_event(mp.TimelineEvent(datetime(2024, 1, 20), "Discharge", "discharge"))
timeline.plot()
```

## Available Shapes

MediPlot includes 216 anatomical recipes organized by category:

| Category | Shapes | Description |
|----------|--------|-------------|
| `brain_atlas` | 78 | Frontal, parietal, temporal, occipital lobes, cerebellum, brainstem, thalamus, hypothalamus, basal ganglia, limbic system, insula, ventricles (6 views each) |
| `abdomen` | 66 | Organs, GI tract, urogenital system, arteries, veins, spine, ribs, muscles (6 views each) |
| `head_neck` | 48 | Skeleton, muscles, arteries, veins, vessels, glands, cartilage (6 views each) |
| `liver` | 24 | Liver segments (I-VIII) and vasculature (6 views each) |

### Exploring Available Shapes

```python
import mediplot as mp

# List all available categories
print(mp.list_categories())
# ['abdomen', 'brain_atlas', 'head_neck', 'liver']

# List shapes in a category
print(mp.list_shapes("brain_atlas"))
# ['brain_frontal_anterior', 'brain_frontal_posterior', 'brain_frontal_lateral_left', ...]

# Get a shape and explore its regions
shape = mp.get_shape("liver_segments_anterior")
print(list(shape.regions.keys()))
# ['liver_segment_i', 'liver_segment_ii', 'liver_segment_iii', ...]

# Use any shape with OrganMap
custom = mp.OrganMap("head_neck_arteries_lateral_left")
custom.fill_dict({...})
```

## Medical Colormaps

```python
import mediplot as mp

# Available medical colormaps
colormaps = [
    "pain",         # Green -> Red (no pain -> severe)
    "inflammation", # White -> Deep red
    "perfusion",    # Blue -> Red
    "oxygenation",  # Blue -> Red (deoxygenated -> oxygenated)
    "temperature",  # Cold blue -> Fever red
    "severity",     # 5-level categorical
]

# Use with any visualization
organ = mp.OrganMap("brain_frontal_anterior")
organ.fill_dict({"left_frontal_pole": 0.7}, cmap="perfusion")
```

## License

This project is licensed under the [Polyform Noncommercial License 1.0.0](LICENSE).

**Free for:**
- Personal use
- Academic research
- Educational purposes
- Non-profit organizations

**Commercial use** requires a separate license. Contact thomaskon90@gmail.com for commercial licensing inquiries.

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/MuteJester/MediPlot.git
cd MediPlot

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Linting
ruff check src/

# Type checking
mypy src/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Thomas Konstantinovsky - thomaskon90@gmail.com

## Links

- [GitHub Repository](https://github.com/MuteJester/MediPlot)
- [Issue Tracker](https://github.com/MuteJester/MediPlot/issues)
