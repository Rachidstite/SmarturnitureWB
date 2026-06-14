import unittest

from manufacturing.material_spec import MaterialSpec


class TestMaterialCatalog(unittest.TestCase):

    def test_material_catalog_exists(self):
        from manufacturing.material_catalog import MaterialCatalog

        self.assertIsNotNone(MaterialCatalog)

    def test_can_add_and_retrieve_exact_material_spec(self):
        from manufacturing.material_catalog import MaterialCatalog

        catalog = MaterialCatalog()
        material = MaterialSpec(name="MDF_18MM", thickness=18.0)

        catalog.add_material("MDF_18MM", material)

        self.assertIs(catalog.get_material("MDF_18MM"), material)

    def test_has_material_returns_true_and_false(self):
        from manufacturing.material_catalog import MaterialCatalog

        catalog = MaterialCatalog()
        catalog.add_material(
            "MDF_18MM",
            MaterialSpec(name="MDF_18MM", thickness=18.0),
        )

        self.assertTrue(catalog.has_material("MDF_18MM"))
        self.assertFalse(catalog.has_material("HDF_3MM"))

    def test_list_material_keys_preserves_insertion_order(self):
        from manufacturing.material_catalog import MaterialCatalog

        catalog = MaterialCatalog()
        catalog.add_material(
            "MDF_18MM",
            MaterialSpec(name="MDF_18MM", thickness=18.0),
        )
        catalog.add_material(
            "HDF_3MM",
            MaterialSpec(name="HDF_3MM", thickness=3.0),
        )

        self.assertEqual(
            catalog.list_material_keys(),
            ["MDF_18MM", "HDF_3MM"],
        )

    def test_from_library_copies_keys_without_mutating_input(self):
        from manufacturing.material_catalog import MaterialCatalog

        first_material = MaterialSpec(name="MDF_18MM", thickness=18.0)
        second_material = MaterialSpec(name="HDF_3MM", thickness=3.0)
        material_library = {
            "MDF_18MM": first_material,
            "HDF_3MM": second_material,
        }
        original_keys = list(material_library)

        catalog = MaterialCatalog.from_library(material_library)
        catalog.add_material(
            "MDF_8MM",
            MaterialSpec(name="MDF_8MM", thickness=8.0),
        )

        self.assertEqual(list(material_library), original_keys)
        self.assertNotIn("MDF_8MM", material_library)
        self.assertEqual(catalog.list_material_keys()[:2], original_keys)
        self.assertIs(catalog.get_material("MDF_18MM"), first_material)
        self.assertIs(catalog.get_material("HDF_3MM"), second_material)

    def test_missing_material_raises_key_error(self):
        from manufacturing.material_catalog import MaterialCatalog

        catalog = MaterialCatalog()

        with self.assertRaises(KeyError):
            catalog.get_material("MISSING")

    def test_empty_catalog_has_empty_key_list(self):
        from manufacturing.material_catalog import MaterialCatalog

        self.assertEqual(MaterialCatalog().list_material_keys(), [])


if __name__ == "__main__":
    unittest.main()
