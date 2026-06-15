import unittest


class TestFurnitureProjectBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from domain.furniture_project_builder import FurnitureProjectBuilder

        self.assertTrue(callable(FurnitureProjectBuilder().build))

    def test_empty_project_builds(self):
        from domain.furniture_project_builder import FurnitureProjectBuilder

        project = FurnitureProjectBuilder().build()

        self.assertEqual(project.cabinets, [])

    def test_single_cabinet_is_accepted(self):
        from domain.furniture_project_builder import FurnitureProjectBuilder

        cabinet = self._cabinet("CABINET-1")

        project = FurnitureProjectBuilder().add_cabinet(cabinet).build()

        self.assertEqual(project.cabinets, [cabinet])
        self.assertIs(project.cabinets[0], cabinet)

    def test_multiple_cabinets_are_accepted(self):
        from domain.furniture_project_builder import FurnitureProjectBuilder

        cabinets = [
            self._cabinet("CABINET-1"),
            self._cabinet("CABINET-2"),
        ]

        project = FurnitureProjectBuilder().add_cabinets(cabinets).build()

        self.assertEqual(project.cabinets, cabinets)
        self.assertIsNot(project.cabinets, cabinets)

    def test_build_returns_furniture_project(self):
        from domain.furniture_project import FurnitureProject
        from domain.furniture_project_builder import FurnitureProjectBuilder

        project = FurnitureProjectBuilder(
            project_id="PROJECT-1",
            name="Kitchen",
            metadata={"customer": "Example"},
        ).build()

        self.assertIsInstance(project, FurnitureProject)
        self.assertEqual(project.project_id, "PROJECT-1")
        self.assertEqual(project.name, "Kitchen")
        self.assertEqual(project.metadata, {"customer": "Example"})

    def test_builder_does_not_mutate_cabinet_objects(self):
        from domain.furniture_project_builder import FurnitureProjectBuilder

        cabinet = self._cabinet("CABINET-1")
        original_values = cabinet.__dict__.copy()

        FurnitureProjectBuilder().add_cabinet(cabinet).build()

        self.assertEqual(cabinet.__dict__, original_values)

    def test_project_cabinets_list_is_not_builder_internal_list(self):
        from domain.furniture_project_builder import FurnitureProjectBuilder

        builder = FurnitureProjectBuilder()
        builder.add_cabinet(self._cabinet("CABINET-1"))

        project = builder.build()

        self.assertIsNot(project.cabinets, builder._cabinets)

    def test_builder_does_not_reuse_external_cabinet_list(self):
        from domain.furniture_project_builder import FurnitureProjectBuilder

        cabinets = [self._cabinet("CABINET-1")]
        builder = FurnitureProjectBuilder(cabinets=cabinets)

        self.assertIsNot(builder._cabinets, cabinets)

    @staticmethod
    def _cabinet(uid):
        from domain.builders import WardrobeBuilder

        return WardrobeBuilder(
            uid=uid,
            width=1000,
            height=2000,
            depth=600,
        ).build()


if __name__ == "__main__":
    unittest.main()
