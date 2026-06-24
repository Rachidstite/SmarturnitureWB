import inspect
import unittest
from dataclasses import fields, is_dataclass


class TestPlacementSemanticBoundaryContract(unittest.TestCase):

    def test_project_and_cabinet_placement_semantics_remain_separate(self):
        from domain.anchors import HardwarePlacement
        from domain.builders import WardrobeBuilder
        from domain.furniture_project import CabinetPlacement
        from domain.furniture_project_builder import FurnitureProjectBuilder
        from domain.rules_engine import HardwarePlacementEngine, RuleContext

        cabinet_builder = self._wardrobe_builder("CAB-1")
        cabinet_builder.add_shelves(count=1, section_id="ROOT")
        cabinet_project = cabinet_builder.build()
        original_cabinet_project_snapshot = self._snapshot(cabinet_project)

        furniture_project = (
            FurnitureProjectBuilder()
            .add_cabinet_at(
                self._wardrobe("FURN-1"),
                x=1200.0,
                y=0.0,
                z=0.0,
                rotation_z=90.0,
            )
            .build()
        )

        self.assertTrue(furniture_project.placements)
        self.assertTrue(
            all(isinstance(placement, CabinetPlacement) for placement in furniture_project.placements)
        )
        self.assertTrue(is_dataclass(CabinetPlacement))
        self.assertEqual(
            [field.name for field in fields(CabinetPlacement)],
            ["cabinet_id", "x", "y", "z", "rotation_z"],
        )
        self.assertTrue(
            all(
                not hasattr(placement, "hardware_intent")
                and not hasattr(placement, "host_node_id")
                and not hasattr(placement, "target_node_id")
                and not hasattr(placement, "anchor")
                for placement in furniture_project.placements
            )
        )

        original_furniture_project_snapshot = self._snapshot(furniture_project)

        self.assertEqual(
            self._snapshot(cabinet_project),
            original_cabinet_project_snapshot,
        )

        HardwarePlacementEngine(RuleContext()).process(cabinet_project)

        self.assertTrue(cabinet_project.placements)
        self.assertTrue(
            all(
                isinstance(placement, HardwarePlacement)
                for placement in cabinet_project.placements
            )
        )
        self.assertTrue(is_dataclass(HardwarePlacement))
        self.assertEqual(
            [field.name for field in fields(HardwarePlacement)],
            [
                "host_node_id",
                "hardware_intent",
                "anchor",
                "target_node_id",
                "description",
            ],
        )
        self.assertTrue(
            all(
                hasattr(placement, "hardware_intent")
                and hasattr(placement, "host_node_id")
                and hasattr(placement, "anchor")
                for placement in cabinet_project.placements
            )
        )
        self.assertTrue(
            all(
                not hasattr(placement, "cabinet_id")
                and not hasattr(placement, "rotation_z")
                for placement in cabinet_project.placements
            )
        )

        self.assertIsNot(
            furniture_project.placements,
            cabinet_project.placements,
        )
        self.assertTrue(
            all(
                isinstance(placement, CabinetPlacement)
                for placement in furniture_project.placements
            )
        )
        self.assertTrue(
            all(
                isinstance(placement, HardwarePlacement)
                for placement in cabinet_project.placements
            )
        )
        self.assertEqual(
            self._snapshot(furniture_project),
            original_furniture_project_snapshot,
        )

    def test_source_boundaries_do_not_cross_import_placement_layers(self):
        from domain import furniture_project, rules_engine
        from domain import furniture_project_builder

        layout_sources = inspect.getsource(rules_engine)
        self.assertNotIn("CabinetPlacement", layout_sources)

        furniture_project_source = inspect.getsource(furniture_project)
        self.assertNotIn("HardwarePlacement", furniture_project_source)

        furniture_project_builder_source = inspect.getsource(
            furniture_project_builder
        )
        self.assertNotIn("layout.layout_engine", furniture_project_builder_source)
        self.assertNotIn("LayoutEngine", furniture_project_builder_source)

    def test_placement_containers_are_not_interchangeable(self):
        from domain.anchors import HardwarePlacement
        from domain.builders import WardrobeBuilder
        from domain.furniture_project import CabinetPlacement
        from domain.furniture_project_builder import FurnitureProjectBuilder
        from domain.rules_engine import HardwarePlacementEngine, RuleContext

        furniture_project = (
            FurnitureProjectBuilder()
            .add_cabinet_at(self._wardrobe("FURN-2"), x=0.0, y=0.0, z=0.0)
            .build()
        )
        cabinet_builder = self._wardrobe_builder("CAB-2")
        cabinet_builder.add_shelves(count=1, section_id="ROOT")
        cabinet_project = cabinet_builder.build()
        HardwarePlacementEngine(RuleContext()).process(cabinet_project)

        self.assertTrue(all(isinstance(p, CabinetPlacement) for p in furniture_project.placements))
        self.assertTrue(all(isinstance(p, HardwarePlacement) for p in cabinet_project.placements))
        self.assertTrue(
            all(
                not hasattr(p, "cabinet_id")
                for p in cabinet_project.placements
            )
        )
        self.assertTrue(
            all(
                not hasattr(p, "hardware_intent")
                for p in furniture_project.placements
            )
        )

    @staticmethod
    def _wardrobe(uid):
        return TestPlacementSemanticBoundaryContract._wardrobe_builder(uid).build()

    @staticmethod
    def _wardrobe_builder(uid):
        from domain.builders import WardrobeBuilder

        return WardrobeBuilder(
            uid=uid,
            width=1000.0,
            height=2000.0,
            depth=600.0,
        )

    @staticmethod
    def _snapshot(obj):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in obj.__dict__.items()
        }


if __name__ == "__main__":
    unittest.main()
