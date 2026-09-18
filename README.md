# Smart Cable Generator (Blender Add-on)

A custom Python add-on for Blender that procedurally generates parametric hanging cables between meshes. Built to speed up Tech Art pipelines for AAA environments.

*(Check out the video demonstrations on my [Portfolio](https://federicocolombo12.github.io/PortFolio/projects/smart-cable-generator))*

## 🧠 Engineering Walkthrough & Features

### 1. Mid-Air Mathematical Pathing
Initially prototyped as a topology-hugging Dijkstra algorithm, the tool was rewritten to use a global-space mathematical approach (`matrix_world @ v.co`). This allows artists to enter Multi-Object Edit Mode and connect vertices across entirely different, disconnected modular buildings.

### 2. Scale-Independent Parabolic Gravity
To simulate realistic weight without running costly physics simulations, the script applies a parabolic equation: `4.0 * sag * t * (1.0 - t)`. Crucially, this sag is mathematically multiplied by the absolute 3D distance between the start and end points. This ensures the physical droop looks accurate whether you are connecting two small desk props or two massive skyscrapers.

### 3. Organic Cable Bundles (Noise Variation)
Perfectly parallel lines look unnatural in games. By increasing the `Cable Count` in the UI, the script uses pseudo-random noise to apply subtle X/Y positional offsets and gravity variations to each individual spline, generating messy, organic wire bundles instantly.

### 4. Game-Ready Export (Auto-Convert)
Blender curves require conversion before FBX export to Unreal Engine 5. The tool includes an **Auto-Convert to Mesh** toggle that programmatically changes the Blender context, collapses the splines into polygons, and applies the selected UI Material, ensuring the asset is 100% engine-ready in one click.

## 🛠 Installation
1. Download `smart_cable_gen.py`.
2. In Blender, go to `Edit > Preferences > Add-ons > Install...`.
3. Select the Python file and enable the add-on.
4. Press `N` in the 3D viewport to open the sidebar and look for the **Tech Art** tab.

## 🖱 Usage
1. Select two objects (e.g., two buildings) in Object Mode.
2. Press `Tab` to enter Multi-Object Edit Mode.
3. Select exactly 1 vertex on the first object, and 1 vertex on the second.
4. Tweak the settings in the UI panel (Bundle Count, Gravity, Material).
5. Click **Generate Cable(s)**.
