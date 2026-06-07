import unittest
from types import SimpleNamespace

from validation.intelligence.unused_operation_cost_impact import (
    UnusedOperationCostImpact,
)

from manufacturing.unified_manufacturing_operation import (
    UnifiedManufacturingOperation,
)


class TestUnusedOperationCostImpact(
    unittest.TestCase
):

    def test_generates_cost_saving(self):

        rule = (
            UnusedOperationCostImpact()
        )

        panel = SimpleNamespace(
            unified_operations=[
                UnifiedManufacturingOperation(
                    operation_type="FACE_DRILL",
                    x=100,
                    y=100,
                    z=0,
                    diameter=5,
                    depth=10,
                    face="FRONT",
                    axis="Z",
                    is_through=False,
                    metadata={}
                )
            ]
        )

        impacts = rule.estimate(
            [panel]
        )

        self.assertEqual(
            len(impacts),
            1
        )


if __name__ == "__main__":
    unittest.main()
