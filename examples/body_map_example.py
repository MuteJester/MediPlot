"""Example: Body map visualizations with MediPlot."""

import mediplot as mp

# Example 1: Simple body map with values
print("Creating body map with regional values...")
bm = mp.body_map(
    regions=["head", "torso", "left_thigh", "right_thigh", "left_forearm"],
    values=[0.9, 0.5, 0.3, 0.4, 0.7],
    cmap="coolwarm",
    colorbar_label="Intensity",
)
bm.save("body_map_values.png")
print("Saved to body_map_values.png")

# Example 2: Object-oriented approach with method chaining
print("\nCreating body map with highlights and labels...")
body = mp.BodyMap(view="anterior")
body.fill(
    regions=["head", "neck", "torso"],
    values=[0.8, 0.6, 0.4],
    cmap="viridis",
)
body.highlight(["left_hand", "right_hand"], color="red", alpha=0.6)
body.label(["head", "torso", "left_hand", "right_hand"])
body.save("body_map_highlighted.png")
print("Saved to body_map_highlighted.png")

# Example 3: Posterior view (back pain mapping)
print("\nCreating posterior body map (back pain example)...")
back = mp.BodyMap(view="posterior")
back.fill_dict(
    {
        "upper_back": 0.3,
        "lower_back": 0.9,
        "gluteal": 0.6,
        "left_hamstring": 0.4,
        "right_hamstring": 0.2,
    },
    cmap="pain",
    colorbar_label="Pain Level",
)
back.save("back_pain_map.png")
print("Saved to back_pain_map.png")

# Example 4: List available regions
print("\nAvailable regions in anterior view:")
bm_info = mp.BodyMap()
for region in bm_info.list_regions():
    print(f"  - {region}")

print("\nAvailable groups:")
for group in bm_info.list_groups():
    regions_in_group = bm_info.get_regions_by_group(group)
    print(f"  {group}: {regions_in_group}")

print("\nDone!")
