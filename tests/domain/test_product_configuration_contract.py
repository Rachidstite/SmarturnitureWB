import unittest
from dataclasses import fields, is_dataclass

from domain.product_configuration import ProductConfiguration


class TestProductConfigurationContract(unittest.TestCase):
    def test_preserves_selected_family_dimensions_material_options_and_metadata(self):
        configuration = ProductConfiguration(
            family_id="BASE_CABINET",
            width=600.0,
            height=720.0,
            depth=580.0,
            material="PLYWOOD",
            options={"door_count": 2, "shelf_count": 1},
            metadata={"source": "user-selection"},
        )

        self.assertTrue(is_dataclass(configuration))
        self.assertEqual(
            [field.name for field in fields(ProductConfiguration)],
            [
                "family_id",
                "width",
                "height",
                "depth",
                "material",
                "options",
                "metadata",
            ],
        )
        self.assertEqual(configuration.family_id, "BASE_CABINET")
        self.assertEqual(configuration.width, 600.0)
        self.assertEqual(configuration.height, 720.0)
        self.assertEqual(configuration.depth, 580.0)
        self.assertEqual(configuration.material, "PLYWOOD")
        self.assertEqual(configuration.options, {"door_count": 2, "shelf_count": 1})
        self.assertEqual(configuration.metadata, {"source": "user-selection"})

    def test_defaults_are_safe_and_empty(self):
        configuration = ProductConfiguration(
            family_id="WALL_CABINET",
            width=600.0,
            height=720.0,
            depth=350.0,
        )

        self.assertEqual(configuration.material, "MDF")
        self.assertEqual(configuration.options, {})
        self.assertEqual(configuration.metadata, {})

    def test_invalid_required_values_raise_value_error(self):
        with self.assertRaises(ValueError):
            ProductConfiguration(
                family_id="",
                width=600.0,
                height=720.0,
                depth=580.0,
            )

        with self.assertRaises(ValueError):
            ProductConfiguration(
                family_id="BASE_CABINET",
                width=0.0,
                height=720.0,
                depth=580.0,
            )

        with self.assertRaises(ValueError):
            ProductConfiguration(
                family_id="BASE_CABINET",
                width=600.0,
                height=-1.0,
                depth=580.0,
            )

        with self.assertRaises(ValueError):
            ProductConfiguration(
                family_id="BASE_CABINET",
                width=600.0,
                height=720.0,
                depth=0.0,
            )

        with self.assertRaises(ValueError):
            ProductConfiguration(
                family_id="BASE_CABINET",
                width=600.0,
                height=720.0,
                depth=580.0,
                material="",
            )


if __name__ == "__main__":
    unittest.main()
