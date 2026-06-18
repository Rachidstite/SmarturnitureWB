import unittest

from domain.builders import Identity, SceneNode, WardrobeBuilder
from domain.core_types import NodeRole
from domain.rules_engine import HardwarePlacementEngine, RuleContext


class TestDrawerSlideSidePanelPlacementContract(unittest.TestCase):

    def test_drawer_slide_placements_include_side_panel_hosts(self):
        project = self._project_with_drawer_fronts_matching_universal_marking_test()
        context = RuleContext()

        HardwarePlacementEngine(context).process(project)

        slide_placements = [
            placement
            for placement in project.placements
            if placement.hardware_intent == "INTENT_DRAWER_SLIDE"
        ]

        self.assertTrue(
            slide_placements,
            "Expected drawer slide placements to be emitted",
        )

        for placement in slide_placements:
            self.assertTrue(
                getattr(placement, "host_node_id", None),
                f"Drawer slide placement missing host_node_id: {placement}",
            )

        side_panel_ids = {
            node.identity.key
            for node in project.graph._by_role[NodeRole.SIDE_PANEL]
        }
        drawer_front_ids = {
            node.identity.key
            for node in project.graph._by_role[NodeRole.DRAWER_FRONT]
        }
        slide_host_ids = {placement.host_node_id for placement in slide_placements}

        self.assertTrue(
            slide_host_ids & side_panel_ids,
            "At least one drawer slide placement must be hosted on a side panel",
        )
        self.assertTrue(
            slide_host_ids - drawer_front_ids,
            "Drawer fronts must not be the only hosts for drawer slide placements",
        )

    @staticmethod
    def _project_with_drawer_fronts_matching_universal_marking_test():
        cabinet = WardrobeBuilder(
            uid="DRAWER_SLIDE_SIDE_PANEL_CONTRACT",
            width=1000,
            height=2000,
            depth=600,
        )
        cabinet.add_doors(2)
        project = cabinet.build()

        drawer_fronts = []
        for index in range(2):
            drawer_front = SceneNode(
                Identity(f"DRAWER_SLIDE_SIDE_PANEL_CONTRACT_DRAWER_FRONT_{index + 1}"),
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
