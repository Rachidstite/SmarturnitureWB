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

    @staticmethod
    def _fake_cost_summary(cost_report):
        return type(
            "ManufacturingCostSummary",
            (),
            {
                "cost_report": cost_report,
                "risk_report": object(),
                "insights": object(),
                "total_manufacturing_cost": 123.0,
                "hardware_cost": 0.0,
                "risk_level": "LOW",
                "warnings": [],
            },
        )()

    @staticmethod
    def _fake_commercial_result():
        return type(
            "ManufacturingCommercialResult",
            (),
            {
                "manufacturing_cost_summary": object(),
                "manufacturing_quotation_input": object(),
                "quotation_report": type(
                    "QuotationReport",
                    (),
                    {
                        "selling_price": 2500.0,
                        "currency": "MAD",
                    },
                )(),
                "profitability_report": object(),
                "quotation_intelligence_report": object(),
            },
        )()

    @staticmethod
    def _fake_quotation_document():
        return type(
            "QuotationDocumentV1",
            (),
            {
                "quotation_number": "Q-2026-001",
                "issue_date": "2026-06-15",
                "valid_until": "2026-07-15",
                "seller_name": "Smart Furniture",
                "customer_name": "Example Customer",
                "project_description": "Custom base cabinet",
                "total_amount": 2500.0,
                "currency": "MAD",
                "notes": "",
                "payment_terms": "",
            },
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

    def test_uses_cost_bridge(self):
        specification = BaseCabinetSpecification()
        scene_graph = object()
        manufacturing_package = object()
        cost_report = object()
        cost_summary = self._fake_cost_summary(cost_report)
        warnings = ["Missing edge data"]

        from manufacturing.manufacturing_cutlist_report import (
            ManufacturingCutlistReport,
        )
        from manufacturing.manufacturing_edge_report import ManufacturingEdgeReport
        from manufacturing.manufacturing_machining_report import (
            ManufacturingMachiningReport,
        )
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )
        from manufacturing.manufacturing_summary_report import (
            ManufacturingSummaryReport,
        )

        production_package = ManufacturingProductionPackage(
            cutlist_report=ManufacturingCutlistReport(
                items=[
                    {
                        "identity": "panel-01",
                        "width": 100.0,
                        "height": 200.0,
                        "thickness": 18.0,
                        "material": "MDF",
                        "quantity": 1,
                    }
                ],
                total_items=1,
                warnings=warnings,
            ),
            edge_report=ManufacturingEdgeReport(
                items=[
                    {
                        "panel_identity": "panel-01",
                        "edge": "TOP",
                        "banding": "ABS_1MM",
                        "linear_meters": 0.1,
                    }
                ],
                total_items=1,
                total_linear_meters=0.1,
                warnings=warnings,
            ),
            machining_report=ManufacturingMachiningReport(
                items=[
                    {
                        "operation_type": "DRILL",
                        "diameter": 5.0,
                        "depth": 12.0,
                        "is_through": False,
                        "x": 100.0,
                        "y": 200.0,
                        "z": 0.0,
                        "face": "TOP",
                        "axis": "Z",
                        "source": "panel-01",
                    }
                ],
                total_items=1,
                warnings=warnings,
            ),
            summary_report=ManufacturingSummaryReport(
                total_panels=1,
                total_materials=1,
                total_edge_operations=1,
                total_machining_operations=1,
                warnings=warnings,
            ),
            warnings=warnings,
        )

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
            return_value=type(
                "Outputs",
                (),
                {
                    "metadata": {},
                    "manufacturing_package": manufacturing_package,
                },
            )(),
        ), patch.object(
            workflow_module,
            "ManufacturingProductionPackageBuilder",
        ) as production_package_builder_class, patch.object(
            workflow_module,
            "ManufacturingCostPipelineBuilder",
        ) as cost_pipeline_builder_class:
            manufacturing_validation_service_class.validate.return_value = (
                self._fake_manufacturing_state([])
            )
            production_package_builder_class.return_value.build.return_value = (
                production_package
            )
            cost_pipeline_builder_class.return_value.build.return_value = (
                cost_summary
            )
            result = build_base_cabinet_product_workflow(specification)

        production_package_builder_class.return_value.build.assert_called_once_with(
            manufacturing_package
        )
        cost_pipeline_builder_class.return_value.build.assert_called_once_with(
            production_package
        )
        self.assertIs(result.cost.manufacturing_production_package, production_package)
        self.assertIs(result.cost.manufacturing_cost_summary, cost_summary)
        self.assertIs(result.cost.manufacturing_cost_report, cost_report)

    def test_uses_commercial_bridge(self):
        specification = BaseCabinetSpecification()
        scene_graph = object()
        manufacturing_package = object()
        cost_summary = self._fake_cost_summary(object())
        commercial_result = self._fake_commercial_result()
        quotation_document = self._fake_quotation_document()
        warnings = ["Missing edge data"]

        from manufacturing.manufacturing_cutlist_report import (
            ManufacturingCutlistReport,
        )
        from manufacturing.manufacturing_edge_report import ManufacturingEdgeReport
        from manufacturing.manufacturing_machining_report import (
            ManufacturingMachiningReport,
        )
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )
        from manufacturing.manufacturing_summary_report import (
            ManufacturingSummaryReport,
        )

        production_package = ManufacturingProductionPackage(
            cutlist_report=ManufacturingCutlistReport(
                items=[
                    {
                        "identity": "panel-01",
                        "width": 100.0,
                        "height": 200.0,
                        "thickness": 18.0,
                        "material": "MDF",
                        "quantity": 1,
                    }
                ],
                total_items=1,
                warnings=warnings,
            ),
            edge_report=ManufacturingEdgeReport(
                items=[
                    {
                        "panel_identity": "panel-01",
                        "edge": "TOP",
                        "banding": "ABS_1MM",
                        "linear_meters": 0.1,
                    }
                ],
                total_items=1,
                total_linear_meters=0.1,
                warnings=warnings,
            ),
            machining_report=ManufacturingMachiningReport(
                items=[
                    {
                        "operation_type": "DRILL",
                        "diameter": 5.0,
                        "depth": 12.0,
                        "is_through": False,
                        "x": 100.0,
                        "y": 200.0,
                        "z": 0.0,
                        "face": "TOP",
                        "axis": "Z",
                        "source": "panel-01",
                    }
                ],
                total_items=1,
                warnings=warnings,
            ),
            summary_report=ManufacturingSummaryReport(
                total_panels=1,
                total_materials=1,
                total_edge_operations=1,
                total_machining_operations=1,
                warnings=warnings,
            ),
            warnings=warnings,
        )

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
            return_value=type(
                "Outputs",
                (),
                {
                    "metadata": {
                        "quotation_number": "Q-2026-001",
                        "issue_date": "2026-06-15",
                        "valid_until": "2026-07-15",
                        "seller_name": "Smart Furniture",
                        "customer_name": "Example Customer",
                        "project_description": "Custom base cabinet",
                    },
                    "manufacturing_package": manufacturing_package,
                },
            )(),
        ), patch.object(
            workflow_module,
            "ManufacturingProductionPackageBuilder",
        ) as production_package_builder_class, patch.object(
            workflow_module,
            "ManufacturingCostPipelineBuilder",
        ) as cost_pipeline_builder_class, patch.object(
            workflow_module,
            "ManufacturingCommercialPipelineBuilder",
        ) as commercial_pipeline_builder_class, patch.object(
            workflow_module,
            "QuotationDocumentBuilderV1",
        ) as quotation_document_builder_class:
            manufacturing_validation_service_class.validate.return_value = (
                self._fake_manufacturing_state([])
            )
            production_package_builder_class.return_value.build.return_value = (
                production_package
            )
            cost_pipeline_builder_class.return_value.build.return_value = (
                cost_summary
            )
            commercial_pipeline_builder_class.return_value.build.return_value = (
                commercial_result
            )
            quotation_document_builder_class.return_value.build.return_value = (
                quotation_document
            )
            result = build_base_cabinet_product_workflow(specification)

        commercial_pipeline_builder_class.return_value.build.assert_called_once_with(
            production_package
        )
        quotation_document_builder_class.return_value.build.assert_called_once()
        self.assertIs(result.commercial.commercial_result, commercial_result)
        self.assertIs(result.commercial.quotation_document, quotation_document)
        self.assertIs(result.quotation_document, quotation_document)

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
        self.assertNotIn("ManufacturingCostCalculator", source)
        self.assertNotIn("ManufacturingCostContextBuilder", source)
        self.assertNotIn("ManufacturingCostInsightsBuilder", source)
        self.assertNotIn("ManufacturingCostRiskReportBuilder", source)
        self.assertNotIn("ManufacturingQuotationInputBuilder", source)
        self.assertNotIn("ManufacturingQuotationReportBuilder", source)
        self.assertNotIn("QuotationCalculator", source)

    def test_no_freecad_import_in_source(self):
        source = inspect.getsource(workflow_module)
        self.assertNotIn("FreeCAD", source)


class FakeEngineeringCabinet:
    def __init__(self, scene_graph):
        self.graph = scene_graph


if __name__ == "__main__":
    unittest.main()
