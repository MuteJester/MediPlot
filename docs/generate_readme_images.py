#!/usr/bin/env python3
"""Generate example images for the README using actual MediPlot recipes."""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

import mediplot as mp

OUTPUT_DIR = Path(__file__).parent / "images"
OUTPUT_DIR.mkdir(exist_ok=True)

# View configurations for multi-panel layouts
VIEWS = ["anterior", "posterior", "lateral_left", "lateral_right"]
VIEW_TITLES = {
    "anterior": "Anterior",
    "posterior": "Posterior",
    "lateral_left": "Left Lateral",
    "lateral_right": "Right Lateral",
}


def generate_brain_atlas_example():
    """Generate brain atlas visualization - multi-view panel."""
    print("Generating brain atlas example (4 views)...")

    # fMRI activation data
    activation_data = {
        "left_frontal_pole": 0.95,
        "right_frontal_pole": 0.92,
        "left_superior_frontal_gyrus": 0.85,
        "right_superior_frontal_gyrus": 0.82,
        "left_precentral_gyrus": 0.75,
        "right_precentral_gyrus": 0.78,
        "left_paracentral_lobule": 0.65,
        "right_paracentral_lobule": 0.68,
        "left_straight_gyrus": 0.55,
        "right_straight_gyrus": 0.58,
        "left_lateral_orbital_gyrus": 0.60,
        "right_lateral_orbital_gyrus": 0.62,
        "left_central_sulcus": 0.35,
        "right_central_sulcus": 0.38,
        "left_precentral_sulcus": 0.40,
        "right_precentral_sulcus": 0.42,
        "left_superior_frontal_sulcus": 0.45,
        "right_superior_frontal_sulcus": 0.48,
        "left_inferior_frontal_sulcus": 0.30,
        "right_inferior_frontal_sulcus": 0.32,
        "left_superior_temporal_sulcus": 0.25,
    }

    fig, axes = plt.subplots(1, 4, figsize=(20, 6))
    fig.suptitle("Brain Frontal Lobes - fMRI Activation Pattern", fontsize=16, fontweight='bold')

    for idx, view in enumerate(VIEWS):
        shape_id = f"brain_frontal_{view}"
        brain = mp.OrganMap(shape_id, ax=axes[idx])
        brain.fill_dict(
            activation_data,
            cmap="plasma",
            show_colorbar=(idx == 3),  # Only show colorbar on last panel
            colorbar_label="BOLD Signal" if idx == 3 else None,
        )
        axes[idx].set_title(VIEW_TITLES[view], fontsize=12)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "brain_atlas_example.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {OUTPUT_DIR / 'brain_atlas_example.png'}")


def generate_head_neck_skeleton_example():
    """Generate head/neck skeleton - multi-view bone density scan."""
    print("Generating head/neck skeleton example (4 views)...")

    # Bone density data (T-score style)
    bone_density = {
        "skull": 0.95,
        "mandible": 0.88,
        "left_clavicle": 0.75,
        "right_clavicle": 0.78,
        "atlas": 0.70,
        "axis": 0.72,
        "cervical3": 0.68,
        "cervical4": 0.65,
        "cervical5": 0.62,
        "cervical6": 0.60,
        "cervical7": 0.58,
        "thoracic1": 0.55,
        "thoracic2": 0.52,
        "thoracic3": 0.50,
        "thoracic4": 0.48,
        "thoracic5": 0.45,
        "rib1": 0.55,
        "rib2": 0.50,
        "rib3": 0.48,
        "rib4": 0.45,
        "rib5": 0.42,
        "hyoid": 0.40,
        "sternum": 0.65,
    }

    fig, axes = plt.subplots(1, 4, figsize=(20, 6))
    fig.suptitle("Head & Neck Skeleton - Bone Mineral Density Scan", fontsize=16, fontweight='bold')

    for idx, view in enumerate(VIEWS):
        shape_id = f"head_neck_skeleton_{view}"
        skeleton = mp.OrganMap(shape_id, ax=axes[idx])
        skeleton.fill_dict(
            bone_density,
            cmap="YlOrBr",
            show_colorbar=(idx == 3),
            colorbar_label="BMD T-score" if idx == 3 else None,
        )
        axes[idx].set_title(VIEW_TITLES[view], fontsize=12)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "head_neck_skeleton_example.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {OUTPUT_DIR / 'head_neck_skeleton_example.png'}")


