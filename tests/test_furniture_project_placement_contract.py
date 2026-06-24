import unittest
from dataclasses import fields, is_dataclass


class TestCabinetPlacementContract(unittest.TestCase):

    def test_cabinet_placement_is_dataclass(self):
        from domain.furniture_project import CabinetPlacement

        self.assertTrue(is_dataclass(CabinetPlacement))

    def test_cabinet_placement_has_exact_fields(self):
        from domain.furniture_project import CabinetPlacement

        self.assertEqual(
            [field.name for field in fields(CabinetPlacement)],
            [
                "cabinet_id",
                "x",
                "y",
                "z",
                "rotation_z",
            ],
        )

    def test_cabinet_placement_has_safe_defaults(self):
        from domain.furniture_project import CabinetPlacement

        placement = CabinetPlacement(cabinet_id="C-1")

        self.assertEqual(placement.cabinet_id, "C-1")
        self.assertEqual(placement.x, 0.0)
        self.assertEqual(placement.y, 0.0)
        self.assertEqual(placement.z, 0.0)
        self.assertEqual(placement.rotation_z, 0.0)

    def test_cabinet_placement_accepts_explicit_coordinates(self):
        from domain.furniture_project import CabinetPlacement

        placement = CabinetPlacement(
            cabinet_id="C-1",
            x=1500.0,
            y=300.0,
            z=0.0,
            rotation_z=90.0,
        )

        self.assertEqual(placement.cabinet_id, "C-1")
        self.assertEqual(placement.x, 1500.0)
        self.assertEqual(placement.y, 300.0)
        self.assertEqual(placement.z, 0.0)
        self.assertEqual(placement.rotation_z, 90.0)


class TestFurnitureProjectPlacementContract(unittest.TestCase):

    def test_furniture_project_has_placements_field(self):
        from domain.furniture_project import FurnitureProject

        field_names = [field.name for field in fields(FurnitureProject)]
        self.assertIn("placements", field_names)

    def test_placements_defaults_to_empty_list(self):
        from domain.furniture_project import FurnitureProject

        project = FurnitureProject()

        self.assertEqual(project.placements, [])

    def test_placements_defaults_are_independent(self):
        from domain.furniture_project import FurnitureProject

        first = FurnitureProject()
        second = FurnitureProject()

        self.assertIsNot(first.placements, second.placements)


class TestFurnitureProjectBuilderPlacementExtension(unittest.TestCase):

    def test_existing_add_cabinet_still_works(self):
        from domain.furniture_project_builder import FurnitureProjectBuilder

        cabinet = self._cabinet("CABINET-1")

        project = FurnitureProjectBuilder().add_cabinet(cabinet).build()

        self.assertEqual(project.cabinets, [cabinet])
        self.assertEqual(project.placements, [])

    def test_add_cabinet_at_stores_cabinet_and_placement(self):
        from domain.furniture_project_builder import FurnitureProjectBuilder

        cabinet = self._cabinet("CABINET-1")

        project = (
            FurnitureProjectBuilder()
            .add_cabinet_at(cabinet, x=1000.0, y=200.0, z=0.0, rotation_z=90.0)
            .build()
        )

        self.assertEqual(project.cabinets, [cabinet])
        self.assertEqual(len(project.placements), 1)
        self.assertEqual(project.placements[0].cabinet_id, "CABINET-1")
        self.assertEqual(project.placements[0].x, 1000.0)
        self.assertEqual(project.placements[0].y, 200.0)
        self.assertEqual(project.placements[0].z, 0.0)
        self.assertEqual(project.placements[0].rotation_z, 90.0)

    def test_add_cabinet_at_defaults_rotation_z_to_zero(self):
        from domain.furniture_project_builder import FurnitureProjectBuilder

        cabinet = self._cabinet("CABINET-1")

        project = (
            FurnitureProjectBuilder()
            .add_cabinet_at(cabinet, x=500.0, y=100.0, z=0.0)
            .build()
        )

        self.assertEqual(project.placements[0].rotation_z, 0.0)

    def test_multiple_cabinets_have_different_placements(self):
        from domain.furniture_project_builder import FurnitureProjectBuilder

        cabinet_a = self._cabinet("CABINET-A")
        cabinet_b = self._cabinet("CABINET-B")

        project = (
            FurnitureProjectBuilder()
            .add_cabinet_at(cabinet_a, x=0.0, y=0.0, z=0.0, rotation_z=0.0)
            .add_cabinet_at(cabinet_b, x=1500.0, y=0.0, z=0.0, rotation_z=0.0)
            .build()
        )

        self.assertEqual(len(project.cabinets), 2)
        self.assertEqual(len(project.placements), 2)
        self.assertEqual(project.placements[0].cabinet_id, "CABINET-A")
        self.assertEqual(project.placements[0].x, 0.0)
        self.assertEqual(project.placements[1].cabinet_id, "CABINET-B")
        self.assertEqual(project.placements[1].x, 1500.0)

    def test_add_cabinet_at_respects_fluent_builder_chaining(self):
        from domain.furniture_project_builder import FurnitureProjectBuilder

        cabinet = self._cabinet("CABINET-1")

        builder = FurnitureProjectBuilder().add_cabinet_at(
            cabinet, x=100.0, y=100.0, z=0.0
        )

        self.assertIs(
            builder,
            builder.add_cabinet_at(
                self._cabinet("CABINET-2"), x=200.0, y=100.0, z=0.0
            ),
        )

    @staticmethod
    def _cabinet(uid):
        from domain.builders import WardrobeBuilder

        return WardrobeBuilder(
            uid=uid,
            width=1000,
            height=2000,
            depth=600,
        ).build()
