from typing import List
from manufacturing.panel_spec import PanelSpec


class ManufacturingExtractor:

    @staticmethod
    def extract(scene_graph):

        specs = []

        for node in scene_graph.physical_nodes:

            spec = PanelSpec(
                identity=node.identity.key,
                role=node.role,
                width=node.width,
                height=node.height,
                thickness=node.thickness,
                material=node.material,
                edge_spec=getattr(
                    node,
                    "edge_spec",
                    None
                )
            )

            specs.append(spec)

        return specs
