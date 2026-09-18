# Smart Cable Generator (Blender Add-on)

A custom Python add-on for Blender that procedurally generates hanging cables between meshes, designed to speed up Tech Art pipelines and environment set-dressing.

## Features
- **Multi-Object Support:** Select vertices across completely different meshes.
- **Parametric Gravity Sag:** Mathematically accurate parabolic curve simulation based on distance.
- **Native UI:** Adjust thickness, resolution, and gravity sag from the sidebar.
- **Material Auto-Assign:** Select a material from the UI to be assigned automatically upon generation.

## Installation
1. Download `smart_cable_gen.py`.
2. In Blender, go to `Edit > Preferences > Add-ons > Install...`.
3. Select the Python file and enable it.
4. Press `N` in the 3D viewport to open the sidebar and look for the **Tech Art** tab.

## Usage
1. Select two objects in Object Mode.
2. Press `Tab` to enter Multi-Object Edit Mode.
3. Select exactly 1 vertex on the first object, and 1 vertex on the second.
4. Choose a Preset or tweak settings in the UI panel.
5. Click **Generate Cable**.
