"""FreeCAD-dependent operations for Cut Object for Magnets macro.

SPDX-License-Identifier: MIT
Copyright (c) 2025 Sean P. Kane (GitHub: spkane)

This module contains FreeCAD-specific operations that require FreeCAD imports.
For testing, use FreeCAD's built-in test framework.
"""

import FreeCAD as App
import Part
from cut_magnets_core import HolePlacementError


def is_plane_object(obj) -> bool:
    """Check if an object is a datum plane or has a planar face.

    Args:
        obj: FreeCAD document object

    Returns:
        True if object is a plane
    """
    if hasattr(obj, "TypeId"):
        if "Plane" in obj.TypeId:
            return True
    return False


def get_object_type(obj) -> str:
    """Get a human-readable type description for an object.

    Args:
        obj: FreeCAD document object

    Returns:
        Human-readable type string
    """
    if hasattr(obj, "TypeId"):
        type_id = obj.TypeId
        if "Part::" in type_id:
            return type_id.replace("Part::", "")
        if "PartDesign::" in type_id:
            return type_id.replace("PartDesign::", "")
        if "Mesh::" in type_id:
            return "Mesh"
        return type_id
    if hasattr(obj, "Shape"):
        return "Shape"
    return ""


def extract_plane_from_datum(plane_obj) -> tuple[App.Vector, App.Vector]:
    """Extract normal and point from a FreeCAD datum plane.

    Args:
        plane_obj: FreeCAD datum plane object

    Returns:
        Tuple of (normal_vector, point_on_plane)
    """
    placement = plane_obj.Placement
    normal = placement.Rotation.multVec(App.Vector(0, 0, 1))
    point = placement.Base
    return normal, point


def extract_plane_from_face(obj, face_idx: int) -> tuple[App.Vector, App.Vector]:
    """Extract normal and point from a planar face.

    Args:
        obj: FreeCAD object containing the face
        face_idx: Index of the face in obj.Shape.Faces

    Returns:
        Tuple of (normal_vector, point_on_plane)
    """
    face = obj.Shape.Faces[face_idx]

    # Get normal at the center of the face
    u_mid = (face.ParameterRange[0] + face.ParameterRange[1]) / 2
    v_mid = (face.ParameterRange[2] + face.ParameterRange[3]) / 2
    normal = face.normalAt(u_mid, v_mid)
    point = face.CenterOfMass

    return normal, point


def create_cutting_box(bbox, normal: App.Vector, point: App.Vector) -> Part.Shape:
    """Create a large cutting box for boolean operations.

    The box represents the half-space "above" the cutting plane.

    Args:
        bbox: BoundBox of the object being cut
        normal: Normal vector of the cutting plane
        point: A point on the cutting plane

    Returns:
        Part.Shape of the cutting box
    """
    size = max(bbox.XLength, bbox.YLength, bbox.ZLength) * 3
    half = size / 2

    # Create a box centered in XY at origin, extending from Z=0 to Z=size
    box = Part.makeBox(size, size, size, App.Vector(-half, -half, 0))

    # Rotate the box so its bottom face aligns with the plane
    z_axis = App.Vector(0, 0, 1)
    rotation = App.Rotation(z_axis, normal)
    box = box.transformed(App.Matrix(rotation.toMatrix()))

    # Translate to pass through the cut point
    box.translate(point)

    return box


def perform_cut(shape: Part.Shape, cutting_box: Part.Shape) -> tuple[Part.Shape, Part.Shape]:
    """Perform the boolean cut operation.

    Args:
        shape: The shape to cut
        cutting_box: The cutting half-space

    Returns:
        Tuple of (bottom_part, top_part)

    Raises:
        HolePlacementError: If cut fails
    """
    try:
        bottom_part = shape.cut(cutting_box)
        top_part = shape.common(cutting_box)
        return bottom_part, top_part
    except Exception as e:
        raise HolePlacementError(f"Failed to cut object: {e!s}") from e


