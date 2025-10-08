# Procedural 3D Open-Pit Mine Terrain Generator

![Blender](https://img.shields.io/badge/Blender-3D%20Modeling-orange)
![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![Procedural Generation](https://img.shields.io/badge/Procedural-Generation-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

A sophisticated procedural terrain generator that creates realistic 3D models of open-pit mines, overburden dumps, and surrounding landscapes using advanced algorithms and Fractal Brownian Motion.

## 🎥 Demo & Screenshots

*[Add screenshots or renderings of generated mine terrain here]*

## ✨ Features

### 🏔️ Realistic Mine Geometry
- **Bench Terraces**: Automatically generated stepped benches with realistic widths and heights
- **Spiral Access Roads**: Procedural road networks that wrap around the pit with proper grading
- **Branching Ramps**: Secondary and tertiary ramp systems for detailed mine operations
- **Multi-Pit Blending**: Support for multiple nested pits with varied sizes and depths

### 🌄 Natural Terrain Features
- **Overburden Dumps**: Realistic waste material piles with proper angle of repose
- **Plateau Formation**: Elevated flat-top features using inverted pit generation
- **Hydraulic Erosion**: Simulated weathering and erosion for natural appearance
- **Stratified Coloring**: Vertex-based color mapping for geological realism

### ⚙️ Advanced Algorithms
- **Fractal Brownian Motion**: Multi-octave noise for natural terrain variation
- **Procedural Generation**: Parameter-driven design with extensive customization
- **Radial Deformation**: Boundary noise for organic pit shapes
- **Mathematical Modeling**: Trigonometric functions for spiral roads and slopes

## 🛠️ Installation

### Prerequisites
- **Blender 3.0+** [Download here](https://www.blender.org/download/)
- **Python 3.7+** (included with Blender)

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/KrishGoya1/open-pit-mine-terrain-generator.git
   cd open-pit-mine-terrain-generator
   ```

2. **Open in Blender**
   - Launch Blender
   - Open the Text Editor workspace
   - Load `run_in_blender.py`

3. **Run the Script**
   - Click "Run Script" or press Alt+P
   - The generation process will start automatically

## 🚀 Usage

### Basic Generation
1. Open `run_in_blender.py` in Blender's text editor
2. Run the script (Alt+P)
3. Watch the procedural generation in real-time
4. The final mesh will be created as "OpenPit_WithDumps"

### Customization
Modify parameters in `mine_generator/config.py`:

```python
# Pit dimensions
MAX_PIT_RADIUS = 110.0      # Maximum pit radius
MAX_DEPTH = 60.0            # Maximum depth
BENCH_HEIGHT = 6.0          # Height of each bench

# Road configuration
ROAD_WIDTH = 12.0           # Width of access roads
ROAD_SPIRAL_TURNS = 4.5     # Number of spiral turns

# Multi-pit settings
MULTI_PIT_COUNT = 2         # Number of additional pits
PIT_SPREAD = 38.0           # Spread between pits

# Random seed for reproducibility
NOISE_SEED = 42             # Set to None for random
```

### Advanced Features

#### Multi-Pit Generation
Enable complex mine systems with multiple interconnected pits:
```python
EXPLICIT_PIT_CENTERS = [(0, 0, 1.0, 1.0), (40, 10, 0.7, 0.8)]
```

#### Dump Configuration
Customize overburden dump properties:
```python
DUMP_MAX_HEIGHT = 26.0
DUMP_ANGLE_OF_REPOSE = 34.0  # Natural slope angle
```

#### Plateau Generation
Create elevated flat-top features:
```python
PLATEAU_ENABLED = True
PLATEAU_MAX_HEIGHT = 45.0
PLATEAU_RADIUS = 70.0
```

## 📁 Project Structure

```
open-pit-mine-terrain-generator/
├── run_in_blender.py              # Main execution script
├── mine_generator/
│   ├── config.py                  # Central configuration
│   ├── pit_generator.py           # Core pit generation algorithms
│   ├── dump_generator.py          # Overburden dump generation
│   ├── plateau_generator.py       # Plateau/mountain features
│   ├── mesh_builder.py            # Blender mesh operations
│   └── utils.py                   # Math and noise utilities
```

### Module Overview

- **`config.py`**: Central hub for all tunable parameters and global settings
- **`pit_generator.py`**: Core algorithms for bench formation, road networks, and pit geometry
- **`dump_generator.py`**: Generates realistic overburden dumps with proper slope physics
- **`plateau_generator.py`**: Creates elevated features by repurposing pit generation logic
- **`mesh_builder.py`**: Handles Blender-specific mesh creation, erosion, and vertex coloring
- **`utils.py`**: Mathematical utilities including FBM noise and interpolation functions

## 🔧 Technical Details

### Algorithmic Foundation

#### Fractal Brownian Motion (FBM)
```python
def fbm(x, y, seed, octaves=4, lacunarity=2.0, gain=0.5):
    """Multi-octave noise for natural terrain variation"""
    value = 0.0
    freq = 1.0
    amp = 1.0
    for _ in range(octaves):
        value += amp * perlin3(x * freq, y * freq, seed)
        freq *= lacunarity
        amp *= gain
    return value
```

#### Bench Generation
- Hierarchical bench system with skip probabilities
- Radial deformation using boundary noise
- Center preservation for stable pit bottoms

#### Road Network
- Main spiral road with mathematical precision
- Branching and secondary ramps
- Road-aware boundary smoothing

### Performance Considerations

- **Resolution**: Configurable grid resolution (default: 220×220)
- **Erosion Iterations**: Adjustable erosion simulation passes
- **Subdivision Levels**: Control mesh density for rendering
- **Vertex Colors**: Optional stratigraphic coloring

## 🎨 Customization Guide

### Creating Different Mine Types

#### Deep Narrow Mine
```python
MAX_PIT_RADIUS = 80.0
MAX_DEPTH = 100.0
BENCH_HEIGHT = 8.0
```

#### Shallow Wide Mine
```python
MAX_PIT_RADIUS = 200.0
MAX_DEPTH = 30.0
BENCH_HEIGHT = 4.0
```

#### Complex Multi-Pit System
```python
MULTI_PIT_COUNT = 4
PIT_SPREAD = 50.0
PIT_SIZE_VARIATION = 0.8
```

### Terrain Styling

Modify vertex colors in `mesh_builder.py`:
```python
def _color_for_depth(z, zmin, zmax):
    n = (zmax - z) / max(1e-6, (zmax - zmin))
    if n < 0.12: return (0.78, 0.75, 0.66, 1.0)  # Topsoil
    elif n < 0.33: return (0.66, 0.56, 0.45, 1.0)  # Weathered rock
    elif n < 0.66: return (0.50, 0.48, 0.50, 1.0)  # Intermediate rock
    else: return (0.18, 0.15, 0.12, 1.0)         # Bedrock
```

## 🚀 Exporting for Other Applications

### For Game Engines
1. Generate terrain in Blender
2. Use File → Export → FBX/OBJ
3. Import into Unity/Unreal Engine
4. Apply appropriate materials and collision

### For Rendering
1. Apply high-quality materials in Blender
2. Set up lighting for dramatic effects
3. Use Cycles or Eevee for final renders

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Citation

If you use this project in your research or work, please cite:

```bibtex
@software{open_pit_mine_generator,
  title = {Procedural 3D Open-Pit Mine Terrain Generator},
  author = {Krish Goyal},
  year = {2024},
  url = {https://github.com/KrishGoya1/open-pit-mine-terrain-generator}
}
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Blender Foundation** for the incredible 3D creation suite
- **Ken Perlin** for the original noise algorithm that powers procedural generation
- The **procedural generation community** for continuous inspiration

## 📞 Contact

**Krish Goyal**
- Email: goyalkrish183@gmail.com
- LinkedIn: [linkedin.com/in/goyalkrish](https://www.linkedin.com/in/goyalkrish)
- GitHub: [github.com/KrishGoya1](https://github.com/KrishGoya1)

---

**⭐ If you find this project useful, please give it a star on GitHub!**

---

<div align="center">
  
### 🎯 Project Status

![Active Development](https://img.shields.io/badge/Status-Active%20Development-brightgreen)
![Blender Compatibility](https://img.shields.io/badge/Blender-3.0%2B%20Compatible-orange)
![Python](https://img.shields.io/badge/Python-3.7%2B%20Tested-blue)

</div>
