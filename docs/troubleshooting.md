# Troubleshooting

## Common Errors

### "Please select an object to cut"

**Solution:** Click on your object in the 3D view before running the macro.

---

### "Selected object does not have a shape"

**Cause:** You selected a group or annotation.

**Solution:** Select the actual 3D object (should be under Part or Body in the tree).

---

### "Failed to cut object"

**Possible causes:**

1. **Invalid mesh** - The object has geometry errors
    - Try: Edit → Preferences → Part Design → "Automatically refine model after boolean operation"
    - Or manually: Part → Refine Shape

2. **Offset is outside object bounds** - The cut plane doesn't intersect the object
    - Check your object's position and bounding box
    - Adjust offset to actually pass through the object

3. **Model plane doesn't intersect** - The selected datum plane doesn't pass through the object
    - Verify the plane position in the 3D view
    - Create a new datum plane that actually cuts through the object

---

### "No planes available"

**Cause:** You selected "Model Plane" but no datum planes or planar faces exist in the document.

**Solution:**

1. Create a datum plane:
    - **Part Design → Create datum plane**
    - Position and angle as needed
    - Click OK
2. Or switch to "Preset Plane" mode
3. Re-run the macro

---

### "Skipping hole at [position] - would penetrate surface"

!!! note "This is normal!"
    The macro is protecting you from holes that would break through.

**If too many holes are skipped:**

1. **Increase edge clearance** (e.g., from 2mm to 4mm)
2. **Reduce number of holes** (fewer holes, but safer)
3. **Reduce hole depth** (less likely to penetrate)
4. **Check your object** - might be too thin for the hole size

---

### "No valid hole positions found"

**Possible causes:**

1. **Cut surface too small** - Not enough room for even one hole
    - Solution: Reduce number of holes or hole diameter

2. **Object too thin** - All positions would penetrate
    - Solution: Reduce hole depth or increase clearance values

3. **Complex geometry** - Cut surface is irregular
    - Solution: Manually place holes in FreeCAD after cutting

---

## Performance Issues

### Macro is slow

**Possible causes:**

1. **Complex object geometry** - Many faces/vertices
    - Try simplifying the mesh before cutting

2. **Too many holes** - Each hole requires collision checking
    - Reduce number of holes

3. **Large hole depth** - Deeper holes require more collision checking
    - Use shallower holes if possible

---

## Getting Help

If you encounter an issue not covered here:

1. Check the [GitHub Issues](https://github.com/spkane/freecad-macro-cut-for-magnets/issues) for similar problems
2. Open a new issue with:
    - FreeCAD version
    - Operating system
    - Steps to reproduce
    - Error message (if any)
    - Screenshot of the object/settings (if helpful)
