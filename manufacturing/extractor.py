from typing import List
from domain.back_panel_engine import BackPanelEngine, BackPanelRule
from domain.manufacturing_ops import Groove
from scene_graph.scene_graph import SceneGraph
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
