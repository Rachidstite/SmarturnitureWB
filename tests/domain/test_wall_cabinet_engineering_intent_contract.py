import inspect
import unittest
from unittest.mock import patch

import domain.base_cabinet_engineering_entry as engineering_entry_module
import domain.wall_cabinet_engineering_intent as wall_entry_module
from domain.wall_cabinet_engineering_intent import (
    WallCabinetEngineeringIntentResult,
    build_wall_cabinet_engineering_intent,
)
from domain.wall_cabinet_specification import WallCabinetSpecification


class TestWallCabinetEngineeringIntentContract(unittest.TestCase):
    def test_build_wall_cabinet_engineering_intent_returns_result_object(self):
        specification = WallCabinetSpecification()

        result = build_wall_cabinet_engineering_intent(specification)

        self.assertIsInstance(result, WallCabinetEngineeringIntentResult)

    def test_result_preserves_the_wall_cabinet_specification(self):
        specification = WallCabinetSpecification(
            width_mm=700.0,
            height_mm=800.0,
            depth_mm=360.0,
            wall_type="MASONRY",
        )

        result = build_wall_cabinet_engineering_intent(specification)

        self.assertIs(result.specification, specification)
        self.assertEqual(result.specification.wall_type, "MASONRY")

    def test_result_marks_mounting_type_and_support_strategy(self):
        result = build_wall_cabinet_engineering_intent(WallCabinetSpecification())

        self.assertEqual(result.mounting_type, "wall")
        self.assertEqual(result.support_strategy, "wall_mounted")

    def test_result_marks_executable_geometry_false(self):
        result = build_wall_cabinet_engineering_intent(WallCabinetSpecification())

        self.assertFalse(result.executable_geometry)

    def test_reason_clearly_states_intent_only(self):
        result = build_wall_cabinet_engineering_intent(WallCabinetSpecification())

        self.assertIn("intent only", result.reason.lower())
        self.assertIn("wall cabinet", result.reason.lower())

    def test_no_forbidden_runtime_imports_or_calls(self):
        source = inspect.getsource(wall_entry_module)
        lowered = source.lower()
        for token in (
            "cabinetbuilder",
            "constructionresolver",
            "basecabinetengineeringmodelbuilder",
            "manufacturing",
            "cost",
            "commercial",
            "application",
        ):
            self.assertNotIn(token, lowered)

    def test_base_cabinet_engineering_contract_remains_unchanged(self):
        from domain.base_cabinet_engineering_entry import (
            build_base_cabinet_engineering_cabinet,
        )
        from domain.base_cabinet_specification import BaseCabinetSpecification

        class FakeCabinetBuilder:
            def __init__(self):
                self.scene_graph = object()

            def build(self, cabinet):
                cabinet.graph = self.scene_graph
                cabinet.scene_graph = self.scene_graph

        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=FakeCabinetBuilder,
        ):
            cabinet = build_base_cabinet_engineering_cabinet(
                BaseCabinetSpecification()
            )

        self.assertIsNotNone(cabinet.construction_model)
        self.assertIsNotNone(cabinet.engineering_model)


if __name__ == "__main__":
    unittest.main()
