# Cut Object for Magnets - FreeCAD Macro

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FreeCAD](https://img.shields.io/badge/FreeCAD-0.21+-blue.svg)](https://www.freecadweb.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776ab.svg)](https://www.python.org/)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://spkane.github.io/freecad-macro-cut-for-magnets/)

[![Tests](https://github.com/spkane/freecad-macro-cut-for-magnets/actions/workflows/tests.yaml/badge.svg)](https://github.com/spkane/freecad-macro-cut-for-magnets/actions/workflows/tests.yaml)
[![Pre-commit](https://github.com/spkane/freecad-macro-cut-for-magnets/actions/workflows/pre-commit.yaml/badge.svg)](https://github.com/spkane/freecad-macro-cut-for-magnets/actions/workflows/pre-commit.yaml)
[![CodeQL](https://github.com/spkane/freecad-macro-cut-for-magnets/actions/workflows/codeql.yaml/badge.svg)](https://github.com/spkane/freecad-macro-cut-for-magnets/actions/workflows/codeql.yaml)

![Macro Icon](macro/Cut_Object_for_Magnets/CutObjectForMagnets.svg)

**Version:** 0.6.1

A FreeCAD macro that intelligently cuts 3D objects along a plane and automatically places magnet holes with built-in surface penetration detection. Perfect for creating multi-part prints that snap together with magnets!

## Features

- **Smart Surface Detection** - Automatically skips holes that would penetrate the object's outer surface
- **Smart Repositioning** - When a hole would penetrate, tries nearby positions
- **Dual-Part Validation** - Validates each hole position works for BOTH parts
- **Flexible Plane Selection** - Use preset planes (XY/XZ/YZ) OR any datum plane from your model
- **Angled Cuts** - Cut along any angle by selecting a datum plane
- **Even Distribution** - Holes are evenly spaced around the perimeter of the cut face
- **Non-Destructive** - Original object is hidden, not deleted

## Quick Start

1. Open your model in FreeCAD
2. Select the object to cut
3. Run the macro: **Macro -> Macros... -> CutObjectForMagnets -> Execute**
4. Configure the cut plane and magnet hole parameters
5. Click **Execute Cut**

## Installation

### From FreeCAD Addon Manager (Recommended)

1. Open FreeCAD
2. Go to **Tools -> Addon Manager**
3. Search for "Cut Object for Magnets"
4. Click **Install**
5. Restart FreeCAD

### Manual Installation

Download `CutObjectForMagnets.FCMacro` and `CutObjectForMagnets.svg` from the `macro/Cut_Object_for_Magnets/` directory and copy them to your FreeCAD macro folder:

- **macOS**: `~/Library/Application Support/FreeCAD/Macro/`
- **Linux**: `~/.local/share/FreeCAD/Macro/` or `~/.FreeCAD/Macro/`
- **Windows**: `%APPDATA%/FreeCAD/Macro/`

## Usage

### Method 1: Preset Planes (Simple)

```text
Select Object -> Run Macro -> Choose XY/XZ/YZ -> Set Offset -> Execute
```

Use for: Axis-aligned cuts, quick splits, standard orientations

### Method 2: Model Planes (Advanced - Any Angle)

```text
Create Datum Plane (angled as needed) -> Select Object -> Run Macro ->
Choose "Model Plane" -> Select Your Plane -> Execute
```

Use for: Angled cuts, following model geometry, complex orientations

## Parameters

| Parameter | Description | Default |
| --- | --- | --- |
| Plane Type | Preset (XY/XZ/YZ) or Model Plane | Preset |
| Offset | Distance from origin for preset planes | 0mm |
| Hole Diameter | Size of magnet holes (e.g., 6.2mm for 6mm magnets) | 6.2mm |
| Hole Depth | How deep holes go into each piece | 2.5mm |
| Number of Holes | Total holes to create (evenly distributed) | 6 |
| Edge Clearance (Preferred) | Ideal distance from hole to surface | 2mm |
| Edge Clearance (Minimum) | Absolute minimum acceptable clearance | 0.5mm |

## Common Use Cases

### Large Print Split for Bed Size

```text
Plane: XY, Offset: 0, Diameter: 6.2mm, Depth: 2.5mm, Holes: 12
```

### Modular Terrain Tiles

```text
Plane: XY, Offset: 50mm, Diameter: 3.2mm, Depth: 1.5mm, Holes: 6
```

### Dowel Pin Alignment

```text
Plane: XY, Diameter: 3.1mm, Depth: 8mm, Holes: 4
```

## Documentation

For detailed documentation including:

- Step-by-step installation guides
- Advanced usage with datum planes
- Troubleshooting tips
- Technical details

See the [full documentation](macro/Cut_Object_for_Magnets/README-CutObjectForMagnets.md).

## Requirements

- FreeCAD 0.21 or later (0.19+ may work)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Credits

Created for the FreeCAD community to make multi-part 3D printing easier and more reliable.
