import inspect
import unittest

from manufacturing.canonical_operation_collector import (
    CanonicalOperationCollector,
)


class TestLegacyRuntimeIsDead(
    unittest.TestCase
):

    def test_canonical_collector_is_independent(self):

        source = inspect.getsource(
            CanonicalOperationCollector
        )

        self.assertNotIn(
            "LegacyOperationAdapter",
            source
        )

        self.assertNotIn(
            "collect_legacy",
            source
        )

        self.assertNotIn(
            "PanelOperationEngine",
            source
        )


if __name__ == "__main__":
    unittest.main()
