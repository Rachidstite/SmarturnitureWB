from __future__ import annotations

from manufacturing.visible_geometry_plan import VisibleGeometryFeatureSpec
from shared.roles import NodeRole


def project_visible_features(cabinet, scene_graph) -> tuple[VisibleGeometryFeatureSpec, ...]:
    engineering_model = getattr(cabinet, "engineering_model", None)
    if engineering_model is None:
        return ()

    back_panel = getattr(engineering_model, "back_panel", None)
    if back_panel is None:
        return ()

    installation_mode = str(
        getattr(getattr(back_panel, "installation_mode", None), "value", back_panel.installation_mode)
        or ""
    ).upper()
    if installation_mode != "GROOVED":
        return ()

    groove_depth = float(getattr(back_panel, "groove_depth_mm", 0.0) or 0.0)
    groove_width = float(getattr(back_panel, "groove_width_mm", 0.0) or 0.0)
    if groove_depth <= 0.0 or groove_width <= 0.0:
        return ()

    side_panels = sorted(
        [
            node
            for node in scene_graph.all_nodes()
            if getattr(node, "role", None) == NodeRole.SIDE_PANEL
        ],
        key=lambda node: float(getattr(node, "x", 0.0) or 0.0),
    )
    bottom_panel = next(
        (
            node
            for node in scene_graph.all_nodes()
            if getattr(node, "role", None) == NodeRole.BOTTOM_PANEL
        ),
        None,
    )
    if len(side_panels) < 2 or bottom_panel is None:
        return ()

    left_panel, right_panel = side_panels[0], side_panels[-1]
    groove_y = float(getattr(back_panel, "position_mm", (0.0, 0.0, 0.0))[1] or 0.0)
    groove_z = float(getattr(back_panel, "position_mm", (0.0, 0.0, 0.0))[2] or 0.0)
    groove_height = float(getattr(back_panel, "height_mm", 0.0) or 0.0)
    groove_x = float(getattr(back_panel, "position_mm", (0.0, 0.0, 0.0))[0] or 0.0)
    back_panel_width = float(getattr(back_panel, "width_mm", 0.0) or 0.0)
    source_rule = str(getattr(back_panel, "source_rule", "") or "")

    return (
        VisibleGeometryFeatureSpec(
            name=f"{left_panel.identity.key}_Back_Groove",
            kind="back_panel_groove",
            node_id=left_panel.identity.key,
            placement=(
                float(getattr(left_panel, "x", 0.0) or 0.0)
                + max(float(getattr(left_panel, "width", 0.0) or 0.0) - groove_depth, 0.0),
                groove_y,
                groove_z,
            ),
            size=(groove_depth, groove_width, groove_height),
            color=(0.35, 0.22, 0.12),
            label="Back panel groove",
            prototype=False,
            notes=("SIDE_PANEL", "LEFT", source_rule),
        ),
        VisibleGeometryFeatureSpec(
            name=f"{right_panel.identity.key}_Back_Groove",
            kind="back_panel_groove",
            node_id=right_panel.identity.key,
            placement=(
                float(getattr(right_panel, "x", 0.0) or 0.0),
                groove_y,
                groove_z,
            ),
            size=(groove_depth, groove_width, groove_height),
            color=(0.35, 0.22, 0.12),
            label="Back panel groove",
            prototype=False,
            notes=("SIDE_PANEL", "RIGHT", source_rule),
        ),
        VisibleGeometryFeatureSpec(
            name=f"{bottom_panel.identity.key}_Back_Groove",
            kind="back_panel_groove",
            node_id=bottom_panel.identity.key,
            placement=(
                groove_x,
                groove_y,
                float(getattr(bottom_panel, "z", 0.0) or 0.0)
                + max(float(getattr(bottom_panel, "height", 0.0) or 0.0) - groove_depth, 0.0),
            ),
            size=(back_panel_width, groove_width, groove_depth),
            color=(0.35, 0.22, 0.12),
            label="Back panel groove",
            prototype=False,
            notes=("BOTTOM_PANEL", source_rule),
        ),
    )
