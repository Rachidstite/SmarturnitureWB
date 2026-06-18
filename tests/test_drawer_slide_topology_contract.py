import unittest

from domain.builders import Identity, SceneNode, WardrobeBuilder
from domain.core_types import NodeRole
from domain.rules_engine import HardwarePlacementEngine, RuleContext


class TestDrawerSlideTopologyContract(unittest.TestCase):

    def test_drawer_slide_placement_represents_cabinet_side_panel_and_drawer_side(self):
        project = self._project_with_drawer_fronts()
        context = RuleContext()

        HardwarePlacementEngine(context).process(project)

        slide_placements = [
            placement
            for placement in project.placements
            if placement.hardware_intent == "INTENT_DRAWER_SLIDE"
        ]
        side_panel_nodes = project.graph._by_role[NodeRole.SIDE_PANEL]
        side_panel_ids = {node.identity.key for node in side_panel_nodes}
        drawer_front_nodes = project.graph._by_role[NodeRole.DRAWER_FRONT]
        drawer_front_ids = {node.identity.key for node in drawer_front_nodes}
        actual_host_node_ids = [placement.host_node_id for placement in slide_placements]

        self.assertTrue(
            slide_placements,
            "Expected drawer slide placements to exist",
        )
        self.assertTrue(
            side_panel_nodes,
            "Expected SIDE_PANEL nodes to exist",
        )
        self.assertIn(
            "DRAWER_SLIDE_TOPOLOGY_CONTRACT_SIDE_L",
            side_panel_ids,
        )
        self.assertIn(
            "DRAWER_SLIDE_TOPOLOGY_CONTRACT_SIDE_R",
            side_panel_ids,
        )
        self.assertTrue(
            drawer_front_nodes,
            "Expected drawer front nodes to exist",
        )

        self.assertTrue(
            set(actual_host_node_ids) & side_panel_ids,
            "Drawer slide placements must include cabinet side panel hosts; "
            f"actual host_node_ids={actual_host_node_ids}",
        )
        self.assertNotEqual(
            set(actual_host_node_ids),
            drawer_front_ids,
            "Drawer slide placements must not represent drawer fronts only; "
            f"actual host_node_ids={actual_host_node_ids}",
        )

    @staticmethod
    def _project_with_drawer_fronts():
        cabinet = WardrobeBuilder(
            uid="DRAWER_SLIDE_TOPOLOGY_CONTRACT",
            width=1000,
            height=2000,
            depth=600,
        )
        project = cabinet.build()

        drawer_fronts = []
        for index in range(2):
            drawer_front = SceneNode(
                Identity(f"DRAWER_SLIDE_TOPOLOGY_CONTRACT_DRAWER_FRONT_{index + 1}"),
                NodeRole.DRAWER_FRONT,
                450.0,
                180.0,
                18.0,
                "MDF_18_WHITE",
            )
            project.graph.add_node(drawer_front)
            drawer_fronts.append(drawer_front)

        drawer_face_role = type(
            "DrawerFaceRole",
            (),
            {
                "name": "DRAWER_FACE",
                "value": "DRAWER_FACE",
                "__hash__": object.__hash__,
            },
        )()
        project.graph._by_role[drawer_face_role] = drawer_fronts
        return project


if __name__ == "__main__":
    unittest.main()
