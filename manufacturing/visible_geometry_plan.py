from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from domain.core_types import NodeCategory, NodeRole
from domain.system32 import System32Engine


@dataclass(frozen=True)
class VisibleGeometryFeatureSpec:
    name: str
    kind: str
    node_id: str
    placement: tuple[float, float, float]
    size: tuple[float, float, float]
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0)
    color: tuple[float, float, float] = (0.6, 0.6, 0.6)
    label: str = ""
    prototype: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class VisibleGeometryPlan:
    features: tuple[VisibleGeometryFeatureSpec, ...]
    production_backed_lines: tuple[str, ...] = field(default_factory=tuple)
    prototype_lines: tuple[str, ...] = field(default_factory=tuple)


def build_visible_geometry_plan(project) -> VisibleGeometryPlan:
    graph = getattr(project, "graph", None)
    nodes = list(getattr(graph, "all_nodes", lambda: [])() or [])
    physical_nodes = [node for node in nodes if _is_physical_node(node)]
    cabinet_depth = float(getattr(getattr(project, "topology", None), "d", 600.0) or 600.0)

    features = []
    production_backed_lines = []
    prototype_lines = []

    for node in physical_nodes:
        features.extend(
            _panel_geometry_features(node, project, cabinet_depth)
        )

    for node in physical_nodes:
        features.extend(
            _manufacturing_details_for_node(node, project, cabinet_depth)
        )

    if _has_real_wall_mount_data(project):
        production_backed_lines.append("Wall mount data available from project model")
    elif any(_role_value(node) == "BACK_PANEL" for node in physical_nodes):
        prototype_lines.append(
            "Wall mount shown as labeled prototype geometry until real data exists"
        )

    return VisibleGeometryPlan(
        features=tuple(features),
        production_backed_lines=tuple(production_backed_lines),
        prototype_lines=tuple(prototype_lines),
    )


def _panel_geometry_features(node, project, cabinet_depth):
    role = _role_value(node)
    features = []

    if role == "BACK_PANEL":
        features.extend(_back_panel_groove_features(node, cabinet_depth))
        features.extend(_wall_mount_prototype_features(node, cabinet_depth, project))

    if role in {"SIDE_PANEL", "DIVIDER"}:
        features.extend(_side_panel_drilling_features(node, project, cabinet_depth))
        features.extend(_hinge_plate_features(node, project, cabinet_depth))
        features.extend(_drawer_slide_features(node, project, cabinet_depth))

    if role == "DOOR_PANEL":
        features.extend(_hinge_cup_features(node, project, cabinet_depth))

    return features


def _manufacturing_details_for_node(node, project, cabinet_depth):
    role = _role_value(node)
    if role not in {"SIDE_PANEL", "DIVIDER"}:
        return []

    features = []
    features.extend(_confirmat_minifix_features(node, project, cabinet_depth))
    features.extend(_screw_features(node, project, cabinet_depth))
    return features


def _back_panel_groove_features(node, cabinet_depth):
    base_x, actual_y, base_z = _panel_world_origin(node, cabinet_depth)
    width, depth, height = _panel_render_dimensions(node)
    groove_depth = 4.0
    groove_thickness = 2.0

    features = [
        VisibleGeometryFeatureSpec(
            name=f"{node.identity.key}_Groove_Left",
            kind="back_panel_groove",
            node_id=node.identity.key,
            placement=(base_x + max(width - groove_thickness, 0.0), actual_y + max(depth - groove_depth, 0.0), base_z),
            size=(groove_thickness, groove_depth, height),
            color=(0.35, 0.22, 0.12),
            label="Back panel groove line",
        ),
        VisibleGeometryFeatureSpec(
            name=f"{node.identity.key}_Groove_Right",
            kind="back_panel_groove",
            node_id=node.identity.key,
            placement=(base_x, actual_y + max(depth - groove_depth, 0.0), base_z),
            size=(groove_thickness, groove_depth, height),
            color=(0.35, 0.22, 0.12),
            label="Back panel groove line",
        ),
    ]

    if _role_value(node) == "BACK_PANEL":
        features.append(
            VisibleGeometryFeatureSpec(
                name=f"{node.identity.key}_Groove_Slot",
                kind="back_panel_groove",
                node_id=node.identity.key,
                placement=(base_x + 4.0, actual_y + 1.0, base_z + 4.0),
                size=(max(width - 8.0, 8.0), 2.0, 2.0),
                color=(0.28, 0.18, 0.10),
                label="Back panel groove slot",
                prototype=False,
            )
        )

    return features


