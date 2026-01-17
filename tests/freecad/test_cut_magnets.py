"""FreeCAD integration tests for Cut Object for Magnets macro.

SPDX-License-Identifier: MIT
Copyright (c) 2025 Sean P. Kane (GitHub: spkane)

These tests require FreeCAD to be installed and run inside FreeCAD.
Run with: freecad -c tests/freecad/test_cut_magnets.py

Or use the just command:
    just testing::freecad
"""

import sys
import unittest
from pathlib import Path

# Add the macro directory to the path for imports
macro_dir = Path(__file__).parent.parent.parent / "macro" / "Cut_Object_for_Magnets"
sys.path.insert(0, str(macro_dir))

import FreeCAD as App  # noqa: E402
import Part  # noqa: E402
from cut_magnets_fc import (  # noqa: E402
    count_cylindrical_faces,
    create_body_from_shape,
    create_cutting_box,
    detect_existing_holes,
    find_cut_face_center,
    get_object_type,
    get_outer_wire,
    get_point_at_length,
    is_hole_safe,
    is_plane_object,
    perform_cut,
    project_hole_to_plane,
)


class TestHelperFunctions(unittest.TestCase):
    """Test helper functions in cut_magnets_fc module."""

    def test_is_plane_object_with_plane(self):
        """Test is_plane_object with a datum plane."""
        doc = App.newDocument("TestIsPlane")
        try:
            body = doc.addObject("PartDesign::Body", "Body")
            plane = body.newObject("PartDesign::Plane", "DatumPlane")
            self.assertTrue(is_plane_object(plane))
        finally:
            App.closeDocument("TestIsPlane")

    def test_is_plane_object_with_box(self):
        """Test is_plane_object with a box (not a plane)."""
        doc = App.newDocument("TestIsPlaneBox")
        try:
            box = doc.addObject("Part::Box", "Box")
            doc.recompute()
            self.assertFalse(is_plane_object(box))
        finally:
            App.closeDocument("TestIsPlaneBox")

    def test_get_object_type_part(self):
        """Test get_object_type with Part object."""
        doc = App.newDocument("TestGetType")
        try:
            box = doc.addObject("Part::Box", "Box")
            doc.recompute()
            obj_type = get_object_type(box)
            self.assertEqual(obj_type, "Box")
        finally:
            App.closeDocument("TestGetType")

    def test_get_object_type_partdesign(self):
        """Test get_object_type with PartDesign object."""
        doc = App.newDocument("TestGetTypePD")
        try:
            body = doc.addObject("PartDesign::Body", "Body")
            obj_type = get_object_type(body)
            self.assertEqual(obj_type, "Body")
        finally:
            App.closeDocument("TestGetTypePD")


class TestCuttingBox(unittest.TestCase):
    """Test cutting box creation."""

    def test_create_cutting_box(self):
        """Test creating a cutting box."""
        _doc = App.newDocument("TestCutBox")  # noqa: F841
        try:
            # Create a simple box to get bounding box
            box = Part.makeBox(100, 100, 100)
            bbox = box.BoundBox

            # Create cutting box for XY plane at Z=50
            normal = App.Vector(0, 0, 1)
            point = App.Vector(0, 0, 50)

            cutting_box = create_cutting_box(bbox, normal, point)

            # Cutting box should be a solid
            self.assertTrue(cutting_box.Volume > 0)
            # Should be larger than original box
            self.assertTrue(cutting_box.Volume > box.Volume)
        finally:
            App.closeDocument("TestCutBox")


class TestPerformCut(unittest.TestCase):
    """Test the perform_cut function."""

    def test_cut_box_xy_plane(self):
        """Test cutting a box along XY plane."""
        _doc = App.newDocument("TestCutXY")  # noqa: F841
        try:
            # Create a box
            box = Part.makeBox(100, 100, 100)
            bbox = box.BoundBox

            # Create cutting box at Z=50
            normal = App.Vector(0, 0, 1)
            point = App.Vector(50, 50, 50)
            cutting_box = create_cutting_box(bbox, normal, point)

            # Perform cut
            bottom, top = perform_cut(box, cutting_box)

            # Both parts should have volume
            self.assertTrue(bottom.Volume > 0)
            self.assertTrue(top.Volume > 0)

            # Total volume should be close to original
            total_volume = bottom.Volume + top.Volume
            self.assertAlmostEqual(total_volume, box.Volume, delta=1.0)
        finally:
            App.closeDocument("TestCutXY")

    def test_cut_box_xz_plane(self):
        """Test cutting a box along XZ plane."""
        _doc = App.newDocument("TestCutXZ")  # noqa: F841
        try:
            box = Part.makeBox(100, 100, 100)
            bbox = box.BoundBox

            # Cut at Y=50
            normal = App.Vector(0, 1, 0)
            point = App.Vector(50, 50, 50)
            cutting_box = create_cutting_box(bbox, normal, point)

            bottom, top = perform_cut(box, cutting_box)

            self.assertTrue(bottom.Volume > 0)
            self.assertTrue(top.Volume > 0)
        finally:
            App.closeDocument("TestCutXZ")


