"""Example: Organ map visualizations with MediPlot."""

import matplotlib.pyplot as plt

import mediplot as mp

# Example 1: Heart with chamber perfusion data
print("Creating heart perfusion map...")
heart = mp.HeartMap()
heart.fill_dict(
    {
        "left_atrium": 0.85,
        "right_atrium": 0.78,
        "left_ventricle": 0.92,
        "right_ventricle": 0.65,
    },
    cmap="perfusion",
    colorbar_label="Perfusion Index",
)
heart.label()
heart.save("heart_perfusion.png")
print("Saved to heart_perfusion.png")

# Example 2: Brain with lobe activation
print("\nCreating brain activation map...")
brain = mp.BrainMap()
brain.fill_dict(
    {
        "frontal_lobe": 0.9,
        "parietal_lobe": 0.6,
        "temporal_lobe": 0.4,
        "occipital_lobe": 0.3,
        "cerebellum": 0.5,
    },
    cmap="coolwarm",
    colorbar_label="Activation Level",
)
brain.save("brain_activation.png")
print("Saved to brain_activation.png")

# Example 3: Lungs with ventilation data
print("\nCreating lung ventilation map...")
lungs = mp.LungsMap()
lungs.fill_dict(
    {
        "right_upper_lobe": 0.95,
        "right_middle_lobe": 0.88,
        "right_lower_lobe": 0.72,
        "left_upper_lobe": 0.91,
        "left_lower_lobe": 0.68,
    },
    cmap="oxygenation",
    colorbar_label="Ventilation %",
)
lungs.save("lung_ventilation.png")
print("Saved to lung_ventilation.png")

# Example 4: Side-by-side comparison using subplots
print("\nCreating multi-organ comparison...")
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Heart
heart2 = mp.OrganMap("heart", ax=axes[0])
heart2.fill_dict(
    {"left_ventricle": 0.7, "right_ventricle": 0.5},
    show_colorbar=False,
)
axes[0].set_title("Heart")

# Brain
brain2 = mp.OrganMap("brain", ax=axes[1])
brain2.fill_dict(
    {"frontal_lobe": 0.8, "temporal_lobe": 0.6},
    show_colorbar=False,
)
axes[1].set_title("Brain")

# Lungs
lungs2 = mp.OrganMap("lungs", ax=axes[2])
lungs2.fill_dict(
    {"left_upper_lobe": 0.9, "right_lower_lobe": 0.4},
    show_colorbar=False,
)
axes[2].set_title("Lungs")

plt.tight_layout()
plt.savefig("organ_comparison.png", dpi=150)
print("Saved to organ_comparison.png")

# List available shapes
print("\nAvailable organ shapes:")
for shape_id in mp.list_shapes("organs"):
    print(f"  - {shape_id}")

print("\nDone!")
