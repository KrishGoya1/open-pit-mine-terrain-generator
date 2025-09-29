# Procedural Open-Pit Mine Generator for Blender

A comprehensive Python script for Blender that procedurally generates complex and realistic 3D models of open-pit mines. This tool automates the creation of detailed terrains, featuring terraced benches, spiral haul roads, branching ramps, and overburden dumps. It is designed to be highly customizable through a central configuration file, enabling the rapid generation of diverse and unique mine models for simulation, visualization, technical illustration, or digital art.

## Table of Contents

  * [About The Project](https://www.google.com/search?q=%23about-the-project)
  * [Key Features](https://www.google.com/search?q=%23key-features)
  * [Getting Started](https://www.google.com/search?q=%23getting-started)
      * [Prerequisites](https://www.google.com/search?q=%23prerequisites)
      * [Installation](https://www.google.com/search?q=%23installation)
  * [Usage](https://www.google.com/search?q=%23usage)
  * [Customization](https://www.google.com/search?q=%23customization)
  * [Technical Overview](https://www.google.com/search?q=%23technical-overview)
  * [Future Development](https://www.google.com/search?q=%23future-development)
  * [License](https://www.google.com/search?q=%23license)

-----

## About The Project

Modeling large-scale industrial sites like open-pit mines is a time-consuming and labor-intensive task. This project provides a procedural solution to this challenge, replacing manual modeling with an automated, parameter-driven workflow.

The generator uses a combination of geometric calculations and noise algorithms (Fractal Brownian Motion) to construct every aspect of the mine, from the overall pit shape to the fine surface details. The result is a topologically clean, high-resolution 3D mesh that is ready for immediate use in Blender.

-----

## Key Features

  * **Multi-Pit Generation:** Create complex mine sites by defining multiple overlapping or adjacent pits, each with its own unique size, depth, and location.
  * **Dynamic Haul Road Network:** Automatically generates a primary spiral haul road descending into the pit, along with configurable secondary and branch ramps for a complete transportation network.
  * **Procedural Overburden Dumps:** Simulates the placement of waste rock in terraced dumps around the pit rim, adhering to a specified angle of repose for physical realism.
  * **Configurable Bench Geometry:** Full control over the vertical height and horizontal width of the pit's terraced benches, including the ability to simulate randomly "skipped" or collapsed sections.
  * **Noise-Driven Terrain Realism:** Utilizes multi-layered FBM noise to introduce natural-looking variation to all surfaces, from large-scale ground undulations to fine-grained rock texture.
  * **Erosion Simulation:** A post-processing step applies a smoothing algorithm that simulates basic hydraulic erosion, creating more natural talus slopes and softening sharp geometric edges.
  * **Automated Vertex Coloring:** Automatically applies vertex colors based on elevation, providing a clear visual distinction between different geological strata and soil layers.
  * **Fully Parametric Design:** The entire generation process is controlled by a single, easy-to-edit configuration file, allowing for extensive customization and repeatable results.

-----

## Getting Started

To get the generator running on your local machine, follow these simple steps.

### Prerequisites

  * **Blender:** Version 3.0 or newer is recommended. (Python is included with Blender).

### Installation

No formal installation is required. Simply structure the project files as follows.

1.  Create a main project directory (e.g., `blender_mine_generator`).
2.  Place the `run_in_blender.py` script inside this main directory.
3.  Create a sub-directory named `mine_generator` inside the main directory.
4.  Place all other module files (`__init__.py`, `config.py`, `utils.py`, etc.) inside the `mine_generator` sub-directory.

The final file structure must be:

```
blender_mine_generator/
│
├── run_in_blender.py
│
└── mine_generator/
    ├── __init__.py
    ├── config.py
    ├── dump_generator.py
    ├── mesh_builder.py
    ├── pit_generator.py
    └── utils.py
```

-----

## Usage

1.  Launch Blender.
2.  Navigate to the **Scripting** workspace.
3.  In the Text Editor, go to **Text -\> Open** and select the `run_in_blender.py` file from your project directory.
4.  Click the **"Run Script"** button (play icon) at the top of the Text Editor.
5.  The script will execute, and the generated mesh will appear in the 3D Viewport. Progress will be printed to the Blender System Console (`Window -> Toggle System Console`).

-----

## Customization

All aspects of the generated mine can be customized by editing the parameters in the `mine_generator/config.py` file. Open this file in any text editor to adjust the settings.

Key customizable areas include:

  * **Global Settings:** `RESOLUTION` and `SIZE` of the generated terrain plane.
  * **Pit Geometry:** `MAX_PIT_RADIUS`, `MAX_DEPTH`, `BENCH_HEIGHT`, `BENCH_WIDTH`, etc.
  * **Multi-Pit System:** `MULTI_PIT_COUNT`, `PIT_SPREAD`, and variations in size and depth.
  * **Road Network:** `ROAD_WIDTH`, `ROAD_SPIRAL_TURNS`, and ramp counts/lengths.
  * **Overburden Dumps:** `DUMP_MAIN_COUNT`, `DUMP_MAX_HEIGHT`, `DUMP_ANGLE_OF_REPOSE`, and sector sizes.
  * **Noise and Realism:** `NOISE_SEED` (for repeatable results), noise scales, and amplitudes for different levels of detail.

After saving your changes to `config.py`, simply re-run the `run_in_blender.py` script to see the new result.

-----

## Technical Overview

The generator's logic is modularized into several distinct Python files, each with a specific responsibility:

  * `config.py`: Holds all user-configurable parameters.
  * `utils.py`: Contains generic helper functions for noise and mathematics.
  * `pit_generator.py`: Calculates the geometry and features of the pit itself.
  * `dump_generator.py`: Calculates the geometry of the overburden dumps.
  * `mesh_builder.py`: Interfaces with the Blender API (`bpy`, `bmesh`) to construct the 3D mesh.
  * `run_in_blender.py`: The main execution script that orchestrates the entire process.

The core algorithm operates by creating a high-resolution grid and iterating through each vertex. For each vertex, it calculates a final elevation by combining the outputs of the pit and dump generator functions. This height map is then post-processed with an erosion filter before being used to construct the final mesh within Blender.

-----

## Future Development

Potential enhancements for future versions include:

  * A user interface (UI) panel directly within Blender to adjust parameters without editing the configuration file.
  * Implementation of a more advanced, hydraulic erosion simulation.
  * Procedural generation and application of materials and textures.
  * Automated placement of mine-related assets (e.g., trucks, shovels, buildings).
  * Options for exporting the model and heightmaps in various standard formats.

-----

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

-----
