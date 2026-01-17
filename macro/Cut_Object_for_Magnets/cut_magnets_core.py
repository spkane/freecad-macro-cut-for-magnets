"""Core business logic for Cut Object for Magnets macro.

SPDX-License-Identifier: MIT
Copyright (c) 2025 Sean P. Kane (GitHub: spkane)

This module contains pure Python logic that doesn't depend on FreeCAD,
making it testable with standard pytest.
"""

import math
from dataclasses import dataclass


class HolePlacementError(Exception):
    """Raised when hole placement fails."""

    pass


@dataclass
class Vector3D:
    """Simple 3D vector for pure Python calculations.

    This class provides basic vector operations without FreeCAD dependency,
    useful for testing core logic.
    """

    x: float
    y: float
    z: float

    def __add__(self, other: "Vector3D") -> "Vector3D":
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vector3D") -> "Vector3D":
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> "Vector3D":
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: float) -> "Vector3D":
        return self.__mul__(scalar)

    @property
    def length(self) -> float:
        """Calculate vector length (magnitude)."""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self) -> "Vector3D":
        """Return a normalized (unit length) vector."""
        length = self.length
        if length < 1e-10:
            return Vector3D(0, 0, 0)
        return Vector3D(self.x / length, self.y / length, self.z / length)

    def dot(self, other: "Vector3D") -> float:
        """Calculate dot product with another vector."""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def distance_to(self, other: "Vector3D") -> float:
        """Calculate distance to another point (vector)."""
        return (self - other).length


