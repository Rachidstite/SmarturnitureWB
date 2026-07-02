import inspect
import unittest

import application.manufacturing_application_service as manufacturing_app_module
import cost_intelligence.manufacturing_commercial_pipeline_builder as commercial_pipeline_module
import cost_intelligence.manufacturing_cost_pipeline_builder as cost_pipeline_module
import domain.base_cabinet_product_workflow as workflow_module
import domain.compatibility_decision_rule as compatibility_rule_module
import domain.hardware_decision_builder as decision_builder_module
import domain.hardware_decision as decision_model_module
import domain.manufacturing_readiness_decision_rule as readiness_rule_module
import domain.operational_decision_rule as operational_rule_module
import domain.quality_decision_rule as quality_rule_module
import manufacturing.manufacturing_decision_builder as manufacturing_decision_builder_module
import manufacturing.manufacturing_package_builder as manufacturing_package_builder_module
import manufacturing.manufacturing_runtime_pipeline_builder as manufacturing_runtime_module


EXPECTED_RULE_ORDER = (
    "apply_compatibility_decision_rule",
    "apply_manufacturing_readiness_decision_rule",
    "apply_quality_decision_rule",
    "apply_operational_decision_rule",
)


class TestDecisionRuleIntegrationContract(unittest.TestCase):
    def test_hardware_decision_builder_remains_pure_mapper_without_rule_execution(self):
        source = inspect.getsource(decision_builder_module)

        self.assertIn("def build_hardware_decision(", source)
        for token in EXPECTED_RULE_ORDER:
            self.assertNotIn(token, source)

    def test_decision_rules_exist_as_pure_hardware_decision_transforms(self):
        rule_functions = (
            compatibility_rule_module.apply_compatibility_decision_rule,
            readiness_rule_module.apply_manufacturing_readiness_decision_rule,
            quality_rule_module.apply_quality_decision_rule,
            operational_rule_module.apply_operational_decision_rule,
        )

        for rule_fn in rule_functions:
            with self.subTest(rule=rule_fn.__name__):
                self.assertEqual(list(inspect.signature(rule_fn).parameters), ["decision"])

    def test_contract_documents_deterministic_rule_order(self):
        self.assertEqual(
            EXPECTED_RULE_ORDER,
            (
                "apply_compatibility_decision_rule",
                "apply_manufacturing_readiness_decision_rule",
                "apply_quality_decision_rule",
                "apply_operational_decision_rule",
            ),
        )

    def test_every_rule_returns_new_hardware_decision_by_contract(self):
        decision_source = inspect.getsource(decision_model_module)
        self.assertIn("class HardwareDecision", decision_source)

        for module in (
            compatibility_rule_module,
            readiness_rule_module,
            quality_rule_module,
            operational_rule_module,
        ):
            with self.subTest(module=module.__name__):
                source = inspect.getsource(module)
                self.assertIn("return replace(", source)

    def test_no_rule_mutates_previous_hardware_decision_instances(self):
        for module in (
            compatibility_rule_module,
            readiness_rule_module,
            quality_rule_module,
            operational_rule_module,
        ):
            with self.subTest(module=module.__name__):
                source = inspect.getsource(module)
                self.assertNotIn(".compatibility_status =", source)
                self.assertNotIn(".manufacturing_impact_note =", source)
                self.assertNotIn(".quality_impact_note =", source)
                self.assertNotIn(".replacement_reason =", source)

    def test_rule_order_is_independent_from_evidence_source_specific_branching(self):
        for module in (
            compatibility_rule_module,
            readiness_rule_module,
            quality_rule_module,
            operational_rule_module,
        ):
            with self.subTest(module=module.__name__):
                source = inspect.getsource(module).lower()
                self.assertNotIn('startswith("minifix', source)
                self.assertNotIn('startswith("confirmat', source)
                self.assertNotIn('startswith("backpanel', source)
                self.assertNotIn('startswith("drawer', source)
                self.assertNotIn('startswith("factoryoperational', source)
                self.assertNotIn('startswith("productionschedule', source)

    def test_manufacturing_pipeline_is_not_responsible_for_rule_execution(self):
        for module in (
            manufacturing_runtime_module,
            manufacturing_package_builder_module,
            manufacturing_decision_builder_module,
        ):
            with self.subTest(module=module.__name__):
                source = inspect.getsource(module)
                for token in EXPECTED_RULE_ORDER:
                    self.assertNotIn(token, source)

    def test_cost_and_commercial_pipelines_are_not_responsible_for_rule_execution(self):
        for module in (
            cost_pipeline_module,
            commercial_pipeline_module,
        ):
            with self.subTest(module=module.__name__):
                source = inspect.getsource(module)
                for token in EXPECTED_RULE_ORDER:
                    self.assertNotIn(token, source)

    def test_application_and_workflow_layers_are_the_future_orchestration_boundary(self):
        app_source = inspect.getsource(manufacturing_app_module)
        workflow_source = inspect.getsource(workflow_module)

        self.assertIn("Orchestrates", app_source)
        self.assertIn("build_base_cabinet_product_workflow", workflow_source)
        for token in EXPECTED_RULE_ORDER:
            self.assertNotIn(token, app_source)
            self.assertNotIn(token, workflow_source)

    def test_no_decision_orchestrator_or_helper_exists(self):
        for module in (
            decision_builder_module,
            manufacturing_app_module,
            workflow_module,
        ):
            with self.subTest(module=module.__name__):
                source = inspect.getsource(module).lower()
                self.assertNotIn("decisionorchestrator", source)
                self.assertNotIn("rulecoordinator", source)
                self.assertNotIn("helper", source)

    def test_future_cost_and_replacement_categories_must_fit_same_sequential_contract(self):
        self.assertEqual(
            EXPECTED_RULE_ORDER[-1],
            "apply_operational_decision_rule",
        )
        self.assertNotIn("apply_cost_decision_rule", EXPECTED_RULE_ORDER)
        self.assertNotIn("apply_replacement_decision_rule", EXPECTED_RULE_ORDER)


if __name__ == "__main__":
    unittest.main()
