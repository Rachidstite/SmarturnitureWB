import unittest
from dataclasses import fields, is_dataclass


class TestOffcutContract(unittest.TestCase):

    def test_offcut_exists_and_is_dataclass(self):

        try:
            from cost_intelligence.offcut import Offcut
        except ImportError:
            self.fail(
                "Offcut does not exist"
            )

        self.assertTrue(
            is_dataclass(Offcut),
        )

    def test_offcut_contains_required_fields(self):

        from cost_intelligence.offcut import Offcut

        field_names = {
            field.name
            for field in fields(Offcut)
        }

        self.assertEqual(
            field_names,
            {
                "id",
                "material",
                "thickness",
                "width",
                "height",
                "area",
                "source_sheet",
                "reusable",
            },
        )

    def test_offcut_calculates_area_and_defaults_to_reusable(self):

        from cost_intelligence.offcut import Offcut

        offcut = Offcut(
            id="OFFCUT-001",
            material="MDF",
            thickness=18,
            width=600,
            height=400,
            source_sheet="SHEET-001",
        )

        self.assertEqual(
            offcut.width,
            600,
        )
        self.assertEqual(
            offcut.height,
            400,
        )
        self.assertEqual(
            offcut.area,
            240000,
        )
        self.assertTrue(
            offcut.reusable,
        )


if __name__ == "__main__":
    unittest.main()
