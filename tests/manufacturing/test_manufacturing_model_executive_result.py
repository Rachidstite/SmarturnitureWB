import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingModelExecutiveResult(unittest.TestCase):

    def test_dataclass_exists(self):
        from manufacturing.manufacturing_model_executive_result import (
            ManufacturingModelExecutiveResult,
        )

        self.assertTrue(is_dataclass(ManufacturingModelExecutiveResult))

    def test_exact_field_order(self):
        from manufacturing.manufacturing_model_executive_result import (
            ManufacturingModelExecutiveResult,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingModelExecutiveResult)],
            [
                "manufacturing_model_report",
                "manufacturing_executive_report",
            ],
        )

    def test_defaults_are_none(self):
        from manufacturing.manufacturing_model_executive_result import (
            ManufacturingModelExecutiveResult,
        )

        result = ManufacturingModelExecutiveResult()

        self.assertIsNone(result.manufacturing_model_report)
        self.assertIsNone(result.manufacturing_executive_report)

    def test_accepts_model_report_object(self):
        from manufacturing.manufacturing_model_executive_result import (
            ManufacturingModelExecutiveResult,
        )

        model_report = object()

        result = ManufacturingModelExecutiveResult(
            manufacturing_model_report=model_report
        )

        self.assertIs(result.manufacturing_model_report, model_report)

    def test_accepts_executive_report_object(self):
        from manufacturing.manufacturing_model_executive_result import (
            ManufacturingModelExecutiveResult,
        )

        executive_report = object()

        result = ManufacturingModelExecutiveResult(
            manufacturing_executive_report=executive_report
        )

        self.assertIs(result.manufacturing_executive_report, executive_report)

    def test_does_not_mutate_embedded_objects(self):
        from manufacturing.manufacturing_model_executive_result import (
            ManufacturingModelExecutiveResult,
        )

        model_report = {"status": "READY"}
        executive_report = {"summary": "OK"}

        result = ManufacturingModelExecutiveResult(
            manufacturing_model_report=model_report,
            manufacturing_executive_report=executive_report,
        )

        self.assertIs(result.manufacturing_model_report, model_report)
        self.assertIs(result.manufacturing_executive_report, executive_report)
        self.assertEqual(model_report, {"status": "READY"})
        self.assertEqual(executive_report, {"summary": "OK"})


if __name__ == "__main__":
    unittest.main()
