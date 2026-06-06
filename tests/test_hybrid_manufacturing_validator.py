import unittest

from validation.hybrid_manufacturing_validator import (
    HybridManufacturingValidator
)

from manufacturing.unified_manufacturing_operation import (
    UnifiedManufacturingOperation
)


class TestHybridManufacturingValidator(unittest.TestCase):

    def test_valid_operation(self):

        op = UnifiedManufacturingOperation(
            operation_type="DRILL",
            source="modern-core"
        )

        issues = (
            HybridManufacturingValidator()
            .validate([op])
        )

        self.assertEqual(len(issues), 0)

    def test_empty_operation_type(self):

        op = UnifiedManufacturingOperation(
            operation_type="",
            source="modern-core"
        )

        issues = (
            HybridManufacturingValidator()
            .validate([op])
        )

        self.assertTrue(
            any(
                i.code == "OPERATION_TYPE_MISSING"
                for i in issues
            )
        )

    def test_empty_source(self):

        op = UnifiedManufacturingOperation(
            operation_type="DRILL",
            source=""
        )

        issues = (
            HybridManufacturingValidator()
            .validate([op])
        )

        self.assertTrue(
            any(
                i.code == "OPERATION_SOURCE_MISSING"
                for i in issues
            )
        )

    def test_negative_values(self):

        op = UnifiedManufacturingOperation(
            operation_type="DRILL",
            source="modern-core",
            diameter=-1,
            depth=-1,
            x=-1,
            y=-1,
            z=-1
        )

        issues = (
            HybridManufacturingValidator()
            .validate([op])
        )

        self.assertEqual(len(issues), 5)




if __name__ == "__main__":
    unittest.main()
