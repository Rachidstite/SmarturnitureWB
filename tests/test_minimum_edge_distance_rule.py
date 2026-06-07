import unittest
from types import SimpleNamespace

from validation.intelligence.minimum_edge_distance_rule import (
    MinimumEdgeDistanceRule,
)

from manufacturing.unified_manufacturing_operation import (
    UnifiedManufacturingOperation,
)


class TestMinimumEdgeDistanceRule(
    unittest.TestCase
):

    def test_valid_distance(self):

        panel = SimpleNamespace(
            width=600,
            height=800
        )

        op = UnifiedManufacturingOperation(
            operation_type="DRILL",
            x=50,
            y=50,
        )

        result = (
            MinimumEdgeDistanceRule()
            .validate(panel, op)
        )

        self.assertTrue(result.passed)

    def test_too_close_to_left_edge(self):

        panel = SimpleNamespace(
            width=600,
            height=800
        )

        op = UnifiedManufacturingOperation(
            operation_type="DRILL",
            x=2,
            y=100,
        )

        result = (
            MinimumEdgeDistanceRule()
            .validate(panel, op)
        )

        self.assertFalse(result.passed)

        self.assertEqual(
            result.code,
            "MIN_EDGE_DISTANCE"
        )


if __name__ == "__main__":
    unittest.main()
