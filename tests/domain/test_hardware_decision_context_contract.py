import inspect
import unittest
from dataclasses import FrozenInstanceError, fields, is_dataclass

import domain.hardware_decision_context as context_module
from domain.hardware_decision_context import HardwareDecisionContext


class TestHardwareDecisionContextContract(unittest.TestCase):
    def _sample_context(self) -> HardwareDecisionContext:
        return HardwareDecisionContext(
            context_id="CTX-HW-001",
            product_family="WALL_CABINET",
            cabinet_type="WALL",
            material_type="MDF",
            panel_thickness_mm=18.0,
            cabinet_width_mm=800.0,
            cabinet_height_mm=720.0,
            cabinet_depth_mm=350.0,
            mounting_type="wall",
            required_load_kg=35.0,
            available_hardware_skus=(
                "HINGE_BLUM_110_V1",
                "SCREW_4X40",
            ),
            manufacturing_capabilities=(
                "CNC_DRILLING",
                "MANUAL_ASSEMBLY",
            ),
            customer_constraints=(
                "NO_VISIBLE_HARDWARE",
                "SOFT_CLOSE_REQUIRED",
            ),
            notes=(
                "Wall substrate requires review",
            ),
        )

    def test_context_is_immutable(self):
        context = self._sample_context()

        self.assertTrue(is_dataclass(HardwareDecisionContext))
        with self.assertRaises(FrozenInstanceError):
            context.context_id = "MUTATED"

    def test_context_is_pure_domain_model(self):
        self.assertEqual(
            [field.name for field in fields(HardwareDecisionContext)],
            [
                "context_id",
                "product_family",
                "cabinet_type",
                "material_type",
                "panel_thickness_mm",
                "cabinet_width_mm",
                "cabinet_height_mm",
                "cabinet_depth_mm",
                "mounting_type",
                "required_load_kg",
                "available_hardware_skus",
                "manufacturing_capabilities",
                "customer_constraints",
                "notes",
            ],
        )

    def test_context_contains_no_builders_rules_or_recommendation_logic(self):
        source = inspect.getsource(context_module).lower()

        for token in (
            "builder",
            "rule_engine",
            "execute_rule",
            "evaluate_rule",
            "recommendation_engine",
            "recommend(",
            "workflow",
            "pipeline",
            "import agent",
            "from agent",
            "import ai",
            "from ai",
            "llm",
        ):
            self.assertNotIn(token, source)

    def test_context_has_no_forbidden_runtime_or_pipeline_dependencies(self):
        source = inspect.getsource(context_module).lower()

        for token in (
            "geometryengine",
            "scenegraph",
            "manufacturingruntimepipelinebuilder",
            "manufacturingpackagebuilder",
            "costpackagebuilder",
            "runtime",
            "freecad",
            "part",
            "applicationservice",
            "import ui",
            "from ui",
        ):
            self.assertNotIn(token, source)

    def test_context_is_suitable_as_future_hardware_decision_builder_input(self):
        context = self._sample_context()

        self.assertEqual(context.product_family, "WALL_CABINET")
        self.assertEqual(context.cabinet_type, "WALL")
        self.assertEqual(context.material_type, "MDF")
        self.assertEqual(context.panel_thickness_mm, 18.0)
        self.assertEqual(context.cabinet_width_mm, 800.0)
        self.assertEqual(context.cabinet_height_mm, 720.0)
        self.assertEqual(context.cabinet_depth_mm, 350.0)
        self.assertEqual(context.mounting_type, "wall")
        self.assertEqual(context.required_load_kg, 35.0)
        self.assertEqual(
            context.available_hardware_skus,
            ("HINGE_BLUM_110_V1", "SCREW_4X40"),
        )
        self.assertEqual(
            context.manufacturing_capabilities,
            ("CNC_DRILLING", "MANUAL_ASSEMBLY"),
        )
        self.assertEqual(
            context.customer_constraints,
            ("NO_VISIBLE_HARDWARE", "SOFT_CLOSE_REQUIRED"),
        )
        self.assertEqual(context.notes, ("Wall substrate requires review",))

    def test_context_is_independent_from_operational_and_hardware_decision_models(self):
        source = inspect.getsource(context_module)

        self.assertNotIn("from domain.operational_decision import", source)
        self.assertNotIn("from domain.hardware_decision import", source)


if __name__ == "__main__":
    unittest.main()
