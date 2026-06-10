from scene_graph.scene_graph import SceneGraph
from scene_graph.node import SceneNode
from shared.identity import PanelIdentity, SemanticRole
from shared.roles import NodeRole
from runtime.runtime_project_adapter import RuntimeProjectAdapter


class TableBuilder:
    """
    Proof-of-concept furniture builder.

    Builds a simple table using the existing SceneGraph and adapts it into
    the current aggregate root through RuntimeProjectAdapter.

    This intentionally does not introduce new NodeRole values yet.
    """

    def __init__(
        self,
        uid="TABLE",
        width=1200,
        depth=700,
        height=750,
        top_thickness=18,
        leg_size=70,
        material="MDF_18MM",
    ):
        self.uid = uid
        self.width = width
        self.depth = depth
        self.height = height
        self.top_thickness = top_thickness
        self.leg_size = leg_size
        self.material = material

    def build_scene_graph(self):
        graph = SceneGraph()

        top = SceneNode(
            identity=PanelIdentity(
                self.uid,
                "STRUCTURE",
                SemanticRole.TOP,
                0,
            ),
            role=NodeRole.TOP_PANEL,
            width=self.width,
            depth=self.depth,
            height=self.top_thickness,
            thickness=self.top_thickness,
            material=self.material,
            x=0,
            y=0,
            z=self.height - self.top_thickness,
            group="Table",
            metadata={
                "furniture_type": "TABLE",
                "semantic_role": "TABLE_TOP",
            },
        )

        graph.add_node(top)

        leg_positions = [
            ("LEFT_FRONT", 0, 0),
            ("RIGHT_FRONT", self.width - self.leg_size, 0),
            ("LEFT_BACK", 0, self.depth - self.leg_size),
            ("RIGHT_BACK", self.width - self.leg_size, self.depth - self.leg_size),
        ]

        for index, (_, x, y) in enumerate(leg_positions):
            leg = SceneNode(
                identity=PanelIdentity(
                    self.uid,
                    "STRUCTURE",
                    SemanticRole.LEFT_SIDE,
                    index,
                ),
                role=NodeRole.SIDE_PANEL,
                width=self.leg_size,
                depth=self.leg_size,
                height=self.height - self.top_thickness,
                thickness=self.leg_size,
                material=self.material,
                x=x,
                y=y,
                z=0,
                group="Table",
                metadata={
                    "furniture_type": "TABLE",
                    "semantic_role": "TABLE_LEG",
                },
            )

            graph.add_node(leg)

        return graph

    def build(self):
        return RuntimeProjectAdapter.from_scene_graph(
            self.build_scene_graph()
        )
