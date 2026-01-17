"""Unit tests for cut_magnets_core module.

SPDX-License-Identifier: MIT
Copyright (c) 2025 Sean P. Kane (GitHub: spkane)

Tests the pure Python logic without FreeCAD dependency.
Run with: pytest tests/unit -v
"""

import sys
from pathlib import Path

import pytest

# Add the macro directory to the path for imports
macro_dir = Path(__file__).parent.parent.parent / "macro" / "Cut_Object_for_Magnets"
sys.path.insert(0, str(macro_dir))

from cut_magnets_core import (  # noqa: E402
    CutPlaneParameters,
    HoleParameters,
    HolePlacementError,
    Vector3D,
    calculate_clearance_steps,
    calculate_hole_parameter_positions,
    calculate_hole_spacing,
    calculate_inset_distance,
    calculate_perimeter_search_offsets,
    check_hole_overlap,
    format_hole_position,
    format_operation_summary,
    get_preset_plane_normal_and_point,
    validate_cut_parameters,
)


class TestVector3D:
    """Tests for the Vector3D class."""

    def test_vector_creation(self):
        """Test creating a vector."""
        v = Vector3D(1.0, 2.0, 3.0)
        assert v.x == 1.0
        assert v.y == 2.0
        assert v.z == 3.0

    def test_vector_addition(self):
        """Test vector addition."""
        v1 = Vector3D(1.0, 2.0, 3.0)
        v2 = Vector3D(4.0, 5.0, 6.0)
        result = v1 + v2
        assert result.x == 5.0
        assert result.y == 7.0
        assert result.z == 9.0

    def test_vector_subtraction(self):
        """Test vector subtraction."""
        v1 = Vector3D(4.0, 5.0, 6.0)
        v2 = Vector3D(1.0, 2.0, 3.0)
        result = v1 - v2
        assert result.x == 3.0
        assert result.y == 3.0
        assert result.z == 3.0

    def test_vector_scalar_multiplication(self):
        """Test multiplying vector by scalar."""
        v = Vector3D(1.0, 2.0, 3.0)
        result = v * 2.0
        assert result.x == 2.0
        assert result.y == 4.0
        assert result.z == 6.0

    def test_vector_rmul(self):
        """Test scalar * vector."""
        v = Vector3D(1.0, 2.0, 3.0)
        result = 2.0 * v
        assert result.x == 2.0
        assert result.y == 4.0
        assert result.z == 6.0

    def test_vector_length(self):
        """Test vector length calculation."""
        v = Vector3D(3.0, 4.0, 0.0)
        assert v.length == 5.0

    def test_vector_length_3d(self):
        """Test 3D vector length."""
        v = Vector3D(1.0, 2.0, 2.0)
        assert v.length == 3.0

    def test_vector_normalize(self):
        """Test vector normalization."""
        v = Vector3D(3.0, 0.0, 0.0)
        n = v.normalize()
        assert abs(n.x - 1.0) < 1e-10
        assert abs(n.y) < 1e-10
        assert abs(n.z) < 1e-10

    def test_vector_normalize_unit(self):
        """Test normalizing already unit vector."""
        v = Vector3D(1.0, 0.0, 0.0)
        n = v.normalize()
        assert abs(n.length - 1.0) < 1e-10

    def test_vector_normalize_zero(self):
        """Test normalizing zero vector."""
        v = Vector3D(0.0, 0.0, 0.0)
        n = v.normalize()
        assert n.x == 0.0
        assert n.y == 0.0
        assert n.z == 0.0

    def test_vector_dot_product(self):
        """Test dot product calculation."""
        v1 = Vector3D(1.0, 0.0, 0.0)
        v2 = Vector3D(0.0, 1.0, 0.0)
        assert v1.dot(v2) == 0.0  # Perpendicular

    def test_vector_dot_product_parallel(self):
        """Test dot product of parallel vectors."""
        v1 = Vector3D(1.0, 0.0, 0.0)
        v2 = Vector3D(2.0, 0.0, 0.0)
        assert v1.dot(v2) == 2.0

    def test_vector_distance_to(self):
        """Test distance calculation."""
        v1 = Vector3D(0.0, 0.0, 0.0)
        v2 = Vector3D(3.0, 4.0, 0.0)
        assert v1.distance_to(v2) == 5.0


