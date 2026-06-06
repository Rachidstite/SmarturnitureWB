import inspect
import unittest

from manufacturing.unified_operation_collector import (
    UnifiedOperationCollector,
)


class TestLegacyRuntimeIsDead(
    unittest.TestCase
):

    def test_collect_canonical_uses_modern_only(self):

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

    def test_legacy_methods_exist_but_are_unused(self):

        source = inspect.getsource(
            UnifiedOperationCollector
        )

        self.assertIn(
            "def collect_legacy",
            source
        )

        self.assertIn(
            "def collect_hybrid",
            source
        )


if __name__ == "__main__":
    unittest.main()
