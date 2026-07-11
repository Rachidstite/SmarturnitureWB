from typing import List
from domain.back_panel_engine import BackPanelEngine, BackPanelRule
from domain.manufacturing_ops import Groove
from scene_graph.scene_graph import SceneGraph
from scene_graph.metadata import BackPanelMetadata
from manufacturing.edge_spec import EdgeBandRegistry
from manufacturing.panel_spec import PanelSpec
from manufacturing.panel_operation_engine import PanelOperationEngine
from shared.roles import NodeRole


from core.logging_config import logger
class ManufacturingExtractor:
    """تحويل SceneGraph الهندسي إلى PanelSpecs تصنيعية."""

    @staticmethod
    def _operation_key(operation):
        operation_type = getattr(
            operation,
            "op_type",
            getattr(operation, "operation_type", operation.__class__.__name__),
        )
        face = getattr(
            operation,
            "face",
            getattr(operation, "edge", ""),
        )
        x = getattr(
            operation,
            "local_x",
            getattr(operation, "x", getattr(operation, "start_x", None)),
        )
        y = getattr(
            operation,
            "local_y",
            getattr(operation, "y", getattr(operation, "z", None)),
        )
        return (
            operation_type,
            face,
            x,
            y,
            getattr(operation, "diameter", None),
            getattr(operation, "depth", None),
            getattr(operation, "axis", None),
            getattr(operation, "is_through", None),
        )

    @staticmethod
    def _merge_operations(*operation_groups):
        merged = []
        seen = set()
        for operations in operation_groups:
            for operation in operations or []:
                key = ManufacturingExtractor._operation_key(operation)
                if key in seen:
                    continue
                seen.add(key)
                merged.append(operation)
        return merged

    @staticmethod
    def _resolve_back_panel_groove_config(scene_graph):
        """Find the back panel node and extract groove configuration.

        Returns None if no grooved back panel exists.
        Returns a dict with groove depth, width, and back panel geometry.
        Supports both str-enum (domain.core_types) and int-enum (shared.roles) NodeRole.
        """
        for node in getattr(scene_graph, 'physical_nodes', scene_graph.all_nodes()):
            role_name = ManufacturingExtractor._role_name(node)
            if role_name != "BACK_PANEL":
                continue

            meta = getattr(node, "metadata", None)
            if not isinstance(meta, BackPanelMetadata):
                continue

            groove_depth = float(getattr(meta, "groove_depth", 0.0) or 0.0)
            if groove_depth <= 0.0:
                continue

            extends_into = bool(getattr(meta, "extends_into_groove", False))
            if not extends_into:
                continue

            back_thickness = float(getattr(node, "thickness", 0.0) or 0.0)
            groove_width = back_thickness + BackPanelRule.groove_clearance

            return {
                "active": True,
                "groove_depth": groove_depth,
                "groove_width": groove_width,
                "back_x": float(getattr(node, "x", 0.0) or 0.0),
                "back_y": float(getattr(node, "y", 0.0) or 0.0),
                "back_z": float(getattr(node, "z", 0.0) or 0.0),
                "back_width": float(getattr(node, "width", 0.0) or 0.0),
                "back_height": float(getattr(node, "height", 0.0) or 0.0),
                "back_panel_identity": str(
                    getattr(getattr(node, "identity", None), "key", "") or ""
                ),
            }

        return None

    @staticmethod
    def _role_name(node):
        """Get role name as uppercase string, supporting both str and int enums."""
        role = getattr(node, "role", None)
        if role is None:
            return ""
        if isinstance(role, str):
            return role.upper()
        name = getattr(role, "name", None)
        if isinstance(name, str):
            return name.upper()
        value = getattr(role, "value", None)
        if isinstance(value, str):
            return value.upper()
        return str(role).upper()

    @staticmethod
    def _build_receiving_panel_groove(node, back_panel_config, cut_width, cut_height):
        """Build a Groove operation for a receiving panel (SIDE_PANEL, BOTTOM_PANEL).

        Returns None when:
        - No grooved back panel exists
        - The node is not a receiving panel
        - The back panel position does not intersect this receiving panel

        Uses the engineering groove dimensions from the back panel metadata.
        Preserves panel_identity and source_operation_reference in metadata.
        """
        if back_panel_config is None:
            return None

        role_name = ManufacturingExtractor._role_name(node)
        if role_name not in ("SIDE_PANEL", "BOTTOM_PANEL"):
            return None

        gd = back_panel_config["groove_depth"]
        gw = back_panel_config["groove_width"]

        rn_x = float(getattr(node, "x", 0.0) or 0.0)
        rn_y = float(getattr(node, "y", 0.0) or 0.0)
        rn_z = float(getattr(node, "z", 0.0) or 0.0)
        rn_width = float(getattr(node, "width", 0.0) or 0.0)
        rn_depth = float(getattr(node, "depth", 0.0) or 0.0)
        rn_height = float(getattr(node, "height", 0.0) or 0.0)

        bp_x = back_panel_config["back_x"]
        bp_y = back_panel_config["back_y"]
        bp_z = back_panel_config["back_z"]
        bp_width = back_panel_config["back_width"]
        bp_height = back_panel_config["back_height"]

        panel_identity = str(
            getattr(getattr(node, "identity", None), "key", "") or ""
        )

        # For SIDE_PANEL: cut_width = depth, cut_height = height
        # The groove runs vertically at the back edge of the panel.
        # In the panel's local face coordinates (X = depth, Y = height):
        #   - The groove is near the back: start_x ≈ depth - gd
        #   - It starts at Y = bp_z - rn_z (back panel bottom relative to panel bottom)
        #   - It extends for bp_height
        if role_name == "SIDE_PANEL":
            panel_depth = rn_depth

            # Groove depth goes into the panel from the inside face,
            # positioned at the back edge of the panel.
            start_x = max(panel_depth - gd, 0.0)
            start_y = max(bp_z - rn_z, 0.0)
            length = bp_height
            face = "BACK"

            if length <= 0.0:
                return None

            return Groove(
                start_x=start_x,
                start_y=start_y,
                width=gw,
                depth=gd,
                length=length,
                face=face,
                metadata={
                    "panel_identity": panel_identity,
                    "source_operation_reference": "EngineeringGrooveProjection",
                    "groove_width": gw,
                    "groove_depth": gd,
                    "groove_length": length,
                    "groove_position_x": start_x,
                    "groove_position_y": start_y,
                    "target_panel_role": "SIDE_PANEL",
                    "target_panel": panel_identity,
                    "back_panel": back_panel_config["back_panel_identity"],
                    "groove_face": face,
                },
            )

        # For BOTTOM_PANEL: cut_width = width, cut_height = depth
        # The groove runs horizontally (along width = X) at the back of the panel.
        # This matches the Groove length semantics (length extends along X).
        if role_name == "BOTTOM_PANEL":
            start_x = 0.0
            start_y = max(rn_depth - gd, 0.0)
            length = bp_width
            face = "BACK"

            if length > cut_width:
                length = cut_width

            return Groove(
                start_x=start_x,
                start_y=start_y,
                width=gw,
                depth=gd,
                length=length,
                face=face,
                metadata={
                    "panel_identity": panel_identity,
                    "source_operation_reference": "EngineeringGrooveProjection",
                    "groove_width": gw,
                    "groove_depth": gd,
                    "groove_length": length,
                    "groove_position_x": start_x,
                    "groove_position_y": start_y,
                    "target_panel_role": "BOTTOM_PANEL",
                    "target_panel": panel_identity,
                    "back_panel": back_panel_config["back_panel_identity"],
                    "groove_face": face,
                },
            )

        return None

    @staticmethod
    def _resolve_cut_dimensions(node):
        """
        تحويل أبعاد XYZ إلى أبعاد تصنيع حقيقية
        حسب نوع القطعة.
        """

        role = node.role

        if role in (
            NodeRole.SIDE_PANEL,
            NodeRole.DIVIDER,
        ):
            return node.depth, node.height

        if role in (
            NodeRole.TOP_PANEL,
            NodeRole.BOTTOM_PANEL,
            NodeRole.SHELF,
        ):
            return node.width, node.depth

        if role in (
            NodeRole.BACK_PANEL,
            NodeRole.DOOR_PANEL,
            NodeRole.DRAWER_FACE,
            NodeRole.PLINTH,
        ):
            return node.width, node.height

        return node.width, node.height

    @staticmethod
    def extract(scene_graph: SceneGraph) -> List[PanelSpec]:

        specs = []

        panel_operations = PanelOperationEngine.generate(
            scene_graph
        )

        logger.debug(
            "[MANUFACTURING EXTRACTOR] %s",
            len(panel_operations)
        )

        # Detect grooved back panel from scene graph nodes
        back_panel_config = ManufacturingExtractor._resolve_back_panel_groove_config(
            scene_graph
        )

        for node in getattr(scene_graph, 'physical_nodes', scene_graph.all_nodes()):

            cut_width, cut_height = (
                ManufacturingExtractor._resolve_cut_dimensions(
                    node
                )
            )

            cnc_operations = ManufacturingExtractor._merge_operations(
                getattr(node, "machining_ops", []),
                panel_operations.get(node.identity.key, []),
            )

            role_value = getattr(node.role, "value", node.role)
            groove_rule = BackPanelRule(thickness=node.thickness)
            if role_value == "BACK_PANEL" and BackPanelEngine.requires_groove(groove_rule):
                cnc_operations.append(
                    Groove(
                        start_x=BackPanelEngine.offset(groove_rule),
                        start_y=0.0,
                        width=BackPanelEngine.groove_width(groove_rule),
                        depth=BackPanelEngine.insertion_depth(groove_rule),
                        length=cut_width,
                        face="BACK",
                    )
                )

            # Emit receiving-panel groove operations from engineering intent
            receiving_groove = ManufacturingExtractor._build_receiving_panel_groove(
                node, back_panel_config, cut_width, cut_height,
            )
            if receiving_groove is not None:
                cnc_operations.append(receiving_groove)

            edge_spec = getattr(node, "edge_spec", None)
            if edge_spec is None:
                edge_spec = EdgeBandRegistry.get_edges(node.role)

            spec = PanelSpec(
                identity=node.identity.key,
                role=node.role,
                width=cut_width,
                height=cut_height,
                thickness=node.thickness,
                material=node.material,
                group=node.group,
                edge_spec=edge_spec,
                cnc_operations=cnc_operations
            )

            specs.append(spec)

            if spec.cnc_operations:
                logger.debug(
                    "[CNC OPS] %s %s",
                    spec.identity,
                    len(spec.cnc_operations)
                )

        return specs
