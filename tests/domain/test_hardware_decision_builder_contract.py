import inspect
import unittest
from dataclasses import FrozenInstanceError

import domain.hardware_decision_builder as builder_module
from domain.hardware_decision import HardwareDecision
from domain.hardware_decision_context import HardwareDecisionContext
from domain.operational_decision import OperationalDecisionType


class TestHardwareDecisionBuilderContract(unittest.TestCase):
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
            manufacturing_capabilities=("CNC_DRILLING",),
            customer_constraints=("SOFT_CLOSE_REQUIRED",),
            notes=("Context-only input",),
        )

    def test_builder_exposes_pure_function_entrypoint(self):
        build_fn = getattr(builder_module, "build_hardware_decision", None)
        self.assertTrue(callable(build_fn))
        self.assertEqual(
            list(inspect.signature(build_fn).parameters),
            ["context"],
        )

    def test_builder_is_deterministic_for_same_context(self):
        context = self._sample_context()

        first = builder_module.build_hardware_decision(context)
        second = builder_module.build_hardware_decision(context)

        self.assertEqual(first, second)

    def test_builder_returns_immutable_hardware_decision(self):
        decision = builder_module.build_hardware_decision(self._sample_context())

        self.assertIsInstance(decision, HardwareDecision)
        with self.assertRaises(FrozenInstanceError):
            decision.selected_hardware_sku = "MUTATED"

    def test_builder_copies_only_explicit_context_values(self):
        context = self._sample_context()
        decision = builder_module.build_hardware_decision(context)

        self.assertEqual(decision.decision.decision_id, context.context_id)
        self.assertEqual(
            decision.decision.decision_type,
            OperationalDecisionType.HARDWARE,
        )
        self.assertEqual(
            decision.candidate_hardware_skus,
            context.available_hardware_skus,
        )
        self.assertEqual(
            tuple(option.option_id for option in decision.decision.candidate_options),
            context.available_hardware_skus,
        )
        self.assertEqual(
            tuple(option.label for option in decision.decision.candidate_options),
            context.available_hardware_skus,
        )

    def test_missing_information_remains_unset_or_default(self):
        decision = builder_module.build_hardware_decision(self._sample_context())

        self.assertIsNone(decision.decision.selected_option)
        self.assertEqual(decision.selected_hardware_sku, "")
        self.assertEqual(decision.rejected_hardware_skus, ())
        self.assertEqual(decision.manufacturing_impact_note, "")
        self.assertEqual(decision.cost_impact_note, "")
        self.assertEqual(decision.quality_impact_note, "")
        self.assertFalse(decision.replacement_allowed)
        self.assertEqual(decision.replacement_reason, "")
        self.assertEqual(decision.decision.reason, "")
        self.assertEqual(decision.decision.traceability.source_component, "")

    def test_builder_does_not_mutate_context(self):
        context = self._sample_context()
        before = context

        builder_module.build_hardware_decision(context)

        self.assertEqual(context, before)

    def test_builder_has_no_rules_recommendation_ai_or_runtime_dependencies(self):
        source = inspect.getsource(builder_module).lower()

        for token in (
            "rule_engine",
            "execute_rule",
            "evaluate_rule",
            "recommendation_engine",
            "recommend(",
            "agent",
            "llm",
            "geometryengine",
            "scenegraph",
            "manufacturingruntimepipelinebuilder",
            "manufacturingpackagebuilder",
            "costpackagebuilder",
            "applicationservice",
            "freecad",
            "runtime",
        ):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
