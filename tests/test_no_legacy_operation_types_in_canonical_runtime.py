import inspect
import unittest

from manufacturing.canonical_operation_collector import (
    CanonicalOperationCollector,
)


class TestNoLegacyOperationTypesInCanonicalRuntime(
    unittest.TestCase
):

    def test_collector_has_no_legacy_operation_types(self):

        source = inspect.getsource(
            CanonicalOperationCollector
        )

        self.assertNotIn(
            "FaceDrill",
            source
        )

        self.assertNotIn(
            "EdgeDrill",
            source
        )

        self.assertNotIn(
            "Groove",
            source
        )


if __name__ == "__main__":
    unittest.main()