class TestHoleParameters:
    """Tests for HoleParameters validation."""

    def test_valid_parameters(self):
        """Test valid parameters pass validation."""
        params = HoleParameters(
            diameter=6.0,
            depth=3.0,
            hole_count=6,
            clearance_preferred=2.0,
            clearance_min=0.5,
        )
        errors = params.validate()
        assert len(errors) == 0

    def test_negative_diameter(self):
        """Test negative diameter fails validation."""
        params = HoleParameters(
            diameter=-1.0,
            depth=3.0,
            hole_count=6,
            clearance_preferred=2.0,
            clearance_min=0.5,
        )
        errors = params.validate()
        assert any("diameter" in e.lower() for e in errors)

    def test_zero_diameter(self):
        """Test zero diameter fails validation."""
        params = HoleParameters(
            diameter=0.0,
            depth=3.0,
            hole_count=6,
            clearance_preferred=2.0,
            clearance_min=0.5,
        )
        errors = params.validate()
        assert any("diameter" in e.lower() for e in errors)

    def test_very_small_diameter(self):
        """Test very small diameter generates warning."""
        params = HoleParameters(
            diameter=0.1,
            depth=3.0,
            hole_count=6,
            clearance_preferred=2.0,
            clearance_min=0.5,
        )
        errors = params.validate()
        assert any("small" in e.lower() for e in errors)

    def test_negative_depth(self):
        """Test negative depth fails validation."""
        params = HoleParameters(
            diameter=6.0,
            depth=-1.0,
            hole_count=6,
            clearance_preferred=2.0,
            clearance_min=0.5,
        )
        errors = params.validate()
        assert any("depth" in e.lower() for e in errors)

    def test_zero_hole_count(self):
        """Test zero hole count fails validation."""
        params = HoleParameters(
            diameter=6.0,
            depth=3.0,
            hole_count=0,
            clearance_preferred=2.0,
            clearance_min=0.5,
        )
        errors = params.validate()
        assert any("count" in e.lower() for e in errors)

    def test_large_hole_count(self):
        """Test very large hole count generates warning."""
        params = HoleParameters(
            diameter=6.0,
            depth=3.0,
            hole_count=200,
            clearance_preferred=2.0,
            clearance_min=0.5,
        )
        errors = params.validate()
        assert any("large" in e.lower() for e in errors)

    def test_clearance_min_greater_than_preferred(self):
        """Test clearance min > preferred fails."""
        params = HoleParameters(
            diameter=6.0,
            depth=3.0,
            hole_count=6,
            clearance_preferred=0.5,
            clearance_min=2.0,
        )
        errors = params.validate()
        assert any("clearance" in e.lower() for e in errors)


class TestCutPlaneParameters:
    """Tests for CutPlaneParameters validation."""

    def test_valid_preset_plane(self):
        """Test valid preset plane passes."""
        params = CutPlaneParameters(
            plane_type="Preset Plane",
            preset_plane="XY",
            offset=10.0,
        )
        errors = params.validate()
        assert len(errors) == 0

    def test_valid_model_plane(self):
        """Test valid model plane passes."""
        params = CutPlaneParameters(
            plane_type="Model Plane",
        )
        errors = params.validate()
        assert len(errors) == 0

    def test_invalid_plane_type(self):
        """Test invalid plane type fails."""
        params = CutPlaneParameters(
            plane_type="Invalid",
        )
        errors = params.validate()
        assert any("type" in e.lower() for e in errors)

    def test_invalid_preset_plane(self):
        """Test invalid preset plane fails."""
        params = CutPlaneParameters(
            plane_type="Preset Plane",
            preset_plane="ABC",
        )
        errors = params.validate()
        assert any("preset" in e.lower() for e in errors)

    def test_all_valid_preset_planes(self):
        """Test all valid preset planes."""
        for plane in ["XY", "XZ", "YZ"]:
            params = CutPlaneParameters(
                plane_type="Preset Plane",
                preset_plane=plane,
            )
            errors = params.validate()
            assert len(errors) == 0


class TestGetPresetPlaneNormalAndPoint:
    """Tests for get_preset_plane_normal_and_point function."""

    def test_xy_plane(self):
        """Test XY plane normal and point."""
        normal, point = get_preset_plane_normal_and_point("XY", 0.0)
        assert normal.x == 0.0
        assert normal.y == 0.0
        assert normal.z == 1.0
        assert point.x == 0.0
        assert point.y == 0.0
        assert point.z == 0.0

    def test_xy_plane_with_offset(self):
        """Test XY plane with offset."""
        normal, point = get_preset_plane_normal_and_point("XY", 50.0)
        assert normal.z == 1.0
        assert point.z == 50.0

    def test_xz_plane(self):
        """Test XZ plane normal and point."""
        normal, point = get_preset_plane_normal_and_point("XZ", 0.0)
        assert normal.x == 0.0
        assert normal.y == 1.0
        assert normal.z == 0.0

    def test_yz_plane(self):
        """Test YZ plane normal and point."""
        normal, point = get_preset_plane_normal_and_point("YZ", 0.0)
        assert normal.x == 1.0
        assert normal.y == 0.0
        assert normal.z == 0.0

    def test_invalid_plane(self):
        """Test invalid plane raises error."""
        with pytest.raises(HolePlacementError):
            get_preset_plane_normal_and_point("ABC", 0.0)


