import unittest
from dataclasses import fields

from manufacturing.material_spec import MATERIAL_LIBRARY, MaterialSpec


class TestMaterialCostCharacterization(unittest.TestCase):

    def test_material_specs_expose_area_price_only(self):
        field_names = {field.name for field in fields(MaterialSpec)}

        self.assertIn("price_per_m2", field_names)
        self.assertNotIn("price_per_sheet", field_names)
        self.assertNotIn("currency", field_names)

    def test_all_registered_material_prices_currently_default_to_zero(self):
        self.assertTrue(MATERIAL_LIBRARY)

        self.assertEqual(
            {key: spec.price_per_m2 for key, spec in MATERIAL_LIBRARY.items()},
            {
                "MDF_18MM": 0.0,
                "MDF_8MM": 0.0,
                "HDF_3MM": 0.0,
                "MELAMINE_WHITE_18MM": 0.0,
            },
        )


if __name__ == "__main__":
    unittest.main()
