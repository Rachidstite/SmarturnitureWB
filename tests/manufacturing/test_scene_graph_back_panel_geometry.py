import unittest
from types import SimpleNamespace
from unittest.mock import patch

from core.material_manager import MaterialManager
from engine.cabinet import Cabinet
from engine.geometry_engine import GeometryEngine
from scene_graph.builder import SceneGraphBuilder, resolve_back_panel_geometry
from shared.roles import NodeRole
from shared.contracts import CabinetParams
from shared.contracts import SectionConfig
from scene_graph.builder import resolve_back_panel_geometry


class SceneGraphBackPanelGeometryTest(unittest.TestCase):
    def setUp(self):
        self.mat = MaterialManager()
        self.mat.mdf_thickness = 18.0
        self.mat.back_thickness = 8.0
        self.cabinet = SimpleNamespace(
            params=CabinetParams(
                width=800.0,
                height=2000.0,
                depth=600.0,
                base_height=80.0,
                material_thickness=18.0,
                back_panel_type="REAR",
            )
        )
        self.section = SimpleNamespace(inner_x=18.0, inner_width=764.0)

    def test_rear_back_panel_sits_behind_cabinet_body(self):
        geometry = resolve_back_panel_geometry(self.cabinet, self.mat, 0, self.section)

        self.assertIsNotNone(geometry)
        self.assertEqual(geometry["width"], 764.0)
        self.assertEqual(geometry["depth"], 8.0)
        self.assertEqual(geometry["height"], 1884.0)
        self.assertEqual(geometry["x"], 18.0)
        self.assertEqual(geometry["y"], 592.0)
        self.assertEqual(geometry["z"], 98.0)
        self.assertEqual(geometry["metadata"].source_rule, "BackPanelRule:REAR")

    def test_groove_back_panel_is_recessed_and_distinct(self):
        self.cabinet.params.back_panel_type = "GROOVE"

        geometry = resolve_back_panel_geometry(self.cabinet, self.mat, 0, self.section)

        self.assertIsNotNone(geometry)
        self.assertEqual(geometry["x"], 10.0)
        self.assertEqual(geometry["y"], 582.0)
        self.assertEqual(geometry["z"], 90.0)
        self.assertEqual(geometry["height"], 1900.0)
        self.assertTrue(geometry["metadata"].extends_into_groove)

    def test_none_back_panel_type_disables_back_panel_geometry(self):
        self.cabinet.params.back_panel_type = "NONE"

        self.assertIsNone(resolve_back_panel_geometry(self.cabinet, self.mat, 0, self.section))

    def test_scene_graph_builder_consumes_helper_for_back_panel_geometry(self):
        cabinet = Cabinet(
            CabinetParams(
                width=1200.0,
                height=2000.0,
                depth=600.0,
                base_height=80.0,
                sec_count=1,
                sec_data={0: SectionConfig(shelves=1, drawers=0, doors="Inset", door_count=2)},
                back_panel_type="REAR",
            )
        )
        mat = MaterialManager()
        geo = GeometryEngine(cabinet, mat)
        geo.resolve_all()

        builder = SceneGraphBuilder(cabinet, mat)
        with patch(
            "scene_graph.builder.resolve_back_panel_geometry",
            wraps=resolve_back_panel_geometry,
        ) as helper_spy:
            graph = builder.build(geo)

        helper_spy.assert_called_once()
        back_nodes = [node for node in graph.all_nodes() if node.role == NodeRole.BACK_PANEL]
        shelf_nodes = [node for node in graph.all_nodes() if node.role == NodeRole.SHELF]
        door_nodes = [node for node in graph.all_nodes() if node.role == NodeRole.DOOR_PANEL]
        divider_nodes = [node for node in graph.all_nodes() if node.role == NodeRole.DIVIDER]
        drawer_nodes = [node for node in graph.all_nodes() if node.role == NodeRole.DRAWER_FACE]
        plinth_nodes = [node for node in graph.all_nodes() if node.role == NodeRole.PLINTH]

        self.assertEqual(len(back_nodes), 1)
        self.assertEqual(len(shelf_nodes), 1)
        self.assertEqual(len(door_nodes), 2)
        self.assertEqual(len(divider_nodes), 0)
        self.assertEqual(len(drawer_nodes), 0)
        self.assertEqual(len(plinth_nodes), 2)

        back_node = back_nodes[0]
        shelf_node = shelf_nodes[0]
        expected = resolve_back_panel_geometry(cabinet, mat, 0, geo.resolved_sections[0])

        self.assertEqual(back_node.width, expected["width"])
        self.assertEqual(back_node.depth, expected["depth"])
        self.assertEqual(back_node.height, expected["height"])
        self.assertEqual(back_node.x, expected["x"])
        self.assertEqual(back_node.y, expected["y"])
        self.assertEqual(back_node.z, expected["z"])
        self.assertEqual(back_node.metadata.source_rule, expected["metadata"].source_rule)
        self.assertLessEqual(shelf_node.y + shelf_node.depth, back_node.y)
        self.assertEqual(len(graph.all_nodes()), 10)

    def test_scene_graph_builder_uses_geometry_engine_dimensions_for_shelves_and_dividers(self):
        cabinet = Cabinet(
            CabinetParams(
                width=1200.0,
                height=2000.0,
                depth=600.0,
                base_height=80.0,
                sec_count=2,
                sec_data={
                    0: SectionConfig(shelves=1, drawers=0, doors="Inset", door_count=2),
                    1: SectionConfig(shelves=1, drawers=0, doors="Inset", door_count=2),
                },
                back_panel_type="REAR",
            )
        )
        mat = MaterialManager()
        geo = GeometryEngine(cabinet, mat)
        geo.resolve_all()

        builder = SceneGraphBuilder(cabinet, mat)
        graph = builder.build(geo)

        section_0 = geo.resolved_sections[0]
        shelf_0 = section_0.shelves[0]
        divider_0 = section_0.divider
        shelf_nodes = [node for node in graph.all_nodes() if node.role == NodeRole.SHELF]
        divider_nodes = [node for node in graph.all_nodes() if node.role == NodeRole.DIVIDER]
        back_nodes = [node for node in graph.all_nodes() if node.role == NodeRole.BACK_PANEL]

        self.assertEqual(len(shelf_nodes), 2)
        self.assertEqual(len(divider_nodes), 1)
        self.assertEqual(len(back_nodes), 2)
        self.assertEqual(len(graph.all_nodes()), 15)

        scene_shelf = shelf_nodes[0]
        scene_divider = divider_nodes[0]
        scene_back = back_nodes[0]
        expected_back = resolve_back_panel_geometry(cabinet, mat, 0, section_0)

        self.assertEqual(scene_shelf.depth, shelf_0.depth)
        self.assertEqual(scene_shelf.y, shelf_0.y)
        self.assertEqual(scene_divider.depth, divider_0.depth)
        self.assertEqual(scene_divider.y, divider_0.y)
        self.assertEqual(scene_back.width, expected_back["width"])
        self.assertEqual(scene_back.depth, expected_back["depth"])
        self.assertEqual(scene_back.height, expected_back["height"])
        self.assertEqual(scene_back.x, expected_back["x"])
        self.assertEqual(scene_back.y, expected_back["y"])
        self.assertEqual(scene_back.z, expected_back["z"])
        self.assertLessEqual(scene_shelf.y + scene_shelf.depth, scene_back.y)
        self.assertLessEqual(scene_divider.y + scene_divider.depth, scene_back.y)


if __name__ == "__main__":
    unittest.main()