def generate_head_neck_muscles_example():
    """Generate head/neck muscles - multi-view EMG tension mapping."""
    print("Generating head/neck muscles example (4 views)...")

    # EMG data - bruxism and postural imbalance pattern
    emg_data = {
        "left_temporalis_muscle": 0.92,
        "right_temporalis_muscle": 0.88,
        "left_masseter_muscle": 0.95,
        "right_masseter_muscle": 0.90,
        "left_zygomatic_muscle": 0.45,
        "right_zygomatic_muscle": 0.48,
        "left_sternocleidomastoideus_muscle": 0.72,
        "right_sternocleidomastoideus_muscle": 0.55,
        "left_scalenius_muscle": 0.60,
        "right_scalenius_muscle": 0.58,
        "left_levator_scapulae_muscle": 0.68,
        "right_levator_scapulae_muscle": 0.65,
        "left_trapezius_muscle": 0.75,
        "right_trapezius_muscle": 0.70,
    }

    fig, axes = plt.subplots(1, 4, figsize=(20, 6))
    fig.suptitle("Head & Neck Muscles - EMG Tension Mapping", fontsize=16, fontweight='bold')

    for idx, view in enumerate(VIEWS):
        shape_id = f"head_neck_muscles_{view}"
        muscles = mp.OrganMap(shape_id, ax=axes[idx])
        muscles.fill_dict(
            emg_data,
            cmap="hot",
            show_colorbar=(idx == 3),
            colorbar_label="EMG (μV)" if idx == 3 else None,
        )
        axes[idx].set_title(VIEW_TITLES[view], fontsize=12)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "head_neck_muscles_example.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {OUTPUT_DIR / 'head_neck_muscles_example.png'}")


def generate_head_neck_vessels_example():
    """Generate head/neck vessels - multi-view Doppler flow mapping."""
    print("Generating head/neck vessels example (4 views)...")

    # Doppler ultrasound flow velocities
    flow_data = {
        "arch_of_aorta": 0.95,
        "brachiocephalic_trunk": 0.90,
        "left_common_carotid": 0.88,
        "right_common_carotid": 0.85,
        "left_internal_carotid": 0.82,
        "right_internal_carotid": 0.80,
        "left_external_carotid": 0.75,
        "right_external_carotid": 0.72,
        "left_subclavian_artery": 0.78,
        "right_subclavian_artery": 0.76,
        "left_vertebral_artery": 0.65,
        "right_vertebral_artery": 0.62,
        "superior_vena_cava": 0.45,
        "left_internal_jugular_vein": 0.40,
        "right_internal_jugular_vein": 0.38,
        "left_subclavian_vein": 0.35,
        "right_subclavian_vein": 0.32,
    }

    fig, axes = plt.subplots(1, 4, figsize=(20, 6))
    fig.suptitle("Head & Neck Vasculature - Doppler Flow Velocity", fontsize=16, fontweight='bold')

    for idx, view in enumerate(VIEWS):
        shape_id = f"head_neck_vessels_{view}"
        vessels = mp.OrganMap(shape_id, ax=axes[idx])
        vessels.fill_dict(
            flow_data,
            cmap="RdBu_r",
            show_colorbar=(idx == 3),
            colorbar_label="cm/s" if idx == 3 else None,
        )
        axes[idx].set_title(VIEW_TITLES[view], fontsize=12)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "head_neck_vessels_example.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {OUTPUT_DIR / 'head_neck_vessels_example.png'}")


def generate_liver_segments_example():
    """Generate liver segments - multi-view hepatic function mapping."""
    print("Generating liver segments example (4 views)...")

    # Hepatocyte function per Couinaud segment
    liver_function = {
        "liver_segment_i": 0.85,
        "liver_segment_ii": 0.78,
        "liver_segment_iii": 0.82,
        "liver_segment_iva": 0.65,
        "liver_segment_ivb": 0.60,
        "liver_segment_v": 0.55,
        "liver_segment_viii": 0.50,
        "liver_segment_vi": 0.45,
        "liver_segment_vii": 0.40,
    }

    fig, axes = plt.subplots(1, 4, figsize=(20, 6))
    fig.suptitle("Liver Couinaud Segments - Hepatocyte Function (MRI)", fontsize=16, fontweight='bold')

    for idx, view in enumerate(VIEWS):
        shape_id = f"liver_segments_{view}"
        liver = mp.OrganMap(shape_id, ax=axes[idx])
        liver.fill_dict(
            liver_function,
            cmap="RdYlGn",
            show_colorbar=(idx == 3),
            colorbar_label="Function %" if idx == 3 else None,
        )
        axes[idx].set_title(VIEW_TITLES[view], fontsize=12)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "liver_segments_example.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {OUTPUT_DIR / 'liver_segments_example.png'}")


