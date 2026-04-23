"""End-to-end demo via SceneManager.

Run:
    python scripts/demo.py

Writes to assets/:
    demo_subcortex.png   — oblique view, transparent MNI152 with paired subcortical ROIs
    demo_cortex.png      — left-lateral view, four labeled cortical landmarks
    demo_rotation.gif    — 360° rotating subcortex scene
"""

from __future__ import annotations

from pathlib import Path

import pyvista as pv

from ezbv import config
from ezbv.atlases import AtlasRegistry
from ezbv.meshing import MeshBuilder
from ezbv.scene import SceneManager
from ezbv.templates import TemplateRegistry


# Paired subcortical structures — localized, visible through a transparent shell,
# well-separated so the colored solids read cleanly from any angle.
SUBCORTEX = [
    ("harvard_oxford_sub", "Left Hippocampus",  (0.894, 0.102, 0.110)),
    ("harvard_oxford_sub", "Right Hippocampus", (0.894, 0.102, 0.110)),
    ("harvard_oxford_sub", "Left Amygdala",     (1.000, 0.498, 0.000)),
    ("harvard_oxford_sub", "Right Amygdala",    (1.000, 0.498, 0.000)),
    ("harvard_oxford_sub", "Left Caudate",      (0.216, 0.494, 0.722)),
    ("harvard_oxford_sub", "Right Caudate",     (0.216, 0.494, 0.722)),
    ("harvard_oxford_sub", "Left Putamen",      (0.302, 0.686, 0.290)),
    ("harvard_oxford_sub", "Right Putamen",     (0.302, 0.686, 0.290)),
    ("harvard_oxford_sub", "Left Thalamus",     (0.596, 0.306, 0.639)),
    ("harvard_oxford_sub", "Right Thalamus",    (0.596, 0.306, 0.639)),
]


# Four cortical landmarks that project to distinct quadrants in a left-lateral
# view — labels stay readable without colliding.
CORTEX_LATERAL = [
    ("harvard_oxford_cort", "Precentral Gyrus",        (0.894, 0.102, 0.110)),
    ("harvard_oxford_cort", "Superior Parietal Lobule", (0.302, 0.686, 0.290)),
    ("harvard_oxford_cort", "Temporal Pole",           (1.000, 0.498, 0.000)),
    ("harvard_oxford_cort", "Occipital Pole",          (0.596, 0.306, 0.639)),
]


def _find_label(labels, needle: str):
    for lab in labels:
        if lab.name.lower() == needle.lower():
            return lab
    for lab in labels:
        if needle.lower() in lab.name.lower():
            return lab
    raise LookupError(f"No label matching {needle!r}")


def _new_scene() -> SceneManager:
    plotter = pv.Plotter(off_screen=True, window_size=config.EXPORT_BASE_SIZE)
    return SceneManager(plotter, AtlasRegistry(), TemplateRegistry(), MeshBuilder())


def _populate(scene: SceneManager, picks, *, show_labels: bool) -> None:
    scene.add_template("mni152_detailed", opacity=config.DEFAULT_TEMPLATE_OPACITY)
    for atlas_id, needle, color in picks:
        atlas = scene.atlases.get_atlas(atlas_id)
        label = _find_label(atlas.labels, needle)
        scene.add_layer(
            atlas_id, label.index, color=color, opacity=1.0, show_label=show_labels
        )


def main() -> None:
    out_dir = Path(__file__).resolve().parent.parent / "assets"
    out_dir.mkdir(exist_ok=True)

    # 1. Subcortex hero — no labels, oblique view.
    scene = _new_scene()
    _populate(scene, SUBCORTEX, show_labels=False)
    scene.set_camera_preset("oblique")
    scene.export_png(out_dir / "demo_subcortex.png", width_px=1600, dpi=200, transparent=True)
    print("Wrote", out_dir / "demo_subcortex.png")

    # 2. Rotating GIF — same subcortex scene, vertical spin.
    scene.export_gif(
        out_dir / "demo_rotation.gif",
        width_px=720,
        rotation_axis="vertical",
        rotation_deg=360.0,
        n_frames=48,
        cycle_duration_s=4.0,
        loop=True,
    )
    print("Wrote", out_dir / "demo_rotation.gif")

    # 3. Cortex labeled — left lateral view, four spread-out landmarks.
    scene = _new_scene()
    _populate(scene, CORTEX_LATERAL, show_labels=True)
    scene.set_camera_preset("left")
    scene.export_png(out_dir / "demo_cortex.png", width_px=1600, dpi=200, transparent=True)
    print("Wrote", out_dir / "demo_cortex.png")


if __name__ == "__main__":
    main()