def find_cut_face_center(part: Part.Shape, normal: App.Vector, cut_point: App.Vector) -> App.Vector | None:
    """Find the center of the cut face on a part.

    Args:
        part: The part shape
        normal: Normal vector of the cut plane
        cut_point: A point on the cut plane

    Returns:
        Center point of cut face or None if not found
    """
    best_face = None
    best_dist = float("inf")

    for face in part.Faces:
        face_normal = face.normalAt(0, 0)
        dot = abs(face_normal.dot(normal))
        if dot > 0.99:  # Nearly parallel
            face_center = face.CenterOfMass
            dist_along_normal = abs((face_center - cut_point).dot(normal))
            if dist_along_normal < best_dist:
                best_dist = dist_along_normal
                best_face = face

    if best_face is not None:
        return best_face.CenterOfMass
    return None


def get_outer_wire(face: Part.Face) -> Part.Wire | None:
    """Get the outer wire (longest perimeter) of a face.

    Args:
        face: The face to get the outer wire from

    Returns:
        The outer wire or None if no wires found
    """
    wires = face.Wires
    if not wires:
        return None
    return max(wires, key=lambda w: w.Length)


def get_point_at_length(wire: Part.Wire, length: float) -> App.Vector | None:
    """Get a point on the wire at a specific length along it.

    Args:
        wire: The wire to traverse
        length: Distance along the wire

    Returns:
        Point at that distance, or None if not found
    """
    cumulative_length = 0.0

    for edge in wire.Edges:
        edge_length = edge.Length

        if cumulative_length + edge_length >= length:
            remaining = length - cumulative_length
            param = remaining / edge_length if edge_length > 0 else 0

            first_param = edge.FirstParameter
            last_param = edge.LastParameter
            edge_param = first_param + param * (last_param - first_param)

            try:
                point = edge.valueAt(edge_param)
                return App.Vector(point)
            except Exception:
                return None

        cumulative_length += edge_length

    return None


def create_body_from_shape(doc, shape: Part.Shape, name: str):
    """Create a PartDesign::Body containing the given shape.

    Args:
        doc: FreeCAD document
        shape: The Part.Shape to wrap
        name: Name for the new body

    Returns:
        The created PartDesign::Body object
    """
    # Create Part::Feature to hold the shape
    base_feature_name = f"{name}_Base"
    feature = doc.addObject("Part::Feature", base_feature_name)
    feature.Shape = shape

    # Create PartDesign::Body
    body = doc.addObject("PartDesign::Body", name)
    body.BaseFeature = feature

    # Hide the intermediate Part::Feature
    if hasattr(feature, "ViewObject") and feature.ViewObject:
        feature.ViewObject.Visibility = False

    doc.recompute()
    return body


def get_internal_base_feature(body):
    """Get the internal PartDesign::FeatureBase from a body.

    Args:
        body: The PartDesign::Body to search

    Returns:
        The PartDesign::FeatureBase object

    Raises:
        HolePlacementError: If no FeatureBase is found
    """
    for obj in body.Group:
        if obj.TypeId == "PartDesign::FeatureBase":
            return obj

    raise HolePlacementError(f"Body {body.Label} has no PartDesign::FeatureBase in Group")


def world_to_sketch_coords(world_pos: App.Vector, sketch) -> App.Vector:
    """Transform world coordinates to sketch-local 2D coordinates.

    Args:
        world_pos: Position in world coordinates
        sketch: The Sketcher::SketchObject with placement info

    Returns:
        Position in sketch-local coordinates
    """
    placement = sketch.Placement
    inv_placement = placement.inverse()
    local_pos = inv_placement.multVec(world_pos)
    return App.Vector(local_pos.x, local_pos.y, 0)


def create_hole_sketch(body, cut_face_name: str, positions: list[App.Vector]):
    """Create a sketch with points at hole center positions.

    Args:
        body: The PartDesign::Body to add the sketch to
        cut_face_name: Name of the face to attach the sketch to
        positions: List of hole center positions in world coordinates

    Returns:
        The created Sketcher::SketchObject
    """
    sketch = body.newObject("Sketcher::SketchObject", "HoleCenters")
    base_feature = get_internal_base_feature(body)

    sketch.AttachmentSupport = [(base_feature, cut_face_name)]
    sketch.MapMode = "FlatFace"

    App.ActiveDocument.recompute()

    for pos in positions:
        local_pos = world_to_sketch_coords(pos, sketch)
        sketch.addGeometry(
            Part.Point(App.Vector(local_pos.x, local_pos.y, 0)),
            False,
        )

    App.ActiveDocument.recompute()
    return sketch


