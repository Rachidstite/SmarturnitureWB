import inspect
import unittest

from manufacturing.unified_operation_collector import (
    UnifiedOperationCollector,
)


class TestCanonicalArchitectureGuard(
    unittest.TestCase
):

    def test_collect_canonical_uses_only_modern_path(self):

        source = inspect.getsource(
            UnifiedOperationCollector.collect_canonical
        )

        self.assertIn(
            "collect_modern",
            source
        )

        self.assertNotIn(
            "collect_legacy",
            source
        )

        self.assertNotIn(
            "collect_hybrid",
            source
        )


if __name__ == "__main__":
    unittest.main()
