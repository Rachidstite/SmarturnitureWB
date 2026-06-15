import unittest
from dataclasses import fields, is_dataclass


class TestFurnitureProjectContract(unittest.TestCase):

    def test_furniture_project_exists_and_is_dataclass(self):
        from domain.furniture_project import FurnitureProject

        self.assertTrue(is_dataclass(FurnitureProject))

    def test_furniture_project_has_exact_field_order(self):
        from domain.furniture_project import FurnitureProject

        self.assertEqual(
            [field.name for field in fields(FurnitureProject)],
            [
                "project_id",
                "name",
                "cabinets",
                "metadata",
            ],
        )

    def test_furniture_project_has_safe_defaults(self):
        from domain.furniture_project import FurnitureProject

        project = FurnitureProject()

        self.assertEqual(project.project_id, "")
        self.assertEqual(project.name, "")
        self.assertEqual(project.cabinets, [])
        self.assertEqual(project.metadata, {})

    def test_cabinet_list_defaults_are_independent(self):
        from domain.furniture_project import FurnitureProject

        first = FurnitureProject()
        second = FurnitureProject()

        self.assertIsNot(first.cabinets, second.cabinets)

    def test_metadata_dict_defaults_are_independent(self):
        from domain.furniture_project import FurnitureProject

        first = FurnitureProject()
        second = FurnitureProject()

        self.assertIsNot(first.metadata, second.metadata)


if __name__ == "__main__":
    unittest.main()
