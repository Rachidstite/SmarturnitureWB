import unittest

from validation.unified_operation_validation_adapter import (
    UnifiedOperationValidationAdapter
)

from manufacturing.unified_manufacturing_operation import (
    UnifiedManufacturingOperation
)


class FakeSpec:

    def __init__(self, operations):

        self.unified_operations = operations


class TestUnifiedOperationValidationAdapter(
    unittest.TestCase
):

    def test_detects_hybrid_issues(self):

        spec = FakeSpec([
            UnifiedManufacturingOperation(
                operation_type="",
                source=""
            )
        ])

        issues = (
            UnifiedOperationValidationAdapter()
            .validate([spec])
        )

        codes = {
            i.code
            for i in issues
        }

        self.assertIn(
            "OPERATION_TYPE_MISSING",
            codes
        )

        self.assertIn(
            "OPERATION_SOURCE_MISSING",
            codes
        )


if __name__ == "__main__":
    unittest.main()