def generate_abdomen_example():
    """Generate abdomen GI tract - multi-view organ health assessment."""
    print("Generating abdomen example (4 views)...")

    # Multi-organ health assessment
    organ_health = {
        "liver": 0.85,
        "gallbladder": 0.70,
        "stomach_and_duodenum": 0.60,
        "pancreas": 0.75,
        "colon_and_ileum": 0.55,
    }

    fig, axes = plt.subplots(1, 4, figsize=(20, 6))
    fig.suptitle("Abdominal GI Tract - Organ Health Assessment", fontsize=16, fontweight='bold')

    for idx, view in enumerate(VIEWS):
        shape_id = f"abdomen_gi_tract_{view}"
        abdomen = mp.OrganMap(shape_id, ax=axes[idx])
        abdomen.fill_dict(
            organ_health,
            cmap="RdYlGn",
            show_colorbar=(idx == 3),
            colorbar_label="Health %" if idx == 3 else None,
        )
        axes[idx].set_title(VIEW_TITLES[view], fontsize=12)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "abdomen_example.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {OUTPUT_DIR / 'abdomen_example.png'}")


def generate_multi_anatomy_example():
    """Generate grid comparison showcasing different anatomical systems across views."""
    print("Generating multi-anatomy comparison (3x4 grid)...")

    # Data for each system
    brain_data = {
        "left_frontal_pole": 0.95, "right_frontal_pole": 0.90,
        "left_superior_frontal_gyrus": 0.80, "right_superior_frontal_gyrus": 0.78,
        "left_precentral_gyrus": 0.65, "right_precentral_gyrus": 0.68,
        "left_paracentral_lobule": 0.55, "right_paracentral_lobule": 0.58,
    }
    liver_data = {
        "liver_segment_i": 0.85, "liver_segment_ii": 0.80, "liver_segment_iii": 0.75,
        "liver_segment_iva": 0.65, "liver_segment_ivb": 0.60, "liver_segment_v": 0.55,
        "liver_segment_vi": 0.45, "liver_segment_vii": 0.40, "liver_segment_viii": 0.50,
    }
    vessel_data = {
        "arch_of_aorta": 0.95, "brachiocephalic_trunk": 0.88,
        "left_common_carotid": 0.85, "right_common_carotid": 0.82,
        "left_internal_carotid": 0.78, "right_internal_carotid": 0.75,
        "superior_vena_cava": 0.40, "left_internal_jugular_vein": 0.35,
    }

    fig, axes = plt.subplots(3, 4, figsize=(20, 15))
    fig.suptitle("MediPlot Anatomical Atlas - Multi-View Visualization", fontsize=18, fontweight='bold', y=0.98)

    # Row labels
    row_labels = ["Brain Frontal\n(fMRI)", "Liver Segments\n(Function)", "Vasculature\n(Doppler)"]
    systems = [
        ("brain_frontal", brain_data, "plasma"),
        ("liver_segments", liver_data, "RdYlGn"),
        ("head_neck_vessels", vessel_data, "RdBu_r"),
    ]

    for row, (base_id, data, cmap) in enumerate(systems):
        for col, view in enumerate(VIEWS):
            shape_id = f"{base_id}_{view}"
            organ = mp.OrganMap(shape_id, ax=axes[row, col])
            organ.fill_dict(data, cmap=cmap, show_colorbar=False)

            if row == 0:
                axes[row, col].set_title(VIEW_TITLES[view], fontsize=12, fontweight='bold')
            if col == 0:
                axes[row, col].set_ylabel(row_labels[row], fontsize=11, fontweight='bold', rotation=0,
                                          labelpad=60, ha='right', va='center')

    plt.tight_layout(rect=[0.05, 0, 1, 0.96])
    plt.savefig(OUTPUT_DIR / "multi_organ_example.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {OUTPUT_DIR / 'multi_organ_example.png'}")


if __name__ == "__main__":
    print("Generating README example images...\n")

    # Individual anatomical diagrams with clinical context
    generate_brain_atlas_example()
    generate_head_neck_skeleton_example()
    generate_head_neck_muscles_example()
    generate_head_neck_vessels_example()
    generate_liver_segments_example()
    generate_abdomen_example()

    # Multi-anatomy comparison
    generate_multi_anatomy_example()

    print("\nAll images generated successfully!")
