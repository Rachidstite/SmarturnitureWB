import unittest
from types import SimpleNamespace

from validation.intelligence.drill_inside_panel_rule import (
    DrillInsidePanelRule,
)

from manufacturing.unified_manufacturing_operation import (
    UnifiedManufacturingOperation,
)


class TestDrillInsidePanelRule(
    unittest.TestCase
):

    def test_valid_operation(self):

        panel = SimpleNamespace(
            width=600,
            height=800
        )

        op = UnifiedManufacturingOperation(
            operation_type="DRILL",
            x=100,
            y=100,
        )

        result = (
            DrillInsidePanelRule()
            .validate(panel, op)
        )

        self.assertTrue(result.passed)

    def test_invalid_x(self):

        panel = SimpleNamespace(
            width=600,
            height=800
        )

        op = UnifiedManufacturingOperation(
            operation_type="DRILL",
            x=700,
            y=100,
        )

        result = (
            DrillInsidePanelRule()
            .validate(panel, op)
        )

        self.assertFalse(result.passed)


if __name__ == "__main__":
    unittest.main()
