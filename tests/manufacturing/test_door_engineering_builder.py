import unittest
from dataclasses import fields, is_dataclass
from types import SimpleNamespace


class TestDoorEngineeringBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.door_engineering_builder import DoorEngineeringBuilder

        self.builder = DoorEngineeringBuilder()

    def test_report_contract(self):
        from manufacturing.door_engineering_report import DoorEngineeringReport

        self.assertTrue(is_dataclass(DoorEngineeringReport))
        self.assertEqual(
            [field.name for field in fields(DoorEngineeringReport)],
            [
                "door_height_risk",
                "door_width_risk",
                "hinge_requirement",
                "recommended_hinge_count",
                "door_recommendation",
            ],
        )

        report = DoorEngineeringReport()

        self.assertEqual(report.door_height_risk, "LOW")
        self.assertEqual(report.door_width_risk, "LOW")
        self.assertEqual(report.hinge_requirement, "")
        self.assertEqual(report.recommended_hinge_count, 2)
        self.assertEqual(report.door_recommendation, "")

    def test_medium_height_creates_medium_risk(self):
        report = self.builder.build(door_height=1200)

        self.assertEqual(report.door_height_risk, "MEDIUM")
        self.assertEqual(report.hinge_requirement, "MEDIUM")
        self.assertEqual(report.recommended_hinge_count, 3)
        self.assertEqual(report.door_recommendation, "Door engineering review recommended")

    def test_high_height_creates_high_risk(self):
        report = self.builder.build(door_height=1800)

        self.assertEqual(report.door_height_risk, "HIGH")
        self.assertEqual(report.hinge_requirement, "HIGH")
        self.assertEqual(report.recommended_hinge_count, 4)
        self.assertEqual(report.door_recommendation, "Door engineering review required")

    def test_medium_width_creates_medium_risk(self):
        report = self.builder.build(door_width=500)

        self.assertEqual(report.door_width_risk, "MEDIUM")

    def test_high_width_creates_high_risk(self):
        report = self.builder.build(door_width=600)

        self.assertEqual(report.door_width_risk, "HIGH")

    def test_low_door_keeps_default_hinge_count(self):
        report = self.builder.build()

        self.assertEqual(report.hinge_requirement, "LOW")
        self.assertEqual(report.recommended_hinge_count, 2)
        self.assertEqual(report.door_recommendation, "")

    def test_high_risk_recommendation(self):
        report = self.builder.build(door_height=1800, door_width=600)

        self.assertEqual(report.door_recommendation, "Door engineering review required")

    def test_medium_risk_recommendation(self):
        report = self.builder.build(door_height=1200, door_width=400)

        self.assertEqual(report.door_recommendation, "Door engineering review recommended")

    def test_builder_does_not_mutate_inputs(self):
        door = SimpleNamespace(height=1200, width=500, tags=["a", "b"])
        snapshot = self._snapshot(door)

        self.builder.build(door_height=door.height, door_width=door.width)

        self.assertEqual(self._snapshot(door), snapshot)

    @staticmethod
    def _snapshot(item):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in item.__dict__.items()
        }


if __name__ == "__main__":
    unittest.main()
