import inspect
import unittest

from manufacturing.canonical_operation_collector import (
    CanonicalOperationCollector,
)


class TestNoLegacyInCanonicalRuntime(
    unittest.TestCase
):

    def test_collector_does_not_use_legacy_runtime(self):

        source = inspect.getsource(
            CanonicalOperationCollector
        )

        self.assertNotIn(
            "collect_legacy",
            source
        )

        self.assertNotIn(
            "LegacyOperationAdapter",
            source
        )


if __name__ == "__main__":
    unittest.main()