class TestFindCutFaceCenter(unittest.TestCase):
    """Test finding the cut face center."""

    def test_find_cut_face_center(self):
        """Test finding cut face center on a cut box."""
        _doc = App.newDocument("TestFindFace")  # noqa: F841
        try:
            box = Part.makeBox(100, 100, 100)
            bbox = box.BoundBox

            # Cut at Z=50
            normal = App.Vector(0, 0, 1)
            point = App.Vector(50, 50, 50)
            cutting_box = create_cutting_box(bbox, normal, point)

            bottom, top = perform_cut(box, cutting_box)

            # Find cut face on bottom part
            center = find_cut_face_center(bottom, normal, point)

            self.assertIsNotNone(center)
            # Center should be at approximately (50, 50, 50)
            self.assertAlmostEqual(center.z, 50.0, delta=1.0)
        finally:
            App.closeDocument("TestFindFace")


class TestGetOuterWire(unittest.TestCase):
    """Test getting outer wire from faces."""

    def test_get_outer_wire_box_face(self):
        """Test getting outer wire from a box face."""
        _doc = App.newDocument("TestOuterWire")  # noqa: F841
        try:
            box = Part.makeBox(100, 100, 100)
            # Get top face
            top_face = None
            for face in box.Faces:
                normal = face.normalAt(0.5, 0.5)
                if abs(normal.z - 1.0) < 0.01:
                    top_face = face
                    break

            self.assertIsNotNone(top_face)

            outer_wire = get_outer_wire(top_face)
            self.assertIsNotNone(outer_wire)
            # Square 100x100, perimeter = 400
            self.assertAlmostEqual(outer_wire.Length, 400.0, delta=1.0)
        finally:
            App.closeDocument("TestOuterWire")


class TestGetPointAtLength(unittest.TestCase):
    """Test getting points along wires."""

    def test_get_point_at_length_wire(self):
        """Test getting point at specific length on wire."""
        _doc = App.newDocument("TestPointAtLength")  # noqa: F841
        try:
            box = Part.makeBox(100, 100, 100)
            top_face = None
            for face in box.Faces:
                normal = face.normalAt(0.5, 0.5)
                if abs(normal.z - 1.0) < 0.01:
                    top_face = face
                    break

            outer_wire = get_outer_wire(top_face)

            # Get point at length 0
            point_0 = get_point_at_length(outer_wire, 0.0)
            self.assertIsNotNone(point_0)

            # Get point at length 100 (quarter way around)
            point_100 = get_point_at_length(outer_wire, 100.0)
            self.assertIsNotNone(point_100)

            # Points should be different
            dist = (point_100 - point_0).Length
            self.assertTrue(dist > 1.0)
        finally:
            App.closeDocument("TestPointAtLength")


class TestIsHoleSafe(unittest.TestCase):
    """Test hole safety checking."""

    def test_hole_safe_in_center(self):
        """Test that a hole in the center of a thick object is safe."""
        _doc = App.newDocument("TestHoleSafe")  # noqa: F841
        try:
            # Create a large box
            box = Part.makeBox(100, 100, 100)

            # Check if hole in center is safe
            center = App.Vector(50, 50, 100)  # On top face
            direction = App.Vector(0, 0, -1)  # Into the box
            diameter = 6.0
            depth = 10.0
            clearance = 2.0

            is_safe = is_hole_safe(center, direction, box, diameter, depth, clearance)
            self.assertTrue(is_safe)
        finally:
            App.closeDocument("TestHoleSafe")

    def test_hole_unsafe_near_edge(self):
        """Test that a hole near the edge is detected as unsafe."""
        _doc = App.newDocument("TestHoleUnsafe")  # noqa: F841
        try:
            # Create a small box
            box = Part.makeBox(20, 20, 50)

            # Check if hole near edge is unsafe
            center = App.Vector(1, 10, 50)  # Near X=0 edge
            direction = App.Vector(0, 0, -1)
            diameter = 10.0
            depth = 20.0
            clearance = 2.0

            is_safe = is_hole_safe(center, direction, box, diameter, depth, clearance)
            self.assertFalse(is_safe)
        finally:
            App.closeDocument("TestHoleUnsafe")


class TestDetectExistingHoles(unittest.TestCase):
    """Test detection of existing holes."""

    def test_detect_holes_in_box_with_hole(self):
        """Test detecting cylindrical holes in a shape."""
        _doc = App.newDocument("TestDetectHoles")  # noqa: F841
        try:
            # Create a box and cut a hole in it
            box = Part.makeBox(100, 100, 50)
            hole = Part.makeCylinder(3.0, 50, App.Vector(50, 50, 0), App.Vector(0, 0, 1))
            box_with_hole = box.cut(hole)

            # Detect holes with target radius 3.0
            holes = detect_existing_holes(box_with_hole, 3.0)

            # Should find at least one hole
            self.assertGreater(len(holes), 0)
        finally:
            App.closeDocument("TestDetectHoles")

    def test_no_holes_in_simple_box(self):
        """Test no holes detected in simple box."""
        _doc = App.newDocument("TestNoHoles")  # noqa: F841
        try:
            box = Part.makeBox(100, 100, 50)

            holes = detect_existing_holes(box, 3.0)

            # Should find no holes
            self.assertEqual(len(holes), 0)
        finally:
            App.closeDocument("TestNoHoles")


