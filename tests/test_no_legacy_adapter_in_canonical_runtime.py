import inspect
import unittest

from manufacturing.unified_operation_collector import (
    UnifiedOperationCollector,
)


class TestNoLegacyAdapterInCanonicalRuntime(
    unittest.TestCase
):

    def test_collect_canonical_does_not_reference_legacy_adapter(self):

        source = inspect.getsource(
            UnifiedOperationCollector.collect_canonical
        )

        self.assertNotIn(
            "LegacyOperationAdapter",
            source
        )

        self.assertNotIn(
            "collect_legacy",
            source
        )

        self.assertIn(
            "collect_modern",
            source
        )


if __name__ == "__main__":
    unittest.main()
