# Parameters Reference

## Plane Settings

| Parameter | Values | Description |
| --- | --- | --- |
| Plane Type | Preset / Model | Choose between preset planes or model geometry |
| Preset Plane | XY, XZ, YZ | Axis-aligned cut planes |
| Offset | mm | Distance from origin for preset planes |
| Model Plane | Dropdown | Select datum plane or planar face |

## Hole Parameters

| Parameter | Default | Description |
| --- | --- | --- |
| Diameter | 6.2mm | Hole diameter (add 0.1-0.2mm clearance for magnets) |
| Depth | 3.0mm | How deep holes go into each piece |
| Number of Holes | 6 | Total holes to create (evenly distributed) |
| Edge Clearance (Preferred) | 2.0mm | Ideal distance from hole edge to outer surface |
| Edge Clearance (Minimum) | 0.5mm | Absolute minimum acceptable clearance |

---

## Understanding Edge Clearance

The macro uses a **dual clearance system** to balance ideal hole placement with flexibility:

- **Preferred Clearance (2mm default):** Initial hole placement uses this value
- **Minimum Clearance (0.5mm default):** Fallback when preferred clearance fails

### How it works

1. Holes are first placed using the preferred clearance
2. If a hole fails the safety check, smart repositioning kicks in
3. The macro tries progressively smaller clearances (from preferred down to minimum)
4. Only if all clearance levels fail does the macro try moving the hole position

The safety check ensures:

```text
hole_radius + depth + clearance < distance_to_nearest_surface
```

### Visual Example

```text
    [Outer Surface]
         |
    clearance (preferred: 2mm, min: 0.5mm)
         |
    [Hole boundary]  ← Must not touch outer surface
         |
    actual hole
```

---

## Calculating Depth for Magnets

For magnets that should be flush or recessed:

```text
depth = magnet_thickness + recess_amount

Examples:
- 2mm thick magnet, flush: depth = 2.5mm (0.5mm tolerance)
- 3mm thick magnet, 0.5mm recess: depth = 4mm
```

**Important:** Total depth in both pieces should accommodate the magnet:

```text
total_depth = depth_bottom + depth_top
total_depth should be >= magnet_thickness
```

---

## Recommended Hole Count Guidelines

| Object Size | Recommended Holes | Notes |
| --- | --- | --- |
| Small (<50mm) | 4-6 | Fewer holes for small surfaces |
| Medium (50-150mm) | 6-10 | Default of 6 works well |
| Large (>150mm) | 10-16 | More holes for stronger connection |
| Thin-walled | 4-6 | Use smaller diameter holes |

---

## Clearance Guidelines by Object Type

| Object Type | Preferred | Minimum | Notes |
| --- | --- | --- | --- |
| Thin-walled (2-4mm walls) | 2mm | 1mm | Increase minimum to prevent breakthrough |
| Thick objects (>10mm walls) | 3mm | 0.5mm | Defaults work well |
| Irregular shapes | 4-5mm | 2mm | Be conservative for safety |

---

## Technical Details

### How Surface Penetration Detection Works

For each potential hole position, the macro:

1. Creates a test cylinder with radius = `(diameter/2) + clearance`
2. Extends the cylinder to depth = `hole_depth + clearance`
3. Performs boolean intersection with the part
4. If intersection volume < 99% of test cylinder volume → hole would penetrate → skip it

### Coordinate System

- **Origin (0,0,0):** FreeCAD document origin
- **Cut planes** pass through a point at the specified offset:
  - XY plane: Point = (0, 0, offset)
  - XZ plane: Point = (0, offset, 0)
  - YZ plane: Point = (offset, 0, 0)

### Hole Direction

- **Bottom piece:** Holes point UP (toward cut plane)
- **Top piece:** Holes point DOWN (toward cut plane)
- Both sets align perfectly at the cut interface