class TestCountCylindricalFaces(unittest.TestCase):
    """Test counting cylindrical faces."""

    def test_count_in_simple_box(self):
        """Test counting in simple box (no cylinders)."""
        _doc = App.newDocument("TestCountCyl")  # noqa: F841
        try:
            box = Part.makeBox(100, 100, 50)
            count = count_cylindrical_faces(box)
            self.assertEqual(count, 0)
        finally:
            App.closeDocument("TestCountCyl")

    def test_count_in_box_with_hole(self):
        """Test counting in box with cylindrical hole."""
        _doc = App.newDocument("TestCountCylHole")  # noqa: F841
        try:
            box = Part.makeBox(100, 100, 50)
            hole = Part.makeCylinder(5.0, 50, App.Vector(50, 50, 0), App.Vector(0, 0, 1))
            box_with_hole = box.cut(hole)

            count = count_cylindrical_faces(box_with_hole)
            # Should find the cylindrical surface of the hole
            self.assertGreaterEqual(count, 1)
        finally:
            App.closeDocument("TestCountCylHole")


class TestCreateBodyFromShape(unittest.TestCase):
    """Test creating PartDesign bodies from shapes."""

    def test_create_body_from_box(self):
        """Test creating a body from a box shape."""
        doc = App.newDocument("TestCreateBody")
        try:
            box = Part.makeBox(100, 100, 50)

            body = create_body_from_shape(doc, box, "TestBody")

            self.assertIsNotNone(body)
            self.assertEqual(body.TypeId, "PartDesign::Body")
            self.assertIsNotNone(body.BaseFeature)
        finally:
            App.closeDocument("TestCreateBody")


class TestProjectHoleToPlane(unittest.TestCase):
    """Test projecting holes to cut planes."""

    def test_project_aligned_hole(self):
        """Test projecting a hole aligned with cut plane."""
        _doc = App.newDocument("TestProject")  # noqa: F841
        try:
            # Hole info simulating a vertical hole
            hole = {
                "center": App.Vector(50, 50, 25),
                "axis": App.Vector(0, 0, 1),
                "radius": 3.0,
                "depth": 10.0,
            }

            # Cut plane at Z=50
            cut_normal = App.Vector(0, 0, 1)
            cut_point = App.Vector(0, 0, 50)

            projected = project_hole_to_plane(hole, cut_normal, cut_point)

            self.assertIsNotNone(projected)
            # Should project to (50, 50, 50)
            self.assertAlmostEqual(projected.x, 50.0, delta=0.1)
            self.assertAlmostEqual(projected.y, 50.0, delta=0.1)
            self.assertAlmostEqual(projected.z, 50.0, delta=0.1)
        finally:
            App.closeDocument("TestProject")

    def test_project_unaligned_hole(self):
        """Test projecting a hole not aligned with cut plane returns None."""
        _doc = App.newDocument("TestProjectUnaligned")  # noqa: F841
        try:
            # Hole perpendicular to the cut normal
            hole = {
                "center": App.Vector(50, 50, 25),
                "axis": App.Vector(1, 0, 0),  # Horizontal hole
                "radius": 3.0,
                "depth": 10.0,
            }

            cut_normal = App.Vector(0, 0, 1)
            cut_point = App.Vector(0, 0, 50)

            projected = project_hole_to_plane(hole, cut_normal, cut_point)

            # Should return None (not aligned enough)
            self.assertIsNone(projected)
        finally:
            App.closeDocument("TestProjectUnaligned")


def run_tests():
    """Run all tests and return exit code."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestHelperFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestCuttingBox))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformCut))
    suite.addTests(loader.loadTestsFromTestCase(TestFindCutFaceCenter))
    suite.addTests(loader.loadTestsFromTestCase(TestGetOuterWire))
    suite.addTests(loader.loadTestsFromTestCase(TestGetPointAtLength))
    suite.addTests(loader.loadTestsFromTestCase(TestIsHoleSafe))
    suite.addTests(loader.loadTestsFromTestCase(TestDetectExistingHoles))
    suite.addTests(loader.loadTestsFromTestCase(TestCountCylindricalFaces))
    suite.addTests(loader.loadTestsFromTestCase(TestCreateBodyFromShape))
    suite.addTests(loader.loadTestsFromTestCase(TestProjectHoleToPlane))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit_code = run_tests()
    # Exit FreeCAD
    if hasattr(App, "exit"):
        App.exit(exit_code)
    else:
        sys.exit(exit_code)
