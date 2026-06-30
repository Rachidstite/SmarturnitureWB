import unittest
from dataclasses import replace

from domain.base_cabinet_engineering_entry import (
    attach_base_cabinet_engineering_models,
)
from domain.base_cabinet_engineering_model import EngineeringDoorPlacement
from domain.base_cabinet_specification_adapter import (
    BaseCabinetSpecificationAdapter,
)
from engine.cabinet import Cabinet
from shared.contracts import CabinetParams
from shared.enums import DoorType


class TestStructuralConsistencyReport(unittest.TestCase):
    def _base_model(self):
        cabinet = Cabinet(CabinetParams())
        spec = BaseCabinetSpecificationAdapter.from_cabinet_params(cabinet.params)
        attach_base_cabinet_engineering_models(cabinet, spec)
        return cabinet.engineering_model

    def _door(self, name):
        return EngineeringDoorPlacement(
            name=name,
            section_index=0,
            section_id="SEC-1",
            door_index=0,
            source_rule="resolved_door_projection",
            x_mm=18.0,
            y_mm=12.0,
            z_mm=100.0,
            width_mm=380.0,
            height_mm=600.0,
            thickness_mm=18.0,
            door_type=DoorType.INSET,
            hinge_side="LEFT",
            layer=0,
            material="MDF_18",
        )

    def test_report_contains_facts_decision_violations_and_source(self):
        from project_engineering.structural_consistency_rule import (
            StructuralConsistencyRule,
        )

        model = replace(
            self._base_model(),
            doors=(self._door("SEC-1_Door_1"),),
        )

        report = StructuralConsistencyRule.evaluate(model, source="report-test")

        self.assertTrue(report.facts)
        self.assertIsNotNone(report.decision)
        self.assertIsInstance(report.violations, tuple)
        self.assertEqual(report.source, "report-test")
        self.assertEqual(report.decision.source, "report-test")

    def test_report_module_has_expected_shape(self):
        from project_engineering.structural_consistency_report import (
            StructuralConsistencyReport,
        )

        report = StructuralConsistencyReport()

        self.assertEqual(report.source, "")
        self.assertEqual(report.decision.status, "PASS")
        self.assertEqual(len(report.facts), 0)
        self.assertEqual(len(report.violations), 0)


if __name__ == "__main__":
    unittest.main()