def _hinge_cup_features(node, project, cabinet_depth):
    placements = _placements_for_intent(project, "INTENT_HINGE", node.identity.key)
    if not placements:
        placements = [
            {
                "offset_x": 22.5,
                "offset_y": offset_y,
                "prototype": True,
            }
            for offset_y in System32Engine.hinge_positions(float(getattr(node, "height", 0.0) or 0.0))
        ]

    base_x, actual_y, base_z = _panel_world_origin(node, cabinet_depth)
    width, depth, height = _panel_render_dimensions(node)
    features = []

    for index, placement in enumerate(placements, start=1):
        offset_x = float(placement["offset_x"])
        offset_y = float(placement["offset_y"])
        prototype = bool(placement["prototype"])
        features.append(
            VisibleGeometryFeatureSpec(
                name=f"{node.identity.key}_Hinge_Cup_Hole_{index}",
                kind="hinge_cup_hole",
                node_id=node.identity.key,
                placement=(
                    base_x + max(min(offset_x, width - 18.0), 18.0),
                    actual_y + max(depth - 2.5, 0.0),
                    base_z + offset_y,
                ),
                size=(35.0, 3.0, 35.0),
                rotation=(90.0, 0.0, 0.0),
                color=(0.85, 0.75, 0.25),
                label="Hinge cup drilling",
                prototype=prototype,
            )
        )

    return features


def _hinge_plate_features(node, project, cabinet_depth):
    placements = _placements_for_intent(project, "INTENT_HINGE", None)
    matching = [
        placement for placement in placements
        if placement["host_node_id"] == node.identity.key
    ]
    if not matching:
        matching = [
            {
                "offset_x": 22.5,
                "offset_y": offset_y,
                "prototype": True,
            }
            for offset_y in System32Engine.hinge_positions(float(getattr(node, "height", 0.0) or 0.0))
        ]

    base_x, actual_y, base_z = _panel_world_origin(node, cabinet_depth)
    width, depth, _height = _panel_render_dimensions(node)
    features = []

    for index, placement in enumerate(matching, start=1):
        offset_y = float(placement["offset_y"])
        features.append(
            VisibleGeometryFeatureSpec(
                name=f"{node.identity.key}_Hinge_Plate_Position_{index}",
                kind="hinge_plate_position",
                node_id=node.identity.key,
                placement=(
                    base_x + max(width - 22.0, 0.0),
                    actual_y + 2.0,
                    base_z + offset_y - 8.0,
                ),
                size=(18.0, 3.0, 32.0),
                color=(0.55, 0.55, 0.62),
                label="Hinge plate location",
                prototype=bool(placement["prototype"]),
            )
        )

    return features


def _side_panel_drilling_features(node, project, cabinet_depth):
    drill_positions = []
    for op in getattr(node, "machining_ops", []) or []:
        op_type = str(getattr(op, "op_type", "") or "").upper()
        if op_type != "DRILL":
            continue
        metadata = getattr(op, "metadata", None) or {}
        if str(metadata.get("hardware_intent", "") or "").upper() != "INTENT_SHELF_PIN":
            continue
        drill_positions.append(
            (
                float(getattr(op, "local_y", 0.0) or 0.0),
                str(getattr(op, "face", "") or "").upper(),
                getattr(op, "metadata", None) or {},
            )
        )

    if not drill_positions:
        return []

    base_x, actual_y, base_z = _panel_world_origin(node, cabinet_depth)
    width, depth, _height = _panel_render_dimensions(node)
    features = []
    for index, (z_position, face, metadata) in enumerate(drill_positions, start=1):
        features.append(
            VisibleGeometryFeatureSpec(
                name=f"{node.identity.key}_Shelf_Pin_Hole_{index}",
                kind="shelf_pin_hole",
                node_id=node.identity.key,
                placement=(
                    base_x + (1.5 if _panel_is_left(node) else max(width - 1.5, 0.0)),
                    actual_y + (depth * 0.5),
                    base_z + z_position,
                ),
                size=(5.0, 5.0, 5.0),
                color=(0.2, 0.6, 0.95),
                label="Shelf pin hole row",
                prototype=bool(metadata.get("prototype", False)),
                notes=(str(metadata.get("hardware_intent", "")), face),
            )
        )
    return features


