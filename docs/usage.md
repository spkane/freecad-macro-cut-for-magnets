# Usage Guide

## Quick Start Guide

### Step 1: Prepare Your Model

1. Open your model in FreeCAD (or create/import one)
2. Ensure the object is a **solid** (not a shell or surface)
3. **Select the object** in the 3D view or tree view

!!! tip
    If you imported an STL, it should already be a valid solid. If you created the model in FreeCAD, make sure you created a solid object in the Part workbench.

### Step 2: Launch the Macro

- **From Macro Menu:** Macro → Macros... → Select "CutObjectForMagnets" → Execute
- **From Toolbar:** Click the macro icon (if you created a toolbar button)

### Step 3: Configure Cut Plane

The dialog will open with several configuration sections.

#### Option 1: Preset Plane (Simple, axis-aligned cuts)

- **Plane:** Choose orientation
  - `XY` - Horizontal cut (most common)
  - `XZ` - Vertical cut (front-to-back)
  - `YZ` - Vertical cut (left-to-right)

- **Offset:** Position of the cut plane from origin (in mm)
  - `0` - Cut through the origin
  - Positive values move the plane in the positive axis direction
  - Negative values move it in the negative axis direction

**Finding the Right Offset:**

1. Note your object's bounding box dimensions (visible in FreeCAD)
2. If your object is centered at origin and you want to cut in half: Use offset = `0`
3. If your object is positioned elsewhere: Look at the coordinate where you want to cut

#### Option 2: Model Plane (Advanced, angled cuts)

Select any datum plane or planar face from your model:

**Using Datum Planes:**

1. Create a datum plane first (if not already in model):
    - Go to **Part Design** workbench
    - Click **Create datum plane** (or Part → Datum → Datum Plane)
    - Position and angle the plane where you want to cut
    - Exit datum plane creation

2. In the macro dialog:
    - Select **"Model Plane"** from Plane Type
    - Choose your datum plane from the dropdown
    - The offset field is disabled (plane position defines the cut)

**Using Object Faces:**

- Any planar face on any object in your document can be used as a cut plane
- Select from the dropdown: "Face: [ObjectName] (Face1, Face2, etc.)"
- Useful for cutting along existing geometry

### Step 4: Configure Magnet Holes

- **Diameter:** The diameter of your magnet (mm)
  - For 6mm magnets: Use `6.2mm` (adds 0.2mm clearance)
  - For 3mm dowels: Use `3.1mm` (adds 0.1mm clearance)

- **Depth:** How deep holes go into each piece (mm)
  - For magnets: Use magnet thickness + 0.5mm
  - For dowel pins: Usually half the dowel length

- **Number of Holes:** Total number of magnet holes to create (default: 6)
  - Holes are evenly distributed around the perimeter
  - Recommended: `4-6` for small objects, `8-12` for large objects

- **Edge Clearance (Preferred):** Ideal distance from hole edge to outer surface
  - Default: `2mm` - holes are initially placed with this clearance

- **Edge Clearance (Minimum):** Absolute minimum acceptable clearance
  - Default: `0.5mm` - the smallest allowable clearance

### Step 5: Execute the Cut

1. Review all parameters
2. Click **"Execute Cut"**
3. Watch the progress bar
4. Check status messages for any skipped holes

### Step 6: Review Results

The macro creates two new objects:

- `[ObjectName]_Bottom` - Lower piece with holes
- `[ObjectName]_Top` - Upper piece with holes

Your original object is **hidden** (not deleted) - you can show it again from the tree view if needed.

---

## Common Use Cases

### Case 1: Large Print Split for Bed Size

**Scenario:** 300mm diameter object, need to split for 250mm print bed

**Settings:**

```text
Plane: XY
Offset: 0 (if centered) or half the object height
Diameter: 6.2mm (for 6×2mm magnets)
Depth: 2.5mm
Number of Holes: 12
Clearance: 3mm
```

### Case 2: Modular Terrain Tiles

**Scenario:** 100×100mm terrain tiles with magnetic edges

**Settings:**

```text
Plane: XY or YZ (depending on desired split)
Offset: 50mm (half the tile dimension)
Diameter: 3.2mm (for 3×1mm magnets)
Depth: 1.5mm
Number of Holes: 6
Clearance: 2mm
```

### Case 3: Angled Cut with Datum Plane (45° Wedge)

**Scenario:** Splitting a wedge-shaped console at a 45° angle

**Preparation:**

1. Switch to **Part Design** workbench
2. Create datum plane:
    - Click **Create datum plane**
    - Rotate 45° around X-axis
    - Position at desired cut location
3. Name it "CutPlane45" (optional but helpful)

**Settings:**

```text
Plane Type: Model Plane
Model Plane: Plane: CutPlane45
Diameter: 6.2mm
Depth: 3mm
Number of Holes: 8
Clearance: 3mm
```

---

## Advanced Tips

### Creating Perfect Datum Planes

**For Angled Cuts:**

1. **Simple Rotation Method:**
    - Part Design → Create datum plane
    - Reference: XY plane (or any base plane)
    - Attachment offset → Rotation:
        - Around X: Tilts forward/back
        - Around Y: Tilts left/right
        - Around Z: Spins horizontally

2. **Align to Edges/Vertices:**
    - Attachment mode: "Three points"
    - Select 3 points on your model
    - Plane will pass through all three points

### Magnet Installation Tips

After printing:

1. Test fit magnets - they should slide in smoothly
2. If too tight: Use a drill bit to clean out the holes
3. If too loose: Use CA glue or epoxy to secure
4. **Check polarity!** - Mark magnet orientation before gluing
