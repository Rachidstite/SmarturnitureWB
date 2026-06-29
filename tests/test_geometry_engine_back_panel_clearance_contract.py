import unittest
from types import SimpleNamespace

from core.material_manager import MaterialManager
from engine.cabinet import Cabinet
from engine.geometry_engine import GeometryEngine
from scene_graph.builder import resolve_back_panel_geometry
from shared.contracts import CabinetParams, SectionConfig


class TestGeometryEngineBackPanelClearanceContract(unittest.TestCase):
    def test_resolved_shelf_leaves_rear_clearance_for_back_panel_zone(self):
        cabinet = Cabinet(
            CabinetParams(
                width=1200.0,
                height=2000.0,
                depth=600.0,
                base_height=80.0,
                sec_count=1,
                sec_data={0: SectionConfig(shelves=1, drawers=0, doors="Inset", door_count=2)},
            )
        )
        mat = MaterialManager()
        geo = GeometryEngine(cabinet, mat)
        geo.resolve_all()

        section = geo.resolved_sections[0]
        shelf = section.shelves[0]

        self.assertEqual(shelf.y, mat.mdf_thickness)
        self.assertEqual(shelf.depth, 567.0)

    def test_back_panel_geometry_helper_exposes_expected_groove_zone(self):
        cabinet = SimpleNamespace(
            params=CabinetParams(
                width=800.0,
                height=2000.0,
                depth=600.0,
                base_height=80.0,
                material_thickness=18.0,
                back_panel_type="GROOVE",
            )
        )
        mat = MaterialManager()
        mat.mdf_thickness = 18.0
        mat.back_thickness = 8.0
        section = SimpleNamespace(inner_x=18.0, inner_width=764.0)

        geometry = resolve_back_panel_geometry(cabinet, mat, 0, section)

        self.assertIsNotNone(geometry)
        self.assertEqual(geometry["x"], 10.0)
        self.assertEqual(geometry["y"], 582.0)
        self.assertEqual(geometry["z"], 90.0)
        self.assertEqual(geometry["height"], 1900.0)
        self.assertTrue(geometry["metadata"].extends_into_groove)


if __name__ == "__main__":
    unittest.main()
