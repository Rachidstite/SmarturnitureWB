import unittest
from dataclasses import fields, is_dataclass
from pathlib import Path
from types import SimpleNamespace


class TestCabinetManufacturingKnowledgeReportContract(unittest.TestCase):

    def test_report_contract(self):
        from manufacturing.cabinet_manufacturing_knowledge_report import (
            CabinetManufacturingKnowledgeReport,
        )

        self.assertTrue(is_dataclass(CabinetManufacturingKnowledgeReport))
        self.assertEqual(
            [field.name for field in fields(CabinetManufacturingKnowledgeReport)],
            [
                "cabinet_structural_report",
                "cabinet_stability_report",
            ],
        )

        report = CabinetManufacturingKnowledgeReport()

        self.assertIsNone(report.cabinet_structural_report)
        self.assertIsNone(report.cabinet_stability_report)

    def test_accepts_structural_and_stability_reports(self):
        from manufacturing.cabinet_manufacturing_knowledge_report import (
            CabinetManufacturingKnowledgeReport,
        )

        cabinet_structural = SimpleNamespace(structural_risk="HIGH")
        cabinet_stability = SimpleNamespace(large_span_risk="MEDIUM")

        report = CabinetManufacturingKnowledgeReport(
            cabinet_structural_report=cabinet_structural,
            cabinet_stability_report=cabinet_stability,
        )

        self.assertIs(report.cabinet_structural_report, cabinet_structural)
        self.assertIs(report.cabinet_stability_report, cabinet_stability)

    def test_does_not_mutate_embedded_objects(self):
        from manufacturing.cabinet_manufacturing_knowledge_report import (
            CabinetManufacturingKnowledgeReport,
        )

        cabinet_structural = SimpleNamespace(
            structural_risk="MEDIUM",
            tags=["a", "b"],
        )
        cabinet_stability = SimpleNamespace(
            large_span_risk="LOW",
            tags=["x", "y"],
        )
        structural_snapshot = self._snapshot(cabinet_structural)
        stability_snapshot = self._snapshot(cabinet_stability)

        CabinetManufacturingKnowledgeReport(
            cabinet_structural_report=cabinet_structural,
            cabinet_stability_report=cabinet_stability,
        )

        self.assertEqual(self._snapshot(cabinet_structural), structural_snapshot)
        self.assertEqual(self._snapshot(cabinet_stability), stability_snapshot)

    def test_forbidden_duplicate_scalar_fields_are_not_present(self):
        from manufacturing.cabinet_manufacturing_knowledge_report import (
            CabinetManufacturingKnowledgeReport,
        )

        field_names = {field.name for field in fields(CabinetManufacturingKnowledgeReport)}

        for forbidden in {
            "cabinet_ready_for_production",
            "recommendation",
            "manufacturing_risk",
            "requires_center_support",
            "requires_reinforcement",
            "readiness_status",
            "recommended_action",
        }:
            self.assertNotIn(forbidden, field_names)

    def test_source_does_not_import_forbidden_modules(self):
        source = Path("manufacturing/cabinet_manufacturing_knowledge_report.py").read_text()

        forbidden_snippets = [
            "runtime",
            "CNC",
            "FreeCAD",
            "cost",
        ]

        for snippet in forbidden_snippets:
            self.assertNotIn(snippet, source)

    def test_no_builder_logic(self):
        from manufacturing.cabinet_manufacturing_knowledge_report import (
            CabinetManufacturingKnowledgeReport,
        )

        self.assertFalse(hasattr(CabinetManufacturingKnowledgeReport, "build"))

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in report.__dict__.items()
        }


if __name__ == "__main__":
    unittest.main()
