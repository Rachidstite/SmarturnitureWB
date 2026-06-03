from typing import List
from scene_graph.scene_graph import SceneGraph
from manufacturing.panel_spec import PanelSpec
from manufacturing.panel_operation_engine import PanelOperationEngine

class ManufacturingExtractor:
    """يحول SceneGraph إلى قائمة PanelSpec جاهزة للتصنيع."""

    @staticmethod
    def extract(scene_graph: SceneGraph) -> List[PanelSpec]:
        specs = []

        panel_operations = PanelOperationEngine.generate(
            scene_graph
        )

        print(
            "[MANUFACTURING EXTRACTOR]",
            len(panel_operations)
        )
        for node in scene_graph.all_nodes():
            spec = PanelSpec(
                identity=node.identity.key,
                role=node.role,
                width=node.width,
                height=node.height,
                thickness=node.thickness,
                material=node.material,
                group=node.group,
                edge_spec=node.edge_spec if hasattr(node, 'edge_spec') else None,  # ✅ الحواف
                cnc_operations=panel_operations.get(
                    node.identity.key,
                    []
                )
            )
            specs.append(spec)

            if spec.cnc_operations:
                print(
                    "[CNC OPS]",
                    spec.identity,
                    len(spec.cnc_operations)
                )
        return specs
