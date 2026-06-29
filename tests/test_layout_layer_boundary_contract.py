import inspect
import unittest
from dataclasses import fields, is_dataclass
from types import SimpleNamespace


class TestLayoutLayerBoundaryContract(unittest.TestCase):

    def test_layout_and_spatial_layers_remain_separate(self):
        from domain.furniture_project import CabinetPlacement, FurnitureProject
        from domain.furniture_project_builder import FurnitureProjectBuilder
        from layout.layout_engine import LayoutEngine
        from layout.layout_result import (
            DoorZone,
            DrawerZone,
            LayoutResult,
            ShelfZone,
        )

        self.assertEqual(
            [field.name for field in fields(LayoutResult)],
            [
                "drawer_zones",
                "door_zone",
                "shelf_zone",
                "shelf_placement_zone",
                "diagnostics",
            ],
        )

        layout_result = LayoutEngine().resolve_zones(self._layout_context())

        self.assertIsInstance(layout_result, LayoutResult)
        self.assertIsInstance(layout_result.drawer_zones, list)
        self.assertIsNotNone(layout_result.door_zone)
        self.assertIsNotNone(layout_result.shelf_zone)
        self.assertIsNotNone(layout_result.diagnostics)
        self.assertTrue(all(isinstance(zone, DrawerZone) for zone in layout_result.drawer_zones))
        self.assertIsInstance(layout_result.door_zone, DoorZone)
        self.assertIsInstance(layout_result.shelf_zone, ShelfZone)

        project = FurnitureProjectBuilder().add_cabinet_at(
            self._cabinet("CAB-1"),
            x=1200.0,
            y=0.0,
            z=0.0,
            rotation_z=90.0,
        ).build()

        self.assertIsInstance(project, FurnitureProject)
        self.assertEqual(project.placements, [project.placements[0]])
        self.assertIsInstance(project.placements[0], CabinetPlacement)
        self.assertEqual(project.placements[0].cabinet_id, "CAB-1")
        self.assertEqual(project.placements[0].x, 1200.0)
        self.assertEqual(project.placements[0].rotation_z, 90.0)

        self.assertEqual(FurnitureProject().placements, [])

        self.assertTrue(is_dataclass(DrawerZone))
        self.assertTrue(is_dataclass(DoorZone))
        self.assertTrue(is_dataclass(ShelfZone))
        self.assertTrue(is_dataclass(CabinetPlacement))

        self.assertIsNot(DrawerZone, DoorZone)
        self.assertIsNot(DrawerZone, ShelfZone)
        self.assertIsNot(DoorZone, ShelfZone)
        self.assertIsNot(CabinetPlacement, DrawerZone)
        self.assertIsNot(CabinetPlacement, DoorZone)
        self.assertIsNot(CabinetPlacement, ShelfZone)

    def test_open_section_with_shelves_creates_shelf_zone(self):
        from layout.layout_engine import LayoutEngine
        from layout.layout_context import LayoutContext
        from shared.enums import DoorType, DrawerLayoutMode

        context = LayoutContext(
            params=SimpleNamespace(),
            section_config=SimpleNamespace(
                drawers=0,
                shelves=1,
                drawer_layout_mode=DrawerLayoutMode.MANUAL,
                drawer_heights=[],
            ),
            mat=SimpleNamespace(
                default_drawer_height=100.0,
                clearance=2.0,
                door_top_gap=3.0,
                door_bottom_gap=4.0,
            ),
            available_height=500.0,
            base_z=0.0,
            door_type=DoorType.NONE,
            has_sliding=False,
            sliding_track=0.0,
        )

        result = LayoutEngine().resolve_zones(context)

        self.assertIsNone(result.door_zone)
        self.assertIsNone(result.shelf_zone)
        self.assertIsNotNone(result.shelf_placement_zone)
        self.assertEqual(result.shelf_placement_zone.__class__.__name__, "ShelfPlacementZone")
        self.assertAlmostEqual(result.shelf_placement_zone.z_start, 0.0)
        self.assertAlmostEqual(result.shelf_placement_zone.height, context.available_height)

    def test_import_boundaries_are_preserved(self):
        from domain import furniture_project, furniture_project_builder
        from layout import equal_layout, layout_engine, layout_result, manual_layout

        layout_sources = "\n".join(
            inspect.getsource(module)
            for module in (
                layout_engine,
                manual_layout,
                equal_layout,
                layout_result,
            )
        )
        for token in (
            "domain.furniture_project",
            "FurnitureProject",
            "CabinetPlacement",
        ):
            with self.subTest(layout_token=token):
                self.assertNotIn(token, layout_sources)

        furniture_project_sources = "\n".join(
            inspect.getsource(module)
            for module in (furniture_project, furniture_project_builder)
        )
        for token in ("layout.layout_engine", "LayoutEngine"):
            with self.subTest(project_token=token):
                self.assertNotIn(token, furniture_project_sources)

    def test_layout_execution_does_not_mutate_inputs(self):
        context = self._layout_context()
        original_context = self._snapshot(context)
        original_section_config = self._snapshot(context.section_config)
        original_mat = self._snapshot(context.mat)

        from layout.layout_engine import LayoutEngine

        LayoutEngine().resolve_zones(context)

        self.assertEqual(self._snapshot(context), original_context)
        self.assertEqual(
            self._snapshot(context.section_config),
            original_section_config,
        )
        self.assertEqual(self._snapshot(context.mat), original_mat)

    @staticmethod
    def _layout_context():
        from shared.enums import DoorType, DrawerLayoutMode
        from layout.layout_context import LayoutContext

        section_config = SimpleNamespace(
            drawers=1,
            shelves=1,
            drawer_layout_mode=DrawerLayoutMode.MANUAL,
            drawer_heights=[120.0],
        )
        mat = SimpleNamespace(
            default_drawer_height=100.0,
            clearance=2.0,
            door_top_gap=3.0,
            door_bottom_gap=4.0,
        )
        return LayoutContext(
            params=SimpleNamespace(),
            section_config=section_config,
            mat=mat,
            available_height=500.0,
            base_z=0.0,
            door_type=DoorType.INSET,
            has_sliding=False,
            sliding_track=0.0,
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

    @staticmethod
    def _snapshot(obj):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in obj.__dict__.items()
        }


if __name__ == "__main__":
    unittest.main()
