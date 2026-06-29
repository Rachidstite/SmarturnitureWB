import unittest

from core.material_manager import MaterialManager
from engine.cabinet import Cabinet
from engine.geometry_engine import GeometryEngine
from shared.contracts import CabinetParams, SectionConfig


class TestGeometryEngineDividerSpacingContract(unittest.TestCase):
    def test_resolved_sections_account_for_divider_thickness(self):
        cabinet = Cabinet(
            CabinetParams(
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
        self.assertEqual(len(geo.resolved_sections[0].shelves), 1)
        self.assertEqual(len(geo.resolved_sections[1].shelves), 1)

    def test_manual_section_widths_scale_to_available_openings(self):
        cabinet = Cabinet(
            CabinetParams(
                width=1800.0,
                height=2000.0,
                depth=600.0,
                base_height=80.0,
                sec_count=3,
                sec_data={
                    0: SectionConfig(shelves=1, drawers=1, doors="Inset", door_count=1, drawer_type="Inset"),
                    1: SectionConfig(shelves=1, drawers=0, doors="None", door_count=1),
                    2: SectionConfig(shelves=1, drawers=0, doors="None", door_count=1),
                },
                section_widths=[450.0, 900.0, 450.0],
                back_thickness=8.0,
                cnc_mode=False,
            )
        )
        mat = MaterialManager()

        geo = GeometryEngine(cabinet, mat)
        geo.resolve_all()

        self.assertEqual(len(geo.resolved_sections), 3)
        self.assertAlmostEqual(geo.resolved_sections[0].inner_width, 432.0)
        self.assertAlmostEqual(geo.resolved_sections[1].inner_x, 468.0)
        self.assertAlmostEqual(geo.resolved_sections[1].inner_width, 864.0)
        self.assertAlmostEqual(geo.resolved_sections[2].inner_x, 1350.0)
        self.assertAlmostEqual(geo.resolved_sections[2].inner_width, 432.0)
        self.assertAlmostEqual(geo.resolved_sections[0].shelves[0].width, 432.0)
        self.assertAlmostEqual(geo.resolved_sections[0].doors[0].width, 428.0)
        self.assertAlmostEqual(geo.resolved_sections[0].drawers[0].face_w, 428.0)

    def test_invalid_manual_section_widths_fall_back_to_equal_resolution(self):
        cabinet = Cabinet(
            CabinetParams(
                width=1200.0,
                height=2000.0,
                depth=600.0,
                base_height=80.0,
                sec_count=2,
                sec_data={
                    0: SectionConfig(shelves=1, doors="None", door_count=1),
                    1: SectionConfig(shelves=1, doors="None", door_count=1),
                },
                section_widths=[500.0, 400.0],
                back_thickness=8.0,
                cnc_mode=False,
            )
        )
        mat = MaterialManager()

        geo = GeometryEngine(cabinet, mat)
        geo.resolve_all()

        self.assertAlmostEqual(geo.resolved_sections[0].inner_width, 573.0)
        self.assertAlmostEqual(geo.resolved_sections[1].inner_x, 609.0)


if __name__ == "__main__":
    unittest.main()
