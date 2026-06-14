import unittest
from unittest.mock import patch


class TestProjectCostCalculator(unittest.TestCase):

    def test_project_cost_calculator_exists(self):

        try:
            from cost_intelligence.project_cost_calculator import (
                ProjectCostCalculator,
            )
        except ImportError:
            self.fail(
                "ProjectCostCalculator does not exist"
            )

    def test_project_cost_calculator_orchestrates_existing_calculators(self):

        from cost_intelligence.cost_estimate import CostEstimate
        from cost_intelligence.cost_report import CostReport
        from cost_intelligence.project_cost_calculator import (
            ProjectCostCalculator,
        )

        material_estimate = CostEstimate(
            material_cost=50,
        )
        sheet_estimate = CostEstimate(
            sheet_cost=560,
        )
        waste_estimate = CostEstimate(
            waste_cost=84,
        )
        hardware_estimate = CostEstimate(
            hardware_cost=48,
        )

        with patch(
            "cost_intelligence.project_cost_calculator.MaterialCostCalculator"
        ) as material_calculator, patch(
            "cost_intelligence.project_cost_calculator.SheetCostCalculator"
        ) as sheet_calculator, patch(
            "cost_intelligence.project_cost_calculator.WasteCostCalculator"
        ) as waste_calculator, patch(
            "cost_intelligence.project_cost_calculator.HardwareCostCalculator"
        ) as hardware_calculator, patch(
            "cost_intelligence.project_cost_calculator.HardwareReportCostService"
        ) as hardware_report_cost_service:
            material_calculator.return_value.estimate.return_value = (
                material_estimate
            )
            sheet_calculator.return_value.estimate.return_value = (
                sheet_estimate
            )
            waste_calculator.return_value.estimate.return_value = (
                waste_estimate
            )
            hardware_calculator.return_value.estimate.return_value = (
                hardware_estimate
            )

            report = ProjectCostCalculator().estimate(
                cutlist_items=[],
                nesting_results={},
                hardware_items=[],
                pricing_catalog={},
            )

        material_calculator.return_value.estimate.assert_called_once()
        sheet_calculator.return_value.estimate.assert_called_once()
        waste_calculator.return_value.estimate.assert_called_once()
        hardware_calculator.return_value.estimate.assert_called_once()
        hardware_report_cost_service.estimate.assert_not_called()

        self.assertIsInstance(
            report,
            CostReport,
        )

        self.assertEqual(
            report.total_cost,
            608,
        )

        self.assertEqual(
            report.material_cost,
            50,
        )

        self.assertEqual(
            report.waste_cost,
            84,
        )

    def test_scene_graph_path_uses_hardware_report_cost_service(self):

        from cost_intelligence.cost_estimate import CostEstimate
        from cost_intelligence.project_cost_calculator import (
            ProjectCostCalculator,
        )

        scene_graph = object()
        pricing_catalog = {"HINGE_BLUM_110_V1": {"unit_price": 6.0}}
        material_estimate = CostEstimate(material_cost=50)
        sheet_estimate = CostEstimate(sheet_cost=560)
        waste_estimate = CostEstimate(waste_cost=84)
        hardware_estimate = CostEstimate(hardware_cost=48)
        summary = CostEstimate(hardware_cost=48, total_cost=608)

        with patch(
            "cost_intelligence.project_cost_calculator.MaterialCostCalculator"
        ) as material_calculator, patch(
            "cost_intelligence.project_cost_calculator.SheetCostCalculator"
        ) as sheet_calculator, patch(
            "cost_intelligence.project_cost_calculator.WasteCostCalculator"
        ) as waste_calculator, patch(
            "cost_intelligence.project_cost_calculator.HardwareCostCalculator"
        ) as hardware_calculator, patch(
            "cost_intelligence.project_cost_calculator.HardwareReportCostService"
        ) as hardware_report_cost_service, patch(
            "cost_intelligence.project_cost_calculator.CostSummaryCalculator"
        ) as summary_calculator:
            material_calculator.return_value.estimate.return_value = (
                material_estimate
            )
            sheet_calculator.return_value.estimate.return_value = sheet_estimate
            waste_calculator.return_value.estimate.return_value = waste_estimate
            hardware_report_cost_service.estimate.return_value = hardware_estimate
            summary_calculator.return_value.estimate.return_value = summary

            ProjectCostCalculator().estimate(
                pricing_catalog=pricing_catalog,
                scene_graph=scene_graph,
            )

        hardware_report_cost_service.estimate.assert_called_once_with(
            scene_graph,
            pricing_catalog=pricing_catalog,
        )
        passed_pricing_catalog = (
            hardware_report_cost_service.estimate.call_args.kwargs[
                "pricing_catalog"
            ]
        )
        self.assertIs(passed_pricing_catalog, pricing_catalog)
        hardware_calculator.assert_not_called()
        summary_calculator.return_value.estimate.assert_called_once_with(
            material_estimate=material_estimate,
            sheet_estimate=sheet_estimate,
            waste_estimate=waste_estimate,
            hardware_estimate=hardware_estimate,
        )

    def test_scene_graph_and_hardware_items_raise_value_error_before_costing(self):
        self._assert_hardware_source_conflict_raises(
            hardware_items=[{"sku": "HINGE_BLUM_110_V1", "quantity": 4}]
        )

    def test_scene_graph_and_empty_hardware_items_raise_value_error_before_costing(
        self,
    ):
        self._assert_hardware_source_conflict_raises(hardware_items=[])

    def _assert_hardware_source_conflict_raises(self, hardware_items):

        from cost_intelligence.project_cost_calculator import (
            ProjectCostCalculator,
        )

        with patch(
            "cost_intelligence.project_cost_calculator.MaterialCostCalculator"
        ) as material_calculator, patch(
            "cost_intelligence.project_cost_calculator.SheetCostCalculator"
        ) as sheet_calculator, patch(
            "cost_intelligence.project_cost_calculator.WasteCostCalculator"
        ) as waste_calculator, patch(
            "cost_intelligence.project_cost_calculator.HardwareCostCalculator"
        ) as hardware_calculator, patch(
            "cost_intelligence.project_cost_calculator.HardwareReportCostService"
        ) as hardware_report_cost_service:
            with self.assertRaisesRegex(
                ValueError,
                "^scene_graph and hardware_items are mutually exclusive$",
            ):
                ProjectCostCalculator().estimate(
                    hardware_items=hardware_items,
                    scene_graph=object(),
                )

        material_calculator.assert_not_called()
        sheet_calculator.assert_not_called()
        waste_calculator.assert_not_called()
        hardware_calculator.assert_not_called()
        hardware_report_cost_service.estimate.assert_not_called()


if __name__ == "__main__":
    unittest.main()
