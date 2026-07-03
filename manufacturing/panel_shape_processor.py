from __future__ import annotations

from typing import Iterable, Sequence

try:
    import Part
except ImportError:  # pragma: no cover - test environment fallback
    Part = None

try:
    from FreeCAD import Rotation, Vector
except ImportError:  # pragma: no cover - test environment fallback
    Rotation = None
    Vector = None

from core.logging_config import logger


def process_panel_shape(base_shape, panel_node, features: Iterable, panel_origin=None):
    """Apply supported visible machining features to a panel solid.

    V1 supports production-backed `back_panel_groove`, `shelf_pin_hole`,
    `drawer_slide_line`, `hinge_cup_hole`, and `minifix_hole` features and
    passes through `edge_banding_strip` markers without altering the solid.
    All other feature kinds are left untouched.
    """
    if base_shape is None:
        return None

    panel_key = _panel_key(panel_node)
    relevant_features = [
        feature
        for feature in list(features or [])
        if _feature_matches_panel(feature, panel_key)
        and _feature_supported_for_panel(panel_node, feature)
    ]

    if not relevant_features:
        return base_shape

    if Part is None:
        logger.warning(
            "Panel shape processor skipped machining for %s because Part is unavailable",
            panel_key,
        )
        return base_shape

    origin = _panel_origin(panel_node, panel_origin)
    if origin is None:
        logger.warning(
            "Panel shape processor skipped machining for %s because panel origin is unavailable",
            panel_key,
        )
        return base_shape

    processed = base_shape
    for feature in relevant_features:
        if _feature_kind(feature) == "edge_banding_strip":
            continue
        tool = _make_feature_tool(feature, origin)
        if tool is None:
            logger.warning(
                "Panel shape processor skipped unsupported groove tool for %s / %s",
                panel_key,
                getattr(feature, "name", "<unnamed>"),
            )
            continue

        try:
            processed = processed.cut(tool)
        except Exception as exc:  # pragma: no cover - safety path
            logger.warning(
                "Panel shape processor preserved original shape for %s after groove cut failure: %s",
                panel_key,
                exc,
            )
            return base_shape

    return processed


def _panel_key(panel_node) -> str:
    if isinstance(panel_node, str):
        return panel_node

    identity = getattr(panel_node, "identity", None)
    if identity is not None:
        return str(getattr(identity, "key", "") or "")

    return str(getattr(panel_node, "key", "") or "")


def _feature_matches_panel(feature, panel_key: str) -> bool:
    if not panel_key:
        return False
    return str(getattr(feature, "node_id", "") or "") == panel_key


def _feature_kind(feature) -> str:
    return str(getattr(feature, "kind", "") or "").lower()


def _panel_role(panel_node) -> str:
    role = getattr(panel_node, "role", "")
    role_value = str(getattr(role, "value", role) or "").upper()
    if role_value:
        return role_value

    panel_key = _panel_key(panel_node).upper()
    if "BACK" in panel_key:
        return "BACK_PANEL"
    if "SIDE" in panel_key:
        return "SIDE_PANEL"
    if "TOP" in panel_key:
        return "TOP_PANEL"
    if "BOTTOM" in panel_key:
        return "BOTTOM_PANEL"
    if "DIVIDER" in panel_key:
        return "DIVIDER"
    if "DOOR" in panel_key:
        return "DOOR_PANEL"
    return ""


def _feature_supported_for_panel(panel_node, feature) -> bool:
    feature_kind = _feature_kind(feature)
    panel_role = _panel_role(panel_node)

    if feature_kind == "back_panel_groove":
        return panel_role == "BACK_PANEL"
    if feature_kind == "shelf_pin_hole":
        return panel_role in {"SIDE_PANEL", "DIVIDER"}
    if feature_kind == "drawer_slide_line":
        return panel_role == "SIDE_PANEL"
    if feature_kind == "hinge_plate_position":
        return panel_role == "SIDE_PANEL"
    if feature_kind == "hinge_cup_hole":
        return panel_role == "DOOR_PANEL"
    if feature_kind == "minifix_hole":
        return panel_role in {"SIDE_PANEL", "TOP_PANEL", "BOTTOM_PANEL", "DIVIDER"}
    if feature_kind == "confirmat_hole":
        return panel_role in {"SIDE_PANEL", "TOP_PANEL", "BOTTOM_PANEL", "DIVIDER"}
    if feature_kind == "edge_banding_strip":
        return panel_role in {
            "SIDE_PANEL",
            "TOP_PANEL",
            "BOTTOM_PANEL",
            "SHELF",
            "DIVIDER",
            "DOOR_PANEL",
            "DRAWER_FACE",
            "PLINTH",
        }
    return False


def _panel_origin(panel_node, panel_origin):
    if panel_origin is not None:
        return tuple(float(value) for value in panel_origin)

    transform = getattr(panel_node, "transform", None)
    if transform is None:
        return None

    return (
        float(getattr(transform, "x", 0.0) or 0.0),
        float(getattr(transform, "y", 0.0) or 0.0),
        float(getattr(transform, "z", 0.0) or 0.0),
    )


def _make_feature_tool(feature, panel_origin):
    size = getattr(feature, "size", (0.0, 0.0, 0.0)) or (0.0, 0.0, 0.0)
    sx, sy, sz = (max(float(size[0]), 0.1), max(float(size[1]), 0.1), max(float(size[2]), 0.1))
    placement = getattr(feature, "placement", (0.0, 0.0, 0.0)) or (0.0, 0.0, 0.0)
    offset = (
        float(placement[0]) - float(panel_origin[0]),
        float(placement[1]) - float(panel_origin[1]),
        float(placement[2]) - float(panel_origin[2]),
    )

    tool = Part.makeBox(sx, sy, sz)
    if any(abs(component) > 0.0 for component in offset):
        _translate_shape(tool, offset)
    return tool


def _translate_shape(shape, offset: Sequence[float]):
    if hasattr(shape, "translate"):
        try:
            if Vector is not None:
                shape.translate(Vector(*offset))
            else:
                shape.translate(tuple(offset))
            return
        except Exception:
            pass

    if hasattr(shape, "Placement") and Placement_supports():
        try:
            from FreeCAD import Placement

            shape.Placement = Placement(Vector(*offset), Rotation())
        except Exception:
            pass


def Placement_supports():
    return Rotation is not None and Vector is not None
