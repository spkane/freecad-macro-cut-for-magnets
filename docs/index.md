# Cut Object for Magnets

![Macro Icon](../macro/Cut_Object_for_Magnets/CutObjectForMagnets.svg){ width="64" }

**Version:** 0.6.1 | **License:** MIT | **FreeCAD:** 0.19+

A FreeCAD macro that intelligently cuts 3D objects along a plane and automatically places magnet holes with built-in surface penetration detection. Unlike simple cutting tools, this macro ensures magnet holes won't accidentally break through the outer surface of your object.

Perfect for creating multi-part prints that snap together with magnets or alignment pins!

## Features

- **Smart Surface Detection** - Automatically skips holes that would penetrate the object's outer surface
- **Smart Repositioning** - When a hole would penetrate, tries nearby positions
- **Dual-Part Validation** - Validates each hole position works for BOTH parts
- **Automatic Alignment** - Magnet holes on both pieces are perfectly aligned
- **Flexible Plane Selection** - Use preset planes (XY/XZ/YZ) OR any datum plane from your model
- **Angled Cuts** - Cut along any angle by selecting a datum plane
- **Even Distribution** - Holes are evenly spaced around the perimeter
- **Non-Destructive** - Original object is hidden, not deleted

## Quick Start

### Method 1: Preset Planes (Simple)

```text
Select Object → Run Macro → Choose XY/XZ/YZ → Set Offset → Execute
```

Use for: Axis-aligned cuts, quick splits, standard orientations

### Method 2: Model Planes (Advanced - ANY Angle)

```text
Create Datum Plane (angled as needed) → Select Object → Run Macro →
Choose "Model Plane" → Select Your Plane → Execute
```

Use for: Angled cuts, following model geometry, complex orientations

### Quick Tip: Select Both Object AND Plane Together

```text
Select Object + Plane (Ctrl+Click) → Run Macro → Plane auto-selected!
```

## Documentation

- [Installation](installation.md) - How to install the macro
- [Usage Guide](usage.md) - Detailed step-by-step instructions
- [Parameters](parameters.md) - Reference guide for all settings
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
- [Contributing](contributing.md) - How to contribute
- [Changelog](changelog.md) - Version history

## Links

- [GitHub Repository](https://github.com/spkane/freecad-macro-cut-for-magnets)
- [Report Issues](https://github.com/spkane/freecad-macro-cut-for-magnets/issues)
- [FreeCAD Wiki](https://wiki.freecad.org/Macro_Cut_Object_for_Magnets)