class TestCalculateClearanceSteps:
    """Tests for calculate_clearance_steps function."""

    def test_basic_clearance_steps(self):
        """Test basic clearance step calculation."""
        steps = calculate_clearance_steps(2.0, 0.5, 5)
        assert len(steps) == 5
        assert steps[0] == 2.0  # Preferred
        assert steps[-1] == 0.5  # Minimum

    def test_clearance_steps_monotonic(self):
        """Test clearance steps are monotonically decreasing."""
        steps = calculate_clearance_steps(2.0, 0.5, 5)
        for i in range(1, len(steps)):
            assert steps[i] < steps[i - 1]

    def test_equal_clearances(self):
        """Test when preferred equals minimum."""
        steps = calculate_clearance_steps(1.0, 1.0, 5)
        assert len(steps) == 1
        assert steps[0] == 1.0

    def test_min_greater_than_preferred(self):
        """Test when min > preferred returns just min."""
        steps = calculate_clearance_steps(0.5, 2.0, 5)
        assert len(steps) == 1
        assert steps[0] == 2.0


class TestCalculateHoleSpacing:
    """Tests for calculate_hole_spacing function."""

    def test_basic_spacing(self):
        """Test basic spacing calculation."""
        spacing = calculate_hole_spacing(100.0, 10)
        assert spacing == 10.0

    def test_spacing_single_hole(self):
        """Test spacing with single hole."""
        spacing = calculate_hole_spacing(100.0, 1)
        assert spacing == 100.0

    def test_zero_perimeter(self):
        """Test zero perimeter raises error."""
        with pytest.raises(HolePlacementError):
            calculate_hole_spacing(0.0, 10)

    def test_zero_hole_count(self):
        """Test zero hole count raises error."""
        with pytest.raises(HolePlacementError):
            calculate_hole_spacing(100.0, 0)

    def test_negative_perimeter(self):
        """Test negative perimeter raises error."""
        with pytest.raises(HolePlacementError):
            calculate_hole_spacing(-100.0, 10)


class TestCalculateHoleParameterPositions:
    """Tests for calculate_hole_parameter_positions function."""

    def test_basic_positions(self):
        """Test basic position calculation."""
        positions = calculate_hole_parameter_positions(100.0, 4)
        assert len(positions) == 4

    def test_positions_within_range(self):
        """Test all positions are within perimeter."""
        positions = calculate_hole_parameter_positions(100.0, 10)
        for pos in positions:
            assert 0 <= pos < 100.0

    def test_positions_evenly_spaced(self):
        """Test positions are evenly spaced."""
        positions = calculate_hole_parameter_positions(100.0, 4)
        # With 4 holes on 100mm perimeter, spacing is 25mm
        # Positions should be at 12.5, 37.5, 62.5, 87.5 (with half-spacing offset)
        for i in range(1, len(positions)):
            spacing = positions[i] - positions[i - 1]
            assert abs(spacing - 25.0) < 0.001

    def test_zero_hole_count(self):
        """Test zero holes returns empty list."""
        positions = calculate_hole_parameter_positions(100.0, 0)
        assert len(positions) == 0


class TestCalculateInsetDistance:
    """Tests for calculate_inset_distance function."""

    def test_basic_inset(self):
        """Test basic inset calculation."""
        inset = calculate_inset_distance(6.0, 2.0)
        # Inset = clearance + radius = 2.0 + 3.0 = 5.0
        assert inset == 5.0

    def test_zero_clearance(self):
        """Test zero clearance."""
        inset = calculate_inset_distance(6.0, 0.0)
        assert inset == 3.0  # Just the radius


