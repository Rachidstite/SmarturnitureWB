import inspect
import unittest
from unittest.mock import patch

import domain.base_cabinet_product_workflow as workflow_module
from domain.base_cabinet_product_result import BaseCabinetProductResult
from domain.base_cabinet_product_workflow import (
    build_base_cabinet_product_workflow,
)
from domain.base_cabinet_scenario import BaseCabinetScenario
from domain.base_cabinet_specification import BaseCabinetSpecification


class TestBaseCabinetProductWorkflowContract(unittest.TestCase):
    @staticmethod
    def _fake_engineering_validation_report(violations):
        return type("EngineeringValidationReport", (), {"violations": violations})()

    @staticmethod
    def _fake_manufacturing_state(issues):
        return type("ManufacturingValidationState", (), {"issues": issues})()

    @staticmethod
    def _fake_manufacturing_report():
        return type(
            "ManufacturingValidationReport",
            (),
            {"ready_for_manufacturing": True},
        )()

    @staticmethod
    def _fake_manufacturing_summary():
        return type(
            "ManufacturingValidationSummaryReport",
            (),
            {"ready_for_manufacturing": True},
        )()

    def test_accepts_base_cabinet_specification(self):
        specification = BaseCabinetSpecification()
        scene_graph = object()
        engineering_violations = [object()]
        manufacturing_issues = [object()]

        with patch.object(
            workflow_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=FakeEngineeringCabinet(scene_graph),
        ) as engineering_entry, patch.object(
            workflow_module,
            "validate_base_cabinet_specification",
            return_value=self._fake_engineering_validation_report(
                engineering_violations
            ),
        ) as validation_entry, patch.object(
            workflow_module,
            "ManufacturingValidationService",
        ) as manufacturing_validation_service_class, patch.object(
            workflow_module,
            "build_manufacturing_validation_report",
            return_value=self._fake_manufacturing_report(),
        ) as manufacturing_report_builder, patch.object(
            workflow_module,
            "build_manufacturing_validation_summary_report",
            return_value=self._fake_manufacturing_summary(),
        ) as manufacturing_summary_builder, patch.object(
            workflow_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=type("Outputs", (), {"metadata": {}})(),
        ) as outputs_entry:
            manufacturing_validation_service_class.validate.return_value = (
                self._fake_manufacturing_state(manufacturing_issues)
            )
            result = build_base_cabinet_product_workflow(specification)

        engineering_entry.assert_called_once_with(specification)
        validation_entry.assert_called_once_with(specification)
        manufacturing_validation_service_class.validate.assert_called_once_with(
            scene_graph
        )
        manufacturing_report_builder.assert_called_once()
        manufacturing_summary_builder.assert_called_once()
        outputs_entry.assert_called_once_with(specification)
        self.assertIsInstance(result, BaseCabinetProductResult)
        self.assertIs(result.validation.engineering_validation_report, validation_entry.return_value)
        self.assertIs(
            result.validation.manufacturing_validation_state,
            manufacturing_validation_service_class.validate.return_value,
        )
        self.assertIs(
            result.validation.manufacturing_validation_report,
            manufacturing_report_builder.return_value,
        )
        self.assertIs(
            result.validation.manufacturing_validation_summary_report,
            manufacturing_summary_builder.return_value,
        )
        self.assertEqual(result.diagnostics, tuple(engineering_violations + manufacturing_issues))

    def test_returns_base_cabinet_product_result(self):
        specification = BaseCabinetSpecification()
        scene_graph = object()

        with patch.object(
            workflow_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=FakeEngineeringCabinet(scene_graph),
        ), patch.object(
            workflow_module,
            "validate_base_cabinet_specification",
            return_value=self._fake_engineering_validation_report([]),
        ), patch.object(
            workflow_module,
            "ManufacturingValidationService",
        ) as manufacturing_validation_service_class, patch.object(
            workflow_module,
            "build_manufacturing_validation_report",
            return_value=self._fake_manufacturing_report(),
        ), patch.object(
            workflow_module,
            "build_manufacturing_validation_summary_report",
            return_value=self._fake_manufacturing_summary(),
        ), patch.object(
            workflow_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=type("Outputs", (), {"metadata": {}})(),
        ) as outputs_entry:
            manufacturing_validation_service_class.validate.return_value = (
                self._fake_manufacturing_state([])
            )
            result = build_base_cabinet_product_workflow(specification)

        self.assertIsInstance(result, BaseCabinetProductResult)
        outputs_entry.assert_called_once_with(specification)

    def test_uses_engineering_entry(self):
        specification = BaseCabinetSpecification()
        scene_graph = object()

        with patch.object(
            workflow_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=FakeEngineeringCabinet(scene_graph),
        ) as engineering_entry, patch.object(
            workflow_module,
            "validate_base_cabinet_specification",
            return_value=self._fake_engineering_validation_report([]),
        ), patch.object(
            workflow_module,
            "ManufacturingValidationService",
        ) as manufacturing_validation_service_class, patch.object(
            workflow_module,
            "build_manufacturing_validation_report",
            return_value=self._fake_manufacturing_report(),
        ), patch.object(
            workflow_module,
            "build_manufacturing_validation_summary_report",
            return_value=self._fake_manufacturing_summary(),
        ), patch.object(
            workflow_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=type("Outputs", (), {"metadata": {}})(),
        ):
            manufacturing_validation_service_class.validate.return_value = (
                self._fake_manufacturing_state([])
            )
            build_base_cabinet_product_workflow(specification)

        engineering_entry.assert_called_once_with(specification)

    def test_uses_validation_entry(self):
        specification = BaseCabinetSpecification()
        scene_graph = object()

        with patch.object(
            workflow_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=FakeEngineeringCabinet(scene_graph),
        ), patch.object(
            workflow_module,
            "validate_base_cabinet_specification",
            return_value=self._fake_engineering_validation_report([]),
        ) as validation_entry, patch.object(
            workflow_module,
            "ManufacturingValidationService",
        ) as manufacturing_validation_service_class, patch.object(
            workflow_module,
            "build_manufacturing_validation_report",
            return_value=self._fake_manufacturing_report(),
        ), patch.object(
            workflow_module,
            "build_manufacturing_validation_summary_report",
            return_value=self._fake_manufacturing_summary(),
        ), patch.object(
            workflow_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=type("Outputs", (), {"metadata": {}})(),
        ):
            manufacturing_validation_service_class.validate.return_value = (
                self._fake_manufacturing_state([])
            )
            build_base_cabinet_product_workflow(specification)

        validation_entry.assert_called_once_with(specification)

    def test_uses_manufacturing_outputs_entry(self):
        specification = BaseCabinetSpecification()
        scene_graph = object()
        manufacturing_outputs = type("Outputs", (), {"metadata": {}})()

        with patch.object(
            workflow_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=FakeEngineeringCabinet(scene_graph),
        ), patch.object(
            workflow_module,
            "validate_base_cabinet_specification",
            return_value=self._fake_engineering_validation_report([]),
        ), patch.object(
            workflow_module,
            "ManufacturingValidationService",
        ) as manufacturing_validation_service_class, patch.object(
            workflow_module,
            "build_manufacturing_validation_report",
            return_value=self._fake_manufacturing_report(),
        ), patch.object(
            workflow_module,
            "build_manufacturing_validation_summary_report",
            return_value=self._fake_manufacturing_summary(),
        ), patch.object(
            workflow_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=manufacturing_outputs,
        ) as outputs_entry:
            manufacturing_validation_service_class.validate.return_value = (
                self._fake_manufacturing_state([])
            )
            result = build_base_cabinet_product_workflow(specification)

        outputs_entry.assert_called_once_with(specification)
        self.assertIs(result.manufacturing_outputs, manufacturing_outputs)

    def test_includes_scenario(self):
        specification = BaseCabinetSpecification()
        scene_graph = object()

        with patch.object(
            workflow_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=FakeEngineeringCabinet(scene_graph),
        ), patch.object(
            workflow_module,
            "validate_base_cabinet_specification",
            return_value=self._fake_engineering_validation_report([]),
        ), patch.object(
            workflow_module,
            "ManufacturingValidationService",
        ) as manufacturing_validation_service_class, patch.object(
            workflow_module,
            "build_manufacturing_validation_report",
            return_value=self._fake_manufacturing_report(),
        ), patch.object(
            workflow_module,
            "build_manufacturing_validation_summary_report",
            return_value=self._fake_manufacturing_summary(),
        ), patch.object(
            workflow_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=type("Outputs", (), {"metadata": {}})(),
        ):
            manufacturing_validation_service_class.validate.return_value = (
                self._fake_manufacturing_state([])
            )
            result = build_base_cabinet_product_workflow(specification)

        self.assertIsInstance(result.scenario, BaseCabinetScenario)
        self.assertIs(result.scenario.specification, specification)

    def test_preserves_metadata(self):
        specification = BaseCabinetSpecification()
        scene_graph = object()
        metadata = {"door_count": 2, "drawer_family": "NONE"}

        with patch.object(
            workflow_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=FakeEngineeringCabinet(scene_graph),
        ), patch.object(
            workflow_module,
            "validate_base_cabinet_specification",
            return_value=self._fake_engineering_validation_report([]),
        ), patch.object(
            workflow_module,
            "ManufacturingValidationService",
        ) as manufacturing_validation_service_class, patch.object(
            workflow_module,
            "build_manufacturing_validation_report",
            return_value=self._fake_manufacturing_report(),
        ), patch.object(
            workflow_module,
            "build_manufacturing_validation_summary_report",
            return_value=self._fake_manufacturing_summary(),
        ), patch.object(
            workflow_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=type("Outputs", (), {"metadata": metadata})(),
        ):
            manufacturing_validation_service_class.validate.return_value = (
                self._fake_manufacturing_state([])
            )
            result = build_base_cabinet_product_workflow(specification)

        self.assertEqual(result.metadata, metadata)
        self.assertIsNot(result.metadata, metadata)

    def test_fills_diagnostics(self):
        specification = BaseCabinetSpecification()
        scene_graph = object()
        engineering_violations = [object(), object()]
        manufacturing_issues = [object()]

        with patch.object(
            workflow_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=FakeEngineeringCabinet(scene_graph),
        ), patch.object(
            workflow_module,
            "validate_base_cabinet_specification",
            return_value=self._fake_engineering_validation_report(
                engineering_violations
            ),
        ), patch.object(
            workflow_module,
            "ManufacturingValidationService",
        ) as manufacturing_validation_service_class, patch.object(
            workflow_module,
            "build_manufacturing_validation_report",
            return_value=self._fake_manufacturing_report(),
        ), patch.object(
            workflow_module,
            "build_manufacturing_validation_summary_report",
            return_value=self._fake_manufacturing_summary(),
        ), patch.object(
            workflow_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=type("Outputs", (), {"metadata": {}})(),
        ):
            manufacturing_validation_service_class.validate.return_value = (
                self._fake_manufacturing_state(manufacturing_issues)
            )
            result = build_base_cabinet_product_workflow(specification)

        self.assertEqual(
            result.diagnostics,
            tuple(engineering_violations + manufacturing_issues),
        )

    def test_populates_validation_artifacts(self):
        specification = BaseCabinetSpecification()
        scene_graph = object()
        engineering_violations = [object()]
        manufacturing_issues = [object(), object()]
        engineering_validation_report = self._fake_engineering_validation_report(
            engineering_violations
        )
        manufacturing_validation_state = self._fake_manufacturing_state(
            manufacturing_issues
        )
        manufacturing_validation_report = self._fake_manufacturing_report()
        manufacturing_validation_summary_report = (
            self._fake_manufacturing_summary()
        )

        with patch.object(
            workflow_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=FakeEngineeringCabinet(scene_graph),
        ), patch.object(
            workflow_module,
            "validate_base_cabinet_specification",
            return_value=engineering_validation_report,
        ), patch.object(
            workflow_module,
            "ManufacturingValidationService",
        ) as manufacturing_validation_service_class, patch.object(
            workflow_module,
            "build_manufacturing_validation_report",
            return_value=manufacturing_validation_report,
        ) as manufacturing_report_builder, patch.object(
            workflow_module,
            "build_manufacturing_validation_summary_report",
            return_value=manufacturing_validation_summary_report,
        ) as manufacturing_summary_builder, patch.object(
            workflow_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=type("Outputs", (), {"metadata": {}})(),
        ):
            manufacturing_validation_service_class.validate.return_value = (
                manufacturing_validation_state
            )
            result = build_base_cabinet_product_workflow(specification)

        self.assertIs(result.validation.engineering_validation_report, engineering_validation_report)
        self.assertIs(result.validation.manufacturing_validation_state, manufacturing_validation_state)
        self.assertIs(result.validation.manufacturing_validation_report, manufacturing_validation_report)
        self.assertIs(result.validation.manufacturing_validation_summary_report, manufacturing_validation_summary_report)
        self.assertEqual(
            len(result.validation.manufacturing_validation_rule_results),
            len(manufacturing_issues),
        )
        self.assertTrue(
            all(
                rule_result.severity == "error"
                for rule_result in result.validation.manufacturing_validation_rule_results
            )
        )
        manufacturing_report_builder.assert_called_once()
        manufacturing_summary_builder.assert_called_once()

    def test_no_direct_builder_imports(self):
        source = inspect.getsource(workflow_module)
        self.assertNotIn("CabinetBuilder", source)
        self.assertNotIn("ManufacturingRuntimePipelineBuilder", source)
        self.assertNotIn("ManufacturingCutlistBuilder", source)

    def test_no_freecad_import_in_source(self):
        source = inspect.getsource(workflow_module)
        self.assertNotIn("FreeCAD", source)


class FakeEngineeringCabinet:
    def __init__(self, scene_graph):
        self.graph = scene_graph


if __name__ == "__main__":
    unittest.main()
