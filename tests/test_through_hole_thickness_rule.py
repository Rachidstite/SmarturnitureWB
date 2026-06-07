import unittest
from types import SimpleNamespace

from validation.intelligence.through_hole_thickness_rule import (
    ThroughHoleThicknessRule,
)

from manufacturing.unified_manufacturing_operation import (
    UnifiedManufacturingOperation,
)


class TestThroughHoleThicknessRule(
    unittest.TestCase
):

    def test_valid_through_hole(self):

        panel = SimpleNamespace(
            thickness=18
        )

        op = UnifiedManufacturingOperation(
            operation_type="DRILL",
            depth=18,
            is_through=True,
        )

        result = (
            ThroughHoleThicknessRule()
            .validate(panel, op)
        )

        self.assertTrue(result.passed)

    def test_invalid_through_hole(self):

        panel = SimpleNamespace(
            thickness=18
        )

        op = UnifiedManufacturingOperation(
            operation_type="DRILL",
            depth=10,
            is_through=True,
        )

        result = (
            ThroughHoleThicknessRule()
            .validate(panel, op)
        )

        self.assertFalse(result.passed)

        self.assertEqual(
            result.code,
            "THROUGH_HOLE_DEPTH"
        )


if __name__ == "__main__":
    unittest.main()
