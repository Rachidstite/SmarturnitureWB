import inspect
import unittest

from manufacturing.unified_operation_collector import (
    UnifiedOperationCollector,
)


class TestNoLegacyInCanonicalRuntime(
    unittest.TestCase
):

    def test_collect_canonical_does_not_use_legacy(self):

        source = inspect.getsource(
            UnifiedOperationCollector.collect_canonical
        )

        self.assertNotIn(
            "collect_legacy",
            source
        )

        self.assertNotIn(
            "collect_hybrid",
            source
        )

        self.assertIn(
            "collect_modern",
            source
        )


if __name__ == "__main__":
    unittest.main()