def create_hole_feature(body, sketch, diameter: float, depth: float):
    """Create a PartDesign::Hole feature from a sketch.

    Args:
        body: The PartDesign::Body containing the sketch
        sketch: Sketch with points defining hole centers
        diameter: Hole diameter in mm
        depth: Hole depth in mm

    Returns:
        The created PartDesign::Hole feature
    """
    hole = body.newObject("PartDesign::Hole", "MagnetHoles")
    hole.Profile = sketch
    hole.Diameter = diameter
    hole.Depth = depth
    hole.DepthType = "Dimension"
    hole.Threaded = False
    hole.HoleCutType = "None"

    App.ActiveDocument.recompute()
    return hole


def is_hole_safe(
    center: App.Vector,
    direction: App.Vector,
    part: Part.Shape,
    diameter: float,
    depth: float,
    clearance: float,
) -> bool:
    """Check if a hole at this position would penetrate the outer surface.

    Args:
        center: Center point of hole on cut surface
        direction: Direction of hole (into the part)
        part: Part shape to check against
        diameter: Hole diameter
        depth: Hole depth
        clearance: Clearance from hole edge to object surface

    Returns:
        True if hole is safe, False if it would penetrate
    """
    dir_normalized = App.Vector(direction).normalize()

    radius_check = (diameter / 2) + clearance
    start_offset = 0.5

    start_pos = center + (dir_normalized * start_offset)
    test_length = depth - start_offset

    if test_length <= 0:
        return True

    test_cylinder = Part.makeCylinder(radius_check, test_length, start_pos, dir_normalized)

    try:
        intersection = part.common(test_cylinder)
        cylinder_vol = test_cylinder.Volume
        intersection_vol = intersection.Volume

        if intersection_vol < cylinder_vol * 0.95:
            return False

        return True
    except Exception:
        return False


def detect_existing_holes(shape: Part.Shape, target_radius: float) -> list[dict]:
    """Detect existing magnet holes in a shape.

    Args:
        shape: The shape to search for holes
        target_radius: Target radius to match (with tolerance)

    Returns:
        List of dicts with hole info: center, axis, radius, depth, face_center
    """
    holes = []

    for face in shape.Faces:
        if face.Surface.__class__.__name__ != "Cylinder":
            continue

        radius = face.Surface.Radius

        # Only consider holes with radius close to target or small holes
        if radius > 10 and abs(radius - target_radius) > target_radius * 0.5:
            continue

        axis = face.Surface.Axis
        center = face.Surface.Center

        bbox = face.BoundBox
        depth = max(bbox.XLength, bbox.YLength, bbox.ZLength)

        holes.append(
            {
                "center": App.Vector(center),
                "axis": App.Vector(axis),
                "radius": radius,
                "depth": depth,
                "face_center": face.CenterOfMass,
            }
        )

    return holes


def project_hole_to_plane(hole: dict, cut_normal: App.Vector, cut_point: App.Vector) -> App.Vector | None:
    """Project an existing hole position onto a cut plane.

    Args:
        hole: Hole info dict from detect_existing_holes
        cut_normal: Normal vector of the cut plane
        cut_point: A point on the cut plane

    Returns:
        Position on the cut plane, or None if not aligned
    """
    hole_axis = hole["axis"]
    hole_center = hole["center"]

    # Check if hole axis is roughly parallel to cut normal
    dot = abs(hole_axis.dot(cut_normal))
    if dot < 0.7:
        return None

    denominator = hole_axis.dot(cut_normal)
    if abs(denominator) < 0.001:
        return None

    t = (cut_point - hole_center).dot(cut_normal) / denominator
    intersection = hole_center + hole_axis * t

    return intersection


def count_cylindrical_faces(shape: Part.Shape) -> int:
    """Count cylindrical faces (holes) in a shape.

    Args:
        shape: The shape to examine

    Returns:
        Number of cylindrical faces
    """
    count = 0
    for face in shape.Faces:
        if face.Surface.__class__.__name__ == "Cylinder":
            count += 1
    return count
