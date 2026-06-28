import unittest
from types import SimpleNamespace

from core.material_manager import MaterialManager
from engine.cabinet import Cabinet
from engine.geometry_engine import GeometryEngine
from shared.contracts import SectionConfig


class TestGeometryEngineDividerSpacingContract(unittest.TestCase):
    def test_resolved_sections_account_for_divider_thickness(self):
        cabinet = Cabinet(
            SimpleNamespace(
                width=1200.0,
                height=2000.0,
                depth=600.0,
                base_height=80.0,
                sec_count=2,
                sec_data={
                    0: SectionConfig(shelves=1, doors="None", door_count=1),
                    1: SectionConfig(shelves=1, doors="None", door_count=1),
                },
                back_thickness=8.0,
                cnc_mode=False,
            )
        )
        mat = MaterialManager()

        geo = GeometryEngine(cabinet, mat)
        geo.resolve_all()

        self.assertEqual(len(geo.resolved_sections), 2)
        self.assertAlmostEqual(geo.resolved_sections[0].inner_width, 573.0)
        self.assertAlmostEqual(geo.resolved_sections[1].inner_x, 609.0)
        self.assertAlmostEqual(
            geo.resolved_sections[0].divider.x,
            geo.resolved_sections[0].inner_x + geo.resolved_sections[0].inner_width,
        )
        self.assertAlmostEqual(
            geo.resolved_sections[0].divider.x + mat.mdf_thickness,
            geo.resolved_sections[1].inner_x,
        )


if __name__ == "__main__":
    unittest.main()