def _confirmat_minifix_features(node, project, cabinet_depth):
    features = []
    for op in getattr(node, "machining_ops", []) or []:
        op_type = str(getattr(op, "op_type", "") or "").upper()
        if op_type != "DRILL":
            continue
        metadata = getattr(op, "metadata", None) or {}
        intent = str(metadata.get("hardware_intent", "") or "").upper()
        if intent not in {"INTENT_MINIFIX_15", "INTENT_CONFIRMAT_50"}:
            continue
        features.extend(
            _feature_from_drill_operation(
                node,
                cabinet_depth,
                op,
                name_prefix="Fastener_Drill",
                color=(0.9, 0.45, 0.15),
                label="Fastener drilling indication",
                prototype=False,
            )
        )

    return features


def _screw_features(node, project, cabinet_depth):
    features = []
    for op in getattr(node, "machining_ops", []) or []:
        op_type = str(getattr(op, "op_type", "") or "").upper()
        if op_type != "DRILL":
            continue
        metadata = getattr(op, "metadata", None) or {}
        intent = str(metadata.get("hardware_intent", "") or "").upper()
        if intent not in {"INTENT_SCREW", "INTENT_PANEL_SCREW"}:
            continue
        features.extend(
            _feature_from_drill_operation(
                node,
                cabinet_depth,
                op,
                name_prefix="Screw_Drill",
                color=(0.65, 0.4, 0.2),
                label="Screw drilling indication",
                prototype=False,
            )
        )

    return features


def _drawer_slide_features(node, project, cabinet_depth):
    placements = _placements_for_intent(project, "INTENT_DRAWER_SLIDE", node.identity.key)
    if not placements:
        return []

    base_x, actual_y, base_z = _panel_world_origin(node, cabinet_depth)
    width, depth, _height = _panel_render_dimensions(node)
    features = []

    for index, placement in enumerate(placements, start=1):
        side = str(placement["side"]).upper()
        z_position = float(placement["offset_y"])
        x_position = base_x + (2.0 if side == "LEFT" else max(width - 5.0, 0.0))
        features.append(
            VisibleGeometryFeatureSpec(
                name=f"{node.identity.key}_Drawer_Slide_Line_{index}",
                kind="drawer_slide_line",
                node_id=node.identity.key,
                placement=(x_position, actual_y + 4.0, base_z + z_position),
                size=(3.0, max(depth - 8.0, 4.0), 3.0),
                color=(0.8, 0.2, 0.9),
                label="Drawer slide hole line",
                prototype=bool(placement["prototype"]),
            )
        )

    return features


def _wall_mount_prototype_features(node, cabinet_depth, project):
    if _has_real_wall_mount_data(project):
        return []

    base_x, actual_y, base_z = _panel_world_origin(node, cabinet_depth)
    width, depth, height = _panel_render_dimensions(node)
    features = [
        VisibleGeometryFeatureSpec(
            name=f"{node.identity.key}_Wall_Mount_Rail",
            kind="wall_mount_prototype",
            node_id=node.identity.key,
            placement=(base_x + 18.0, actual_y + max(depth - 5.0, 0.0), base_z + max(height - 35.0, 0.0)),
            size=(max(width - 36.0, 80.0), 5.0, 18.0),
            color=(0.15, 0.75, 0.6),
            label="Wall mount prototype rail",
            prototype=True,
        ),
        VisibleGeometryFeatureSpec(
            name=f"{node.identity.key}_Wall_Mount_Bracket_Left",
            kind="wall_mount_prototype",
            node_id=node.identity.key,
            placement=(base_x + 24.0, actual_y + max(depth - 10.0, 0.0), base_z + max(height - 30.0, 0.0)),
            size=(12.0, 12.0, 24.0),
            color=(0.15, 0.75, 0.6),
            label="Wall mount prototype bracket",
            prototype=True,
        ),
        VisibleGeometryFeatureSpec(
            name=f"{node.identity.key}_Wall_Mount_Bracket_Right",
            kind="wall_mount_prototype",
            node_id=node.identity.key,
            placement=(base_x + max(width - 36.0, 36.0), actual_y + max(depth - 10.0, 0.0), base_z + max(height - 30.0, 0.0)),
            size=(12.0, 12.0, 24.0),
            color=(0.15, 0.75, 0.6),
            label="Wall mount prototype bracket",
            prototype=True,
        ),
    ]
    return features


