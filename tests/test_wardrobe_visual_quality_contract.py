import unittest
from types import SimpleNamespace

from domain.builders import WardrobeBuilder
from domain.core_types import NodeRole
from scene_graph.renderer import SceneRenderer


class TestWardrobeVisualQualityContract(unittest.TestCase):
    def test_renderer_palette_distinguishes_structure_roles(self):
        back = SimpleNamespace(role=NodeRole.BACK_PANEL, group="Carcass")
        door = SimpleNamespace(role=NodeRole.DOOR_PANEL, group="Doors")
        shelf = SimpleNamespace(role=NodeRole.SHELF, group="Shelves")
        divider = SimpleNamespace(role=NodeRole.DIVIDER, group="Dividers")
        side = SimpleNamespace(role=NodeRole.SIDE_PANEL, group="Carcass")

        back_color = SceneRenderer._visual_color_for(back)
        door_color = SceneRenderer._visual_color_for(door)
        shelf_color = SceneRenderer._visual_color_for(shelf)
        divider_color = SceneRenderer._visual_color_for(divider)
        side_color = SceneRenderer._visual_color_for(side)

        self.assertNotEqual(back_color, door_color)
        self.assertNotEqual(back_color, shelf_color)
        self.assertNotEqual(door_color, shelf_color)
        self.assertNotEqual(divider_color, side_color)
        self.assertNotEqual(side_color, back_color)

    def test_wardrobe_geometry_still_contains_expected_parts_and_spacing(self):
        cabinet = WardrobeBuilder(uid="VISUAL_QA", width=1200, height=2000, depth=600)
        left_id, _right_id = cabinet.add_divider(x_offset=600)
        cabinet.add_shelves(count=3, section_id=left_id)
        cabinet.add_doors(count=2)
        project = cabinet.build()

        by_role = project.graph._by_role

        self.assertEqual(len(project.graph.physical_nodes), 11)
        self.assertEqual(len(by_role[NodeRole.SIDE_PANEL]), 2)
        self.assertEqual(len(by_role[NodeRole.TOP_PANEL]), 1)
        self.assertEqual(len(by_role[NodeRole.BOTTOM_PANEL]), 1)
        self.assertEqual(len(by_role[NodeRole.BACK_PANEL]), 1)
        self.assertEqual(len(by_role[NodeRole.DIVIDER]), 1)
        self.assertEqual(len(by_role[NodeRole.SHELF]), 3)
        self.assertEqual(len(by_role[NodeRole.DOOR_PANEL]), 2)

        left_side, right_side = sorted(
            by_role[NodeRole.SIDE_PANEL],
            key=lambda node: node.transform.x,
        )
        divider = by_role[NodeRole.DIVIDER][0]
        bottom = by_role[NodeRole.BOTTOM_PANEL][0]
        top = by_role[NodeRole.TOP_PANEL][0]
        back = by_role[NodeRole.BACK_PANEL][0]

        self.assertEqual(left_side.transform.x, 0)
        self.assertEqual(right_side.transform.x, cabinet.w - cabinet.t)
        self.assertLess(left_side.transform.x + left_side.thickness, divider.transform.x)
        self.assertLess(divider.transform.x, right_side.transform.x)
        self.assertEqual(bottom.transform.z, 0)
        self.assertEqual(top.transform.z, cabinet.h - cabinet.t)
        self.assertGreater(back.transform.y, 0)
        for shelf in by_role[NodeRole.SHELF]:
            self.assertGreaterEqual(shelf.transform.z, cabinet.t)
            self.assertLess(shelf.transform.z, cabinet.h - cabinet.t)


if __name__ == "__main__":
    unittest.main()
