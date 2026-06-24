import unittest
from unittest.mock import MagicMock, patch


class TestManufacturingModelExecutiveBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.manufacturing_model_executive_builder import (
            ManufacturingModelExecutiveBuilder,
        )

        self.builder = ManufacturingModelExecutiveBuilder()

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_returns_manufacturing_model_executive_result(self):
        from manufacturing.manufacturing_model_executive_result import (
            ManufacturingModelExecutiveResult,
        )

        with patch(
            "manufacturing.manufacturing_model_executive_builder."
            "ManufacturingModelBuilder"
        ) as model_builder_class, patch(
            "manufacturing.manufacturing_model_executive_builder."
            "ManufacturingExecutiveBuilder"
        ) as executive_builder_class:
            model_report = object()
            executive_report = object()
            model_builder_class.return_value.build.return_value = model_report
            executive_builder_class.return_value.build.return_value = executive_report

            result = self.builder.build()

        self.assertIsInstance(result, ManufacturingModelExecutiveResult)
        self.assertIs(result.manufacturing_model_report, model_report)
        self.assertIs(result.manufacturing_executive_report, executive_report)

    def test_calls_manufacturing_model_builder(self):
        with patch(
            "manufacturing.manufacturing_model_executive_builder."
            "ManufacturingModelBuilder"
        ) as model_builder_class, patch(
            "manufacturing.manufacturing_model_executive_builder."
            "ManufacturingExecutiveBuilder"
        ) as executive_builder_class:
            model_report = object()
            executive_builder_class.return_value.build.return_value = object()
            model_builder_class.return_value.build.return_value = model_report

            self.builder.build(manufacturing_model_inputs={"project_name": "Kitchen"})

        model_builder_class.return_value.build.assert_called_once_with(
            project_name="Kitchen"
        )

    def test_passes_inventory_counts_to_manufacturing_model_builder(self):
        inventory_counts = object()

        with patch(
            "manufacturing.manufacturing_model_executive_builder."
            "ManufacturingModelBuilder"
        ) as model_builder_class, patch(
            "manufacturing.manufacturing_model_executive_builder."
            "ManufacturingExecutiveBuilder"
        ) as executive_builder_class:
            model_builder_class.return_value.build.return_value = object()
            executive_builder_class.return_value.build.return_value = object()

            self.builder.build(inventory_counts=inventory_counts)

        model_builder_class.return_value.build.assert_called_once_with(
            inventory_counts=inventory_counts
        )

    def test_calls_manufacturing_executive_builder_with_model_report(self):
        model_report = object()

        with patch(
            "manufacturing.manufacturing_model_executive_builder."
            "ManufacturingModelBuilder"
        ) as model_builder_class, patch(
            "manufacturing.manufacturing_model_executive_builder."
            "ManufacturingExecutiveBuilder"
        ) as executive_builder_class:
            model_builder_class.return_value.build.return_value = model_report
            executive_builder_class.return_value.build.return_value = object()

            self.builder.build(
                executive_inputs={
                    "factory_decision_report": object(),
                    "factory_executive_intelligence_report": object(),
                    "factory_delivery_report": object(),
                    "production_forecast_report": object(),
                }
            )

        executive_builder_class.return_value.build.assert_called_once_with(
            model_report,
            factory_decision_report=unittest.mock.ANY,
            factory_executive_intelligence_report=unittest.mock.ANY,
            factory_delivery_report=unittest.mock.ANY,
            production_forecast_report=unittest.mock.ANY,
        )

    def test_preserves_embedded_report_identity(self):
        model_report = MagicMock()
        executive_report = MagicMock()

        with patch(
            "manufacturing.manufacturing_model_executive_builder."
            "ManufacturingModelBuilder"
        ) as model_builder_class, patch(
            "manufacturing.manufacturing_model_executive_builder."
            "ManufacturingExecutiveBuilder"
        ) as executive_builder_class:
            model_builder_class.return_value.build.return_value = model_report
            executive_builder_class.return_value.build.return_value = executive_report

            result = self.builder.build()

        self.assertIs(result.manufacturing_model_report, model_report)
        self.assertIs(result.manufacturing_executive_report, executive_report)

    def test_does_not_mutate_manufacturing_model_inputs(self):
        model_inputs = {"project_name": "Kitchen"}
        snapshot = model_inputs.copy()

        with patch(
            "manufacturing.manufacturing_model_executive_builder."
            "ManufacturingModelBuilder"
        ) as model_builder_class, patch(
            "manufacturing.manufacturing_model_executive_builder."
            "ManufacturingExecutiveBuilder"
        ) as executive_builder_class:
            model_builder_class.return_value.build.return_value = object()
            executive_builder_class.return_value.build.return_value = object()

            self.builder.build(manufacturing_model_inputs=model_inputs)

        self.assertEqual(model_inputs, snapshot)

    def test_does_not_mutate_executive_inputs(self):
        executive_inputs = {
            "factory_decision_report": object(),
            "factory_executive_intelligence_report": object(),
            "factory_delivery_report": object(),
            "production_forecast_report": object(),
        }
        snapshot = executive_inputs.copy()

        with patch(
            "manufacturing.manufacturing_model_executive_builder."
            "ManufacturingModelBuilder"
        ) as model_builder_class, patch(
            "manufacturing.manufacturing_model_executive_builder."
            "ManufacturingExecutiveBuilder"
        ) as executive_builder_class:
            model_builder_class.return_value.build.return_value = object()
            executive_builder_class.return_value.build.return_value = object()

            self.builder.build(executive_inputs=executive_inputs)

        self.assertEqual(executive_inputs, snapshot)

    def test_works_with_none_inputs(self):
        with patch(
            "manufacturing.manufacturing_model_executive_builder."
            "ManufacturingModelBuilder"
        ) as model_builder_class, patch(
            "manufacturing.manufacturing_model_executive_builder."
            "ManufacturingExecutiveBuilder"
        ) as executive_builder_class:
            model_builder_class.return_value.build.return_value = object()
            executive_builder_class.return_value.build.return_value = object()

            result = self.builder.build()

        self.assertIsNotNone(result)
        model_builder_class.return_value.build.assert_called_once_with()
        executive_builder_class.return_value.build.assert_called_once()

    def test_does_not_scan_inventory_or_project_objects(self):
        inventory_counts = object()

        with patch(
            "manufacturing.manufacturing_model_executive_builder."
            "ManufacturingModelBuilder"
        ) as model_builder_class, patch(
            "manufacturing.manufacturing_model_executive_builder."
            "ManufacturingExecutiveBuilder"
        ) as executive_builder_class:
            model_builder_class.return_value.build.return_value = object()
            executive_builder_class.return_value.build.return_value = object()

            self.builder.build(
                manufacturing_model_inputs={"manufacturing_package": object()},
                executive_inputs={
                    "factory_decision_report": object(),
                    "factory_executive_intelligence_report": object(),
                    "factory_delivery_report": object(),
                    "production_forecast_report": object(),
                },
                inventory_counts=inventory_counts,
            )

        model_builder_class.return_value.build.assert_called_once()
        self.assertEqual(
            model_builder_class.return_value.build.call_args.kwargs["inventory_counts"],
            inventory_counts,
        )


if __name__ == "__main__":
    unittest.main()