@dataclass
class HoleParameters:
    """Parameters for magnet hole creation."""

    diameter: float
    depth: float
    hole_count: int
    clearance_preferred: float
    clearance_min: float

    def validate(self) -> list[str]:
        """Validate parameters and return list of errors.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if self.diameter <= 0:
            errors.append("Hole diameter must be positive")
        elif self.diameter < 0.5:
            errors.append("Hole diameter is very small (< 0.5mm)")

        if self.depth <= 0:
            errors.append("Hole depth must be positive")
        elif self.depth < 0.5:
            errors.append("Hole depth is very small (< 0.5mm)")

        if self.hole_count <= 0:
            errors.append("Hole count must be at least 1")
        elif self.hole_count > 100:
            errors.append("Hole count is very large (> 100)")

        if self.clearance_min <= 0:
            errors.append("Minimum clearance must be positive")

        if self.clearance_preferred < self.clearance_min:
            errors.append("Preferred clearance must be >= minimum clearance")

        return errors


@dataclass
class CutPlaneParameters:
    """Parameters for cut plane definition."""

    plane_type: str  # "Preset Plane" or "Model Plane"
    preset_plane: str = "XY"  # XY, XZ, or YZ
    offset: float = 0.0  # Offset for preset planes

    def validate(self) -> list[str]:
        """Validate parameters and return list of errors."""
        errors = []

        if self.plane_type not in ("Preset Plane", "Model Plane"):
            errors.append(f"Invalid plane type: {self.plane_type}")

        if self.plane_type == "Preset Plane":
            if self.preset_plane not in ("XY", "XZ", "YZ"):
                errors.append(f"Invalid preset plane: {self.preset_plane}")

        return errors


def get_preset_plane_normal_and_point(plane: str, offset: float) -> tuple[Vector3D, Vector3D]:
    """Get normal vector and point for a preset plane.

    Args:
        plane: Plane name (XY, XZ, or YZ)
        offset: Offset from origin along plane normal

    Returns:
        Tuple of (normal_vector, point_on_plane)

    Raises:
        HolePlacementError: If plane is invalid
    """
    if plane == "XY":
        normal = Vector3D(0, 0, 1)
        point = Vector3D(0, 0, offset)
    elif plane == "XZ":
        normal = Vector3D(0, 1, 0)
        point = Vector3D(0, offset, 0)
    elif plane == "YZ":
        normal = Vector3D(1, 0, 0)
        point = Vector3D(offset, 0, 0)
    else:
        raise HolePlacementError(f"Unknown preset plane: {plane}")

    return normal, point


def calculate_clearance_steps(clearance_preferred: float, clearance_min: float, num_steps: int = 5) -> list[float]:
    """Calculate clearance values to try when repositioning holes.

    When a hole fails safety check at preferred clearance, we try
    progressively smaller clearances down to minimum.

    Args:
        clearance_preferred: Preferred clearance (starting point)
        clearance_min: Minimum acceptable clearance
        num_steps: Number of steps from preferred to minimum

    Returns:
        List of clearance values from preferred to minimum
    """
    if clearance_preferred <= clearance_min:
        return [clearance_min]

    step_size = (clearance_preferred - clearance_min) / (num_steps - 1)
    return [clearance_preferred - (i * step_size) for i in range(num_steps)]


def calculate_hole_spacing(perimeter_length: float, hole_count: int) -> float:
    """Calculate even spacing between holes along a perimeter.

    For N holes distributed around a closed perimeter, the spacing between
    adjacent holes (including wrap-around from last to first) equals
    perimeter_length divided by hole_count.

    Args:
        perimeter_length: Total perimeter length
        hole_count: Number of holes to distribute

    Returns:
        Spacing between holes

    Raises:
        HolePlacementError: If inputs are invalid
    """
    if perimeter_length <= 0:
        raise HolePlacementError("Perimeter length must be positive")
    if hole_count <= 0:
        raise HolePlacementError("Hole count must be positive")

    return perimeter_length / hole_count


def calculate_hole_parameter_positions(perimeter_length: float, hole_count: int) -> list[float]:
    """Calculate parameter positions along perimeter for each hole.

    Holes are evenly distributed with a half-spacing offset to avoid
    starting exactly at position 0 (often a corner/vertex).

    Args:
        perimeter_length: Total perimeter length
        hole_count: Number of holes

    Returns:
        List of parameter positions (0 to perimeter_length)
    """
    if hole_count <= 0:
        return []

    spacing = calculate_hole_spacing(perimeter_length, hole_count)
    positions = []

    for i in range(hole_count):
        # Place holes evenly spaced with offset to avoid corners
        param = (i * spacing) + (spacing / 2)
        # Wrap around if we exceed perimeter length
        if param >= perimeter_length:
            param = param - perimeter_length
        positions.append(param)

    return positions


def calculate_inset_distance(diameter: float, clearance: float) -> float:
    """Calculate how far to inset holes from the edge.

    Holes should be placed inward from the edge by clearance + radius.

    Args:
        diameter: Hole diameter
        clearance: Distance from hole edge to object edge

    Returns:
        Distance to move inward from edge
    """
    return clearance + (diameter / 2)


def check_hole_overlap(existing_positions: list[Vector3D], new_position: Vector3D, diameter: float) -> bool:
    """Check if a new hole position would overlap with existing holes.

    Holes must have at least one hole diameter of space between them.

    Args:
        existing_positions: List of already accepted hole positions
        new_position: The new position to check
        diameter: Hole diameter

    Returns:
        True if position is valid (no overlap), False if it would overlap
    """
    # Minimum distance = 2 * diameter (one hole width between holes)
    min_distance = diameter * 2

    for existing_pos in existing_positions:
        dist = new_position.distance_to(existing_pos)
        if dist < min_distance:
            return False

    return True


def calculate_perimeter_search_offsets(segment_length: float, num_offsets: int = 4) -> list[float]:
    """Calculate offsets to try when searching for alternative hole positions.

    When a hole fails safety check, we search along the perimeter in both
    directions. This generates offsets from 5% to 20% of segment length.

    Args:
        segment_length: Length of one segment (perimeter / hole_count)
        num_offsets: Number of offset percentages to try

    Returns:
        List of offset values (positive and negative)
    """
    offsets = []
    percentages = [0.05, 0.10, 0.15, 0.20][:num_offsets]

    for pct in percentages:
        offsets.append(segment_length * pct)
        offsets.append(-segment_length * pct)

    return offsets


def validate_cut_parameters(hole_params: HoleParameters, plane_params: CutPlaneParameters) -> list[str]:
    """Validate all cut parameters.

    Args:
        hole_params: Hole parameters to validate
        plane_params: Plane parameters to validate

    Returns:
        Combined list of all validation errors
    """
    errors = []
    errors.extend(hole_params.validate())
    errors.extend(plane_params.validate())
    return errors


def format_hole_position(position: Vector3D, precision: int = 2) -> str:
    """Format a hole position for display.

    Args:
        position: The position vector
        precision: Number of decimal places

    Returns:
        Formatted string like "(1.50, 2.00, 3.25)"
    """
    return f"({position.x:.{precision}f}, {position.y:.{precision}f}, {position.z:.{precision}f})"


def format_operation_summary(
    holes_created: int,
    holes_repositioned: int,
    holes_skipped: int,
    bottom_name: str,
    top_name: str,
) -> str:
    """Format a summary of the cut operation results.

    Args:
        holes_created: Number of holes successfully created
        holes_repositioned: Number of holes that were moved
        holes_skipped: Number of holes that couldn't be placed
        bottom_name: Name of the bottom piece
        top_name: Name of the top piece

    Returns:
        Formatted summary string
    """
    lines = [
        "Cut operation complete:",
        f"  Created: {bottom_name} and {top_name}",
        f"  Holes: {holes_created} created",
    ]

    if holes_repositioned > 0:
        lines.append(f"  Repositioned: {holes_repositioned} holes adjusted for clearance")

    if holes_skipped > 0:
        lines.append(f"  Skipped: {holes_skipped} holes couldn't be placed safely")

    return "\n".join(lines)
