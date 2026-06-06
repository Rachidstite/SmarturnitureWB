import inspect
import unittest

from manufacturing.canonical_operation_collector import (
    CanonicalOperationCollector,
)


class TestCanonicalArchitectureGuard(
    unittest.TestCase
):

    def test_collector_has_no_legacy_dependencies(self):

        source = inspect.getsource(
            CanonicalOperationCollector
        )

        self.assertNotIn(
            "LegacyOperationAdapter",
            source
        )

        self.assertNotIn(
            "PanelOperationEngine",
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
