import unittest
from types import SimpleNamespace


class TestEngineeringDemonstrationReport(unittest.TestCase):

    def test_builds_report_from_existing_manufacturing_data(self):
        from manufacturing.engineering_demonstration_report import (
            build_engineering_demonstration_report,
        )

        nodes = [
            SimpleNamespace(
                identity=SimpleNamespace(key="SIDE_L"),
                role=SimpleNamespace(value="SIDE_PANEL"),
                width=18.0,
                depth=600.0,
                height=2400.0,
                thickness=18.0,
                transform=SimpleNamespace(x=0.0, y=0.0, z=0.0),
                machining_ops=[SimpleNamespace(op_type="DRILL", face="LEFT")],
            ),
            SimpleNamespace(
                identity=SimpleNamespace(key="BACK_1"),
                role=SimpleNamespace(value="BACK_PANEL"),
                width=1200.0,
                depth=3.0,
                height=2382.0,
                thickness=3.0,
                transform=SimpleNamespace(x=18.0, y=15.0, z=9.0),
                machining_ops=[
                    SimpleNamespace(op_type="GROOVE", face="BACK"),
                    SimpleNamespace(op_type="DRILL", face="BACK"),
                ],
            ),
            SimpleNamespace(
                identity=SimpleNamespace(key="SHELF_1"),
                role=SimpleNamespace(value="SHELF"),
                width=564.0,
                depth=580.0,
                height=18.0,
                thickness=18.0,
                transform=SimpleNamespace(x=18.0, y=0.0, z=720.0),
                machining_ops=[],
            ),
        ]

        project = SimpleNamespace(
            uid="DEMO",
            graph=SimpleNamespace(
                all_nodes=lambda: nodes,
                get_node=lambda _node_id: None,
            ),
            placements=[
                SimpleNamespace(hardware_intent="INTENT_HINGE"),
                SimpleNamespace(hardware_intent="INTENT_CONFIRMAT_50"),
            ],
        )

        report = build_engineering_demonstration_report(
            project,
            validation_state=SimpleNamespace(
                issues=[
                    SimpleNamespace(level="WARNING", message="Check shelf row"),
                ]
            ),
            cost_summary=SimpleNamespace(total_manufacturing_cost=123.45),
        )

        self.assertEqual(report.panel_count, 3)
        self.assertEqual(report.hardware_count, 2)
        self.assertEqual(report.drilling_count, 3)
        self.assertEqual(report.validation_status, "READY_WITH_WARNINGS")
        self.assertEqual(report.estimated_manufacturing_cost, 123.45)
        self.assertIn("Wall mount geometry shown as a labeled engineering prototype", report.prototype_detail_lines)

        lines = report.to_lines()
        self.assertIn("Visible Engineering Demonstration", lines[0])
        self.assertIn("Estimated manufacturing cost: 123.45", " ".join(lines))


if __name__ == "__main__":
    unittest.main()
