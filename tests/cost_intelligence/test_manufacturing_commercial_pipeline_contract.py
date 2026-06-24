import unittest
from dataclasses import is_dataclass


class TestManufacturingCommercialPipelineContract(unittest.TestCase):

    def test_end_to_end_manufacturing_commercial_pipeline_contract(self):
        from cost_intelligence.manufacturing_commercial_pipeline_builder import (
            ManufacturingCommercialPipelineBuilder,
        )
        from cost_intelligence.manufacturing_commercial_result import (
            ManufacturingCommercialResult,
        )

        production_package = self._manufacturing_production_package()
        original_package_snapshot = self._snapshot(production_package)
        original_cutlist_snapshot = self._snapshot(
            production_package.cutlist_report
        )
        original_edge_snapshot = self._snapshot(
            production_package.edge_report
        )
        original_machining_snapshot = self._snapshot(
            production_package.machining_report
        )
        original_summary_snapshot = self._snapshot(
            production_package.summary_report
        )

        result = ManufacturingCommercialPipelineBuilder().build(
            production_package,
            markup_rate=0.25,
            currency="MAD",
        )

        self.assertIsInstance(result, ManufacturingCommercialResult)
        self.assertTrue(is_dataclass(ManufacturingCommercialResult))
        self.assertIsNotNone(result.manufacturing_cost_summary)
        self.assertIsNotNone(result.manufacturing_quotation_input)
        self.assertIsNotNone(result.quotation_report)
        self.assertIsNotNone(result.profitability_report)
        self.assertIsNotNone(result.quotation_intelligence_report)

        self.assertEqual(
            result.quotation_report.production_cost,
            result.manufacturing_cost_summary.total_manufacturing_cost,
        )
        self.assertEqual(result.quotation_report.markup_rate, 0.25)
        self.assertGreater(
            result.quotation_report.selling_price,
            result.quotation_report.production_cost,
        )
        self.assertEqual(result.quotation_report.currency, "MAD")

        self.assertEqual(
            result.profitability_report.production_cost,
            result.quotation_report.production_cost,
        )
        self.assertEqual(
            result.profitability_report.selling_price,
            result.quotation_report.selling_price,
        )
        self.assertGreater(result.profitability_report.gross_profit, 0)
        self.assertGreater(result.profitability_report.gross_margin_rate, 0)

        warnings = production_package.warnings
        self.assertEqual(result.manufacturing_cost_summary.warnings, warnings)
        self.assertIs(
            result.manufacturing_cost_summary.warnings,
            warnings,
        )
        self.assertEqual(result.manufacturing_quotation_input.warnings, warnings)
        self.assertIs(result.manufacturing_quotation_input.warnings, warnings)
        self.assertEqual(result.quotation_report.warnings, warnings)
        self.assertIs(result.quotation_report.warnings, warnings)
        self.assertEqual(result.profitability_report.warnings, warnings)

        self.assertEqual(
            self._snapshot(production_package),
            original_package_snapshot,
        )
        self.assertEqual(
            self._snapshot(production_package.cutlist_report),
            original_cutlist_snapshot,
        )
        self.assertEqual(
            self._snapshot(production_package.edge_report),
            original_edge_snapshot,
        )
        self.assertEqual(
            self._snapshot(production_package.machining_report),
            original_machining_snapshot,
        )
        self.assertEqual(
            self._snapshot(production_package.summary_report),
            original_summary_snapshot,
        )

        self.assertFalse(hasattr(ManufacturingCommercialResult, "build"))
        self.assertFalse(hasattr(ManufacturingCommercialResult, "calculate"))
        self.assertFalse(hasattr(ManufacturingCommercialResult, "compute"))
        self.assertFalse(hasattr(ManufacturingCommercialResult, "manufacture"))

    @staticmethod
    def _manufacturing_production_package():
        from manufacturing.manufacturing_cutlist_report import (
            ManufacturingCutlistReport,
        )
        from manufacturing.manufacturing_edge_report import (
            ManufacturingEdgeReport,
        )
        from manufacturing.manufacturing_machining_report import (
            ManufacturingMachiningReport,
        )
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )
        from manufacturing.manufacturing_summary_report import (
            ManufacturingSummaryReport,
        )

        warnings = ["Commercial pipeline warning"]

        return ManufacturingProductionPackage(
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

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in report.__dict__.items()
        }


if __name__ == "__main__":
    unittest.main()