def _feature_from_drill_operation(node, cabinet_depth, operation, name_prefix, color, label, prototype):
    base_x, actual_y, base_z = _panel_world_origin(node, cabinet_depth)
    width, depth, _height = _panel_render_dimensions(node)
    local_x = float(getattr(operation, "local_x", 0.0) or 0.0)
    local_y = float(getattr(operation, "local_y", 0.0) or 0.0)
    metadata = getattr(operation, "metadata", None) or {}
    intent = str(metadata.get("hardware_intent", "") or "")
    face = str(getattr(operation, "face", "") or "").upper()
    return [
        VisibleGeometryFeatureSpec(
            name=f"{node.identity.key}_{name_prefix}_{int(round(local_y))}",
            kind="drilling_indicator",
            node_id=node.identity.key,
            placement=(
                base_x + local_x,
                actual_y + max(depth - 3.0, 0.0),
                base_z + local_y,
            ),
            size=(5.0, 5.0, 5.0),
            color=color,
            label=label,
            prototype=prototype,
            notes=(intent, face),
        )
    ]


def _placements_for_intent(project, intent, node_id):
    placements = []
    for placement in _placements(project):
        if placement["intent"] != intent:
            continue
        if node_id is not None and placement["host_node_id"] != node_id and placement["target_node_id"] != node_id:
            continue
        placements.append(placement)
    return placements


def _placements(project):
    placements = []
    for placement in list(getattr(project, "placements", []) or []):
        anchor = getattr(placement, "anchor", None)
        placements.append(
            {
                "host_node_id": str(getattr(placement, "host_node_id", "") or ""),
                "target_node_id": str(getattr(placement, "target_node_id", "") or ""),
                "intent": str(getattr(placement, "hardware_intent", "") or ""),
                "offset_x": float(getattr(anchor, "offset_x", 0.0) or 0.0),
                "offset_y": float(getattr(anchor, "offset_y", 0.0) or 0.0),
                "face": str(getattr(anchor, "face", "") or "").upper(),
                "side": "LEFT" if str(getattr(anchor, "face", "") or "").upper() == "LEFT" else "RIGHT",
                "prototype": False,
            }
        )
    return placements


def _panel_world_origin(node, cabinet_depth):
    base_x = float(getattr(getattr(node, "transform", None), "x", 0.0) or 0.0)
    base_y = float(getattr(getattr(node, "transform", None), "y", 0.0) or 0.0)
    base_z = float(getattr(getattr(node, "transform", None), "z", 0.0) or 0.0)
    _width, depth, _height = _panel_render_dimensions(node)
    actual_y = cabinet_depth - base_y - depth
    return base_x, actual_y, base_z


def _panel_render_dimensions(node):
    role = _role_value(node)
    width = float(getattr(node, "width", 0.0) or 0.0)
    depth = float(getattr(node, "depth", 0.0) or 0.0)
    height = float(getattr(node, "height", 0.0) or 0.0)
    thickness = float(getattr(node, "thickness", 0.0) or 0.0)

    if role in {"SIDE_PANEL", "DIVIDER"}:
        return thickness, width, height
    if role in {"TOP_PANEL", "BOTTOM_PANEL", "SHELF"}:
        return width, depth, thickness
    if role in {"BACK_PANEL", "DOOR_PANEL"}:
        return width, thickness, height
    return width, depth, height


def _role_value(node):
    role = getattr(node, "role", NodeRole.UNKNOWN)
    return str(getattr(role, "value", role) or "").upper()


def _panel_is_left(node):
    key = str(getattr(getattr(node, "identity", None), "key", "") or "").upper()
    return key.endswith("_SIDE_L") or key.endswith("_LEFT")


def _is_physical_node(node) -> bool:
    category = getattr(node, "category", None)
    if category is None:
        return True
    return str(getattr(category, "value", category) or "").upper() == "PHYSICAL"


def _has_real_wall_mount_data(project) -> bool:
    for attribute in (
        "wall_mount_points",
        "wall_mount_capability",
        "mounting_points",
        "suspension_hardware",
    ):
        if getattr(project, attribute, None):
            return True
    return False