class TestCheckHoleOverlap:
    """Tests for check_hole_overlap function."""

    def test_no_overlap_far(self):
        """Test no overlap when holes are far apart."""
        existing = [Vector3D(0.0, 0.0, 0.0)]
        new_pos = Vector3D(100.0, 0.0, 0.0)
        assert check_hole_overlap(existing, new_pos, 6.0) is True

    def test_overlap_close(self):
        """Test overlap detected when holes are close."""
        existing = [Vector3D(0.0, 0.0, 0.0)]
        new_pos = Vector3D(10.0, 0.0, 0.0)  # 10mm apart
        # Diameter 6mm, min distance = 12mm, so 10mm is overlap
        assert check_hole_overlap(existing, new_pos, 6.0) is False

    def test_exactly_at_limit(self):
        """Test exactly at minimum distance."""
        existing = [Vector3D(0.0, 0.0, 0.0)]
        new_pos = Vector3D(12.0, 0.0, 0.0)  # Exactly 2 * diameter
        # This is exactly at the limit, should be valid
        assert check_hole_overlap(existing, new_pos, 6.0) is True

    def test_empty_existing(self):
        """Test with no existing holes."""
        existing = []
        new_pos = Vector3D(0.0, 0.0, 0.0)
        assert check_hole_overlap(existing, new_pos, 6.0) is True


class TestCalculatePerimeterSearchOffsets:
    """Tests for calculate_perimeter_search_offsets function."""

    def test_basic_offsets(self):
        """Test basic offset calculation."""
        offsets = calculate_perimeter_search_offsets(100.0)
        # Should have both positive and negative offsets
        assert any(o > 0 for o in offsets)
        assert any(o < 0 for o in offsets)

    def test_offset_count(self):
        """Test correct number of offsets."""
        offsets = calculate_perimeter_search_offsets(100.0, 4)
        # 4 percentages * 2 (positive and negative) = 8 offsets
        assert len(offsets) == 8

    def test_offset_values(self):
        """Test offset values are correct percentages."""
        offsets = calculate_perimeter_search_offsets(100.0, 2)
        # Should be 5mm, -5mm, 10mm, -10mm for 100mm segment
        assert 5.0 in offsets
        assert -5.0 in offsets
        assert 10.0 in offsets
        assert -10.0 in offsets


class TestValidateCutParameters:
    """Tests for validate_cut_parameters function."""

    def test_valid_parameters(self):
        """Test valid parameters return no errors."""
        hole_params = HoleParameters(
            diameter=6.0,
            depth=3.0,
            hole_count=6,
            clearance_preferred=2.0,
            clearance_min=0.5,
        )
        plane_params = CutPlaneParameters(
            plane_type="Preset Plane",
            preset_plane="XY",
        )
        errors = validate_cut_parameters(hole_params, plane_params)
        assert len(errors) == 0

    def test_invalid_both(self):
        """Test both invalid returns combined errors."""
        hole_params = HoleParameters(
            diameter=-1.0,
            depth=3.0,
            hole_count=6,
            clearance_preferred=2.0,
            clearance_min=0.5,
        )
        plane_params = CutPlaneParameters(
            plane_type="Invalid",
        )
        errors = validate_cut_parameters(hole_params, plane_params)
        assert len(errors) >= 2


class TestFormatHolePosition:
    """Tests for format_hole_position function."""

    def test_basic_format(self):
        """Test basic formatting."""
        pos = Vector3D(1.5, 2.5, 3.5)
        result = format_hole_position(pos)
        assert "(1.50, 2.50, 3.50)" == result

    def test_custom_precision(self):
        """Test custom precision."""
        pos = Vector3D(1.5555, 2.5555, 3.5555)
        result = format_hole_position(pos, precision=1)
        assert "(1.6, 2.6, 3.6)" == result


class TestFormatOperationSummary:
    """Tests for format_operation_summary function."""

    def test_basic_summary(self):
        """Test basic summary formatting."""
        result = format_operation_summary(
            holes_created=6,
            holes_repositioned=0,
            holes_skipped=0,
            bottom_name="Part_Bottom",
            top_name="Part_Top",
        )
        assert "Part_Bottom" in result
        assert "Part_Top" in result
        assert "6" in result

    def test_summary_with_repositioned(self):
        """Test summary with repositioned holes."""
        result = format_operation_summary(
            holes_created=6,
            holes_repositioned=2,
            holes_skipped=0,
            bottom_name="Part_Bottom",
            top_name="Part_Top",
        )
        assert "Repositioned" in result
        assert "2" in result

    def test_summary_with_skipped(self):
        """Test summary with skipped holes."""
        result = format_operation_summary(
            holes_created=4,
            holes_repositioned=0,
            holes_skipped=2,
            bottom_name="Part_Bottom",
            top_name="Part_Top",
        )
        assert "Skipped" in result
        assert "2" in result
